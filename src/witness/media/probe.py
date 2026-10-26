"""Inspect local media without transcoding or changing source timestamps."""

import json
import math
import shutil
import subprocess
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from witness.errors import WitnessError


@dataclass(frozen=True)
class FrameTime:
    """Index in ffprobe's selected-stream decoded presentation order."""

    original_frame_index: int
    pts: int | None
    best_effort_timestamp: int | None
    media_time_s: float | None
    timestamp_source: str
    quality_flags: tuple[str, ...]


@dataclass(frozen=True)
class VideoInfo:
    stream_index: int
    codec_name: str
    width: int
    height: int
    time_base: str
    average_frame_rate: str | None
    nominal_frame_rate: str | None
    declared_duration_s: float | None
    timeline_origin_ticks: int
    timeline_span_s: float
    frames: tuple[FrameTime, ...]
    ffprobe_version: str

    def metadata(self) -> dict[str, Any]:
        result = asdict(self)
        del result["frames"]
        result["decoded_frame_count"] = len(self.frames)
        return result


def validate_local_video(path: Path, *, max_bytes: int) -> Path:
    """Require a nonempty supported local container; ffprobe validates its contents."""
    path = path.resolve()
    if not path.is_file():
        raise WitnessError("Input must be an existing local file.")
    if path.suffix.lower() not in {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi"}:
        raise WitnessError("Unsupported local video extension.")
    size = path.stat().st_size
    if size == 0:
        raise WitnessError("Input video is empty.")
    if size > max_bytes:
        raise WitnessError("Input exceeds the configured file size limit.")
    return path


def _integer(value: Any) -> int | None:
    if value is None or value == "N/A":
        return None
    if isinstance(value, bool):
        raise WitnessError("Invalid integer in ffprobe metadata.")
    try:
        return int(str(value))
    except (TypeError, ValueError) as error:
        raise WitnessError("Invalid integer in ffprobe metadata.") from error


def _rate(value: Any) -> Fraction | None:
    try:
        rate = Fraction(str(value))
        return rate if rate > 0 else None
    except (ValueError, ZeroDivisionError):
        return None


def parse_probe(payload: dict[str, Any], *, version: str = "unknown") -> VideoInfo:
    """Keep raw PTS and fallback timestamps separate; never infer time from FPS."""
    try:
        streams = payload["streams"]
        raw_frames = payload["frames"]
        if (
            not isinstance(streams, list)
            or not isinstance(raw_frames, list)
            or not all(isinstance(item, dict) for item in streams + raw_frames)
        ):
            raise WitnessError("Malformed stream or frame entries in ffprobe metadata.")
        if len(streams) != 1 or not raw_frames:
            raise WitnessError("Exactly one selected video stream with decoded frames is required.")
        stream = streams[0]
        width, height = int(stream["width"]), int(stream["height"])
        time_base = Fraction(stream["time_base"])
        if width <= 0 or height <= 0 or time_base <= 0:
            raise WitnessError("Invalid video dimensions or time base.")
        timestamps = [
            (_integer(frame.get("pts")), _integer(frame.get("best_effort_timestamp")))
            for frame in raw_frames
        ]
        ticks = [pts if pts is not None else best for pts, best in timestamps]
        origin = next((tick for tick in ticks if tick is not None), None)
        if origin is None:
            raise WitnessError("No usable presentation timestamps were found.")
        nominal = _rate(stream.get("r_frame_rate"))
        frames: list[FrameTime] = []
        previous: int | None = None
        for index, ((pts, best), tick) in enumerate(zip(timestamps, ticks, strict=True)):
            flags: list[str] = []
            source = "pts" if pts is not None else "best_effort" if best is not None else "missing"
            if source != "pts":
                flags.append("missing_original_pts")
            if tick is None:
                flags.append("missing_timestamp")
            else:
                if previous is not None:
                    if tick <= previous:
                        raise WitnessError("Video presentation timestamps must increase strictly.")
                    if nominal and (tick - previous) * time_base > Fraction(3, 2) / nominal:
                        flags.append("timestamp_gap_candidate")
                previous = tick
            frames.append(
                FrameTime(
                    original_frame_index=index,
                    pts=pts,
                    best_effort_timestamp=best,
                    media_time_s=float((tick - origin) * time_base) if tick is not None else None,
                    timestamp_source=source,
                    quality_flags=tuple(flags),
                )
            )
        duration_value = stream.get("duration", payload.get("format", {}).get("duration"))
        duration = None if duration_value in (None, "N/A") else float(duration_value)
        if duration is not None and (not math.isfinite(duration) or duration < 0):
            raise WitnessError("Invalid declared media duration.")
        return VideoInfo(
            stream_index=int(stream["index"]),
            codec_name=str(stream["codec_name"]),
            width=width,
            height=height,
            time_base=str(time_base),
            average_frame_rate=str(stream["avg_frame_rate"])
            if _rate(stream.get("avg_frame_rate"))
            else None,
            nominal_frame_rate=str(nominal) if nominal else None,
            declared_duration_s=duration,
            timeline_origin_ticks=origin,
            timeline_span_s=max(frame.media_time_s or 0 for frame in frames),
            frames=tuple(frames),
            ffprobe_version=version,
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        if isinstance(error, WitnessError):
            raise
        raise WitnessError("Malformed or incomplete ffprobe metadata.") from error


def probe_video(path: Path, *, timeout_s: float = 60) -> VideoInfo:
    executable = shutil.which("ffprobe")
    if executable is None:
        raise WitnessError("ffprobe is not available on PATH.")
    entries = (
        "stream=index,codec_name,width,height,time_base,avg_frame_rate,r_frame_rate,duration:"
        "frame=pts,best_effort_timestamp:format=duration"
    )
    command = [
        executable,
        "-v",
        "error",
        "-protocol_whitelist",
        "file,pipe",
        "-format_whitelist",
        "mov,matroska,webm,avi",
        "-select_streams",
        "v:0",
        "-show_entries",
        entries,
        "-show_frames",
        "-of",
        "json",
        str(path),
    ]
    try:
        result = subprocess.run(command, capture_output=True, timeout=timeout_s, check=False)
        if result.returncode:
            raise WitnessError("ffprobe could not decode the selected video stream.")
        version = (
            subprocess.run(
                [executable, "-version"],
                capture_output=True,
                timeout=10,
                check=True,
            )
            .stdout.decode("utf-8", errors="replace")
            .splitlines()[0]
        )
        payload = json.loads(result.stdout)
    except subprocess.TimeoutExpired as error:
        raise WitnessError("ffprobe exceeded the configured timeout.") from error
    except (OSError, subprocess.CalledProcessError, UnicodeError, json.JSONDecodeError) as error:
        raise WitnessError("ffprobe did not return usable metadata.") from error
    return parse_probe(payload, version=version)
