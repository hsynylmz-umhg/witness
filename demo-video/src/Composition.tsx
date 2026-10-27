import { useEffect, useState } from "react";
import {
  AbsoluteFill,
  CalculateMetadataFunction,
  Composition,
  IFrame,
  Img,
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
const SCRIPT = staticFile("witness/DEMO_SCRIPT.md");

type Beat = { number: number; seconds: number; onScreen: string; spoken: string; sources: string };
type Props = { beats: Beat[] };

const parseScript = (text: string): Beat[] =>
  text
    .split("\n")
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
  const total = beats.reduce((sum, beat) => sum + beat.seconds, 0);
  if (beats.length !== 8 || total !== 180) {
    throw new Error(`DEMO_SCRIPT.md parsed to ${beats.length} beats, ${total} s; expected 8, 180 s.`);
  }
  return { durationInFrames: total * FPS, props: { beats } };
};

export const MyComposition = () => (
  <Composition
    id="WitnessDemo"
    component={WitnessDemo}
    durationInFrames={180 * FPS}
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
const Excerpt: React.FC<{ file: string; parts: [string, number][]; label: string }> = ({
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
        setText(runs.join("\n…\n"));
        continueRender(handle);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps -- parts is a fresh literal each render
  }, [file, JSON.stringify(parts), handle]);
  return (
    <AbsoluteFill style={{ background: "#0b1220", padding: "56px 48px" }}>
      <pre style={{ margin: 0, color: "#e2e8f0", font: "21px/1.45 monospace", whiteSpace: "pre-wrap" }}>
        {text}
      </pre>
      <Label text={label} />
    </AbsoluteFill>
  );
};

const Visual: React.FC<{ beat: Beat }> = ({ beat }) => {
  const half = (beat.seconds * FPS) / 2;
  switch (beat.number) {
    case 1:
      return <Still file="clean_evidence-1.png" label="artifacts/real_clean_02/evidence/evidence-1.png — a frame of real_panel_v1_clean.mp4" />;
    case 2:
      return <Page file="clean_report.html" label="artifacts/real_clean_02/report.html" />;
    case 3:
      return <Excerpt file="clean_manifest.json" parts={[["{", 40]]} label="artifacts/real_clean_02/manifest.json" />;
    case 4:
      return <Excerpt file="RISK_GATE.md" parts={[["All 25 cases are SYNTHETIC", 5], ["All conditions: TP=", 3]]} label="docs/RISK_GATE.md" />;
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
                <Excerpt file="REAL_MEDIA.md" parts={[["| Clip | Expected | Marks found | Box ids, in onset order", 4]]} label="docs/REAL_MEDIA.md — Round 7 vs key" />
              </div>
            </AbsoluteFill>
          </Sequence>
        </>
      );
    case 6:
      return <Excerpt file="REAL_MEDIA.md" parts={[["## Round 8 measurement", 20], ["| clean | 10 marks, no findings | none", 2]]} label="docs/REAL_MEDIA.md — Round 8" />;
    case 7:
      return <Excerpt file="STATUS.md" parts={[["## Current", 26]]} label="docs/STATUS.md — Current" />;
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
        from += beat.seconds * FPS;
        return (
          <Sequence key={beat.number} from={start} durationInFrames={beat.seconds * FPS}>
            <BeatView beat={beat} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
