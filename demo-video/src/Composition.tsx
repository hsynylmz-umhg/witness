import { useEffect, useState } from "react";
import {
  AbsoluteFill,
  Audio,
  CalculateMetadataFunction,
  Composition,
  IFrame,
  Img,
  OffthreadVideo,
  Sequence,
  continueRender,
  delayRender,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// docs/DEMO_SCRIPT.md is the source of truth: beats, durations and spoken text are parsed from
// it at render time, so the on-screen words cannot drift from the script.
const FPS = 30;
// Beat 7 is widened to 23.60 s from beat 4's silence so no narration is cut (round 17).
const TOTAL_FRAMES = 5400;
const frames = (seconds: number) => Math.round(seconds * FPS);
const SCRIPT = staticFile("witness/DEMO_SCRIPT.md");

type Beat = { number: number; seconds: number; onScreen: string; spoken: string; sources: string };
type Props = { beats: Beat[] };

// sync-assets.mjs masks the repository and home paths; any user path left fails the render.
const LEAK = /[A-Za-z]:(\\\\|\\|\/)Users(\\\\|\\|\/)/;
const guard = (beat: number, text: string) => {
  if (LEAK.test(text)) throw new Error(`Beat ${beat} would show an absolute user path.`);
};
const voice = (beat: number) => `witness/voiceover/beat-${String(beat).padStart(2, "0")}.wav`;

const parseScript = (text: string): Beat[] =>
  text
    .split(/\r?\n/)
    .filter((line) => /^\| \d+ \|/.test(line))
    .map((line) => {
      const cells = line.split(" | ").map((cell) => cell.replace(/^\| ?| ?\|$/g, "").trim());
      return {
        number: Number(cells[0]),
        seconds: Number(cells[2]),
        onScreen: cells[3],
        spoken: cells[4],
        sources: cells[5],
      };
    });

const calculateMetadata: CalculateMetadataFunction<Props> = async () => {
  const beats = parseScript(await (await fetch(SCRIPT)).text());
  const total = beats.reduce((sum, beat) => sum + frames(beat.seconds), 0);
  if (beats.length !== 8 || total !== TOTAL_FRAMES) {
    throw new Error(`DEMO_SCRIPT.md parsed to ${beats.length} beats, ${total} frames; expected 8, ${TOTAL_FRAMES}.`);
  }
  // Played clip durations, measured by ffprobe in sync-assets.mjs on this render.
  const audio: Record<string, number> = await (await fetch(staticFile("witness/audio.json"))).json();
  for (const beat of beats) {
    guard(beat.number, `${beat.onScreen} ${beat.spoken} ${beat.sources}`);
    const clip = audio[beat.number];
    if (clip === undefined || clip > beat.seconds) {
      throw new Error(`Beat ${beat.number}: voiceover is ${clip} s, slot is ${beat.seconds} s.`);
    }
  }
  return { durationInFrames: total, props: { beats } };
};

export const MyComposition = () => (
  <Composition
    id="WitnessDemo"
    component={WitnessDemo}
    durationInFrames={TOTAL_FRAMES}
    fps={FPS}
    width={1920}
    height={1080}
    defaultProps={{ beats: [] }}
    calculateMetadata={calculateMetadata}
  />
);

// Fade in and out over half a second; a slow push of at most 4% on stills.
const useFade = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return interpolate(frame, [0, 15, durationInFrames - 15, durationInFrames], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

const Push: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const scale = interpolate(frame, [0, durationInFrames], [1, 1.04]);
  return <AbsoluteFill style={{ transform: `scale(${scale})` }}>{children}</AbsoluteFill>;
};

const Label: React.FC<{ text: string }> = ({ text }) => (
  <div style={{ position: "absolute", top: 8, left: 12, font: "20px monospace", color: "#94a3b8" }}>
    {text}
  </div>
);

const Still: React.FC<{ file: string; label: string }> = ({ file, label }) => (
  <AbsoluteFill style={{ background: "#0b1220" }}>
    <Push>
      <Img src={staticFile(`witness/${file}`)} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
    </Push>
    <Label text={label} />
  </AbsoluteFill>
);

const Page: React.FC<{ file: string; label: string }> = ({ file, label }) => (
  <AbsoluteFill style={{ background: "#ffffff" }}>
    <Push>
      <IFrame src={staticFile(`witness/${file}`)} style={{ width: "100%", height: "100%", border: 0 }} />
    </Push>
    <Label text={label} />
  </AbsoluteFill>
);

// Shows runs of lines of a text file, each starting at a marker line, exactly as stored.
const Excerpt: React.FC<{ beat: number; file: string; parts: [string, number][]; label: string }> = ({
  beat,
  file,
  parts,
  label,
}) => {
  const [text, setText] = useState<string | null>(null);
  const [handle] = useState(() => delayRender(`excerpt ${file}`));
  useEffect(() => {
    fetch(staticFile(`witness/${file}`))
      .then((response) => response.text())
      .then((body) => {
        const all = body.replace(/\r\n/g, "\n").split("\n");
        const runs = parts.map(([marker, lines]) => {
          const start = all.findIndex((line) => line.startsWith(marker));
          if (start < 0) throw new Error(`${file} has no line starting with ${marker}`);
          return all.slice(start, start + lines).join("\n");
        });
        const shown = runs.join("\n…\n");
        guard(beat, shown);
        setText(shown);
        continueRender(handle);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps -- parts is a fresh literal each render
  }, [beat, file, JSON.stringify(parts), handle]);
  return (
    <AbsoluteFill style={{ background: "#0b1220", padding: "56px 48px" }}>
      <pre style={{ margin: 0, color: "#e2e8f0", font: "21px/1.45 monospace", whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>
        {text}
      </pre>
      <Label text={label} />
    </AbsoluteFill>
  );
};

// Beat 1 opens with the silent bolt excerpt cut by sync-assets.mjs (8 s), then the panel still.
const BOLTS_FRAMES = 8 * FPS;

const Visual: React.FC<{ beat: Beat }> = ({ beat }) => {
  const half = Math.round(frames(beat.seconds) / 2);
  switch (beat.number) {
    case 1:
      return (
        <>
          <Sequence durationInFrames={BOLTS_FRAMES}>
            <AbsoluteFill style={{ background: "#0b1220" }}>
              <OffthreadVideo muted src={staticFile("witness/bolts_beat1.mp4")} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
              <Label text="data/raw/demo_bolts_v1_clean.mp4, 0-8 s — B-roll" />
              <div
                style={{
                  position: "absolute", left: 0, right: 0, top: 48, padding: "14px 0", textAlign: "center",
                  background: "rgba(11, 18, 32, 0.85)", color: "#fde68a", font: "bold 52px Arial, sans-serif",
                }}
              >
                intended use case — not a measurement
              </div>
            </AbsoluteFill>
          </Sequence>
          <Sequence from={BOLTS_FRAMES}>
            <Still file="clean_evidence-1.png" label="artifacts/real_clean_02/evidence/evidence-1.png — a frame of real_panel_v1_clean.mp4" />
          </Sequence>
        </>
      );
    case 2:
      return <Page file="clean_report.html" label="artifacts/real_clean_02/report.html" />;
    case 3:
      return <Excerpt beat={beat.number} file="clean_manifest.json" parts={[["{", 40]]} label="artifacts/real_clean_02/manifest.json" />;
    case 4:
      return <Excerpt beat={beat.number} file="RISK_GATE.md" parts={[["All 25 cases are SYNTHETIC", 5], ["All conditions: TP=", 3]]} label="docs/RISK_GATE.md" />;
    case 5:
      return (
        <>
          <Sequence durationInFrames={half}>
            <Still file="overlay.png" label="artifacts/overlays/real_clean_02_frame-7224.png" />
          </Sequence>
          <Sequence from={half}>
            <AbsoluteFill style={{ flexDirection: "row" }}>
              <div style={{ position: "relative", flex: 1 }}>
                <Page file="clean_report.html" label="real_clean_02/report.html" />
              </div>
              <div style={{ position: "relative", flex: 1 }}>
                <Page file="skipped_report.html" label="real_skipped_02/report.html" />
              </div>
              <div style={{ position: "relative", flex: 1 }}>
                <Excerpt beat={beat.number} file="REAL_MEDIA.md" parts={[["| Clip | Expected | Marks found | Box ids, in onset order", 4]]} label="docs/REAL_MEDIA.md — Round 7 vs key" />
              </div>
            </AbsoluteFill>
          </Sequence>
        </>
      );
    case 6:
      return <Excerpt beat={beat.number} file="REAL_MEDIA.md" parts={[["## Round 8 measurement", 20], ["| clean | 10 marks, no findings | none", 2]]} label="docs/REAL_MEDIA.md — Round 8" />;
    case 7:
      return (
        <Excerpt
          beat={beat.number}
          file="REAL_MEDIA.md"
          parts={[["## Model-produced events", 1], ["| Clip | Session | Anchors", 4], ["Reports: ", 4]]}
          label="docs/REAL_MEDIA.md — Model-produced events"
        />
      );
    default:
      return <Page file="clean_report.html" label="artifacts/real_clean_02/report.html" />;
  }
};

const BeatView: React.FC<{ beat: Beat }> = ({ beat }) => (
  <AbsoluteFill style={{ opacity: useFade(), background: "#0b1220" }}>
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 230, overflow: "hidden" }}>
      <Visual beat={beat} />
    </div>
    <div
      style={{
        position: "absolute", left: 0, right: 0, bottom: 0, height: 230, padding: "22px 48px",
        background: "#111827", color: "#f8fafc", font: "27px/1.4 Arial, sans-serif",
      }}
    >
      {beat.spoken}
      <div style={{ marginTop: 8, color: "#94a3b8", font: "18px monospace" }}>Sources: {beat.sources}</div>
    </div>
  </AbsoluteFill>
);

export const WitnessDemo: React.FC<Props> = ({ beats }) => {
  let from = 0;
  return (
    <AbsoluteFill style={{ background: "#0b1220" }}>
      {beats.map((beat) => {
        const start = from;
        from += frames(beat.seconds);
        return (
          <Sequence key={beat.number} from={start} durationInFrames={frames(beat.seconds)}>
            <BeatView beat={beat} />
            <Audio src={staticFile(voice(beat.number))} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
