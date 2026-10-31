import React from "react";
import { AbsoluteFill, Audio, CalculateMetadataFunction, Composition, Sequence, staticFile, useCurrentFrame } from "remotion";
import { BEATS, BREATH_S, CAVEAT, FPS, TOTAL_FRAMES, startOf } from "./beats";
import { Arc, Joint, MarkGeometry, Rod } from "./Mark";
import { Film, FilmData } from "./Scenes";
import { color, layout } from "./theme";

// The beats are authored in beats.ts; the figures and hashes are read from the current run, copied
// into public/witness by sync-assets.mjs; the mark is read from its own SVG files in public/brand.
type Props = { data: FilmData | null };

// sync-assets.mjs masks the repository and home paths; any user path left in a drawn string fails the render.
const LEAK = /[A-Za-z]:(\\\\|\\|\/)Users(\\\\|\\|\/)/;

const sha256 = async (bytes: Uint8Array): Promise<string> =>
  Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)), (b) => (b < 16 ? "0" : "") + b.toString(16)).join("");

const voice = (n: number) => `witness/voiceover/beat-${n < 10 ? "0" : ""}${n}.wav`;

const read = async (path: string): Promise<string> => {
  const response = await fetch(staticFile(path));
  if (!response.ok) throw new Error(`${path} is missing; run sync-assets.mjs first.`);
  return response.text();
};

const parseMark = (svg: string): MarkGeometry => {
  const doc = new DOMParser().parseFromString(svg, "image/svg+xml");
  const num = (el: Element | null, name: string) => Number(el ? el.getAttribute(name) : NaN);
  const all = (selector: string) => Array.prototype.slice.call(doc.querySelectorAll(selector)) as Element[];
  const width = (el: Element) => num(el, "stroke-width") || num(el.parentElement, "stroke-width");
  const lines = (selector: string): Rod[] =>
    all(selector).map((el) => ({
      x1: num(el, "x1"),
      y1: num(el, "y1"),
      x2: num(el, "x2"),
      y2: num(el, "y2"),
      width: width(el),
      pen: num(el, "data-pen"),
    }));
  const joints: Joint[] = all("circle.joint").map((el) => ({ cx: num(el, "cx"), cy: num(el, "cy"), r: num(el, "r"), pen: num(el, "data-pen") }));
  const arcs: Arc[] = all("path.rim").map((el) => ({
    d: el.getAttribute("d") || "",
    r: Number((el.getAttribute("d") || "").split(/\s+/)[4]),
    width: width(el),
    pen: num(el, "data-pen"),
  }));
  const gradient = doc.querySelector("linearGradient");
  return {
    rods: lines("line.rod"),
    rims: lines("line.rim"),
    joints,
    arcs,
    gradient: [num(gradient, "x1"), num(gradient, "y1"), num(gradient, "x2"), num(gradient, "y2")],
    stops: all("stop").map((el) => (el.getAttribute("stop-color") || "").toUpperCase()),
  };
};

const calculateMetadata: CalculateMetadataFunction<Props> = async () => {
  const audio = JSON.parse(await read("witness/audio.json")) as Record<string, number>;
  const procedure = JSON.parse(await read("witness/procedure.json"));
  const log = JSON.parse(await read("witness/events.json"));
  const report = JSON.parse(await read("witness/findings.json"));
  const manifest = JSON.parse(await read("witness/manifest.json"));
  const manifestSum = (await read("witness/manifest.sha256")).trim().split(/\s+/)[0];
  const full = parseMark(await read("brand/witness-logo.svg"));
  const mono = parseMark(await read("brand/witness-logo-mono.svg"));
  const data: FilmData = {
    parts: procedure.steps.map((s: { part_id: string }) => s.part_id),
    events: log.events.map((e: { part_id: string; observed_order: number; evidence_id: string }) => ({
      part: e.part_id,
      order: e.observed_order,
      evidence: e.evidence_id,
    })),
    findings: report.findings.map((x: { kind: string; part_id: string; message: string }) => ({
      kind: x.kind,
      part: x.part_id,
      message: x.message,
    })),
    hashes: { record: manifest.record_hash, report: manifest.report_hash, manifest: manifestSum, input: manifest.report_hash_input },
    mark: { mono, full },
  };

  // Guard 1, paths: every string a beat draws, authored or read from the run.
  const drawn: Record<number, string[]> = {};
  for (const beat of BEATS) {
    drawn[beat.number] = beat.cues.map((cue) => cue.text).concat(Object.keys(beat.text).map((key) => beat.text[key]));
  }
  drawn[2] = drawn[2].concat(
    data.parts,
    data.events.map((e) => e.evidence),
    data.findings.map((x) => `${x.kind} ${x.part} ${x.message}`),
  );
  drawn[3] = drawn[3].concat([data.hashes.record, data.hashes.report, data.hashes.manifest, data.hashes.input]);
  drawn[7].push(CAVEAT);
  drawn[8].push(CAVEAT);
  for (const beat of BEATS) {
    if (drawn[beat.number].some((s) => LEAK.test(s))) {
      throw new Error(`Beat ${beat.number} would draw an absolute user path.`);
    }
  }
  // Guard 2, audio: each played clip, measured by ffprobe in sync-assets.mjs, fits its slot with the
  // 2.000 s breath (beats 4 and 6 hold far longer by design).
  for (const beat of BEATS) {
    const clip = audio[String(beat.number)];
    const slot = beat.frames / FPS;
    if (clip === undefined || clip + BREATH_S > slot) {
      throw new Error(`Beat ${beat.number}: voiceover is ${clip} s, slot is ${slot.toFixed(3)} s; it needs at least ${(clip + BREATH_S).toFixed(3)} s.`);
    }
  }
  // The subtitles are the narration, word for word.
  for (const beat of BEATS) {
    if (beat.cues.map((cue) => cue.text).join(" ") !== beat.spoken) {
      throw new Error(`Beat ${beat.number}: the subtitle cues are not the narration word for word.`);
    }
  }
  // The slots fill exactly 4914 frames.
  const total = BEATS.reduce((sum, beat) => sum + beat.frames, 0);
  if (BEATS.length !== 8 || total !== TOTAL_FRAMES) {
    throw new Error(`The beats fill ${total} frames in ${BEATS.length} beats; expected 8 beats and ${TOTAL_FRAMES} frames.`);
  }
  // The film's ramp is the mark's gradient, and the mono mark has the full mark's geometry.
  if (full.stops.join() !== [color.rampBase, color.rampCrown].join()) {
    throw new Error("The mark's gradient stops are not the theme's ramp ends.");
  }
  const shape = (m: MarkGeometry) => JSON.stringify([m.rods, m.joints]);
  if (shape(full) !== shape(mono)) throw new Error("The mono mark's geometry differs from the full mark's.");
  // The report shown in beat 3 belongs to the run whose hashes are drawn above it.
  const page = new Uint8Array(await (await fetch(staticFile("witness/report.html"))).arrayBuffer());
  const record = new TextEncoder().encode(data.hashes.record);
  const joined = new Uint8Array(record.length + page.length);
  joined.set(record, 0);
  joined.set(page, record.length);
  const listed = (manifest.artifacts as { path: string; sha256: string }[]).filter((a) => a.path === "report.html")[0];
  if ((await sha256(joined)) !== data.hashes.report || !listed || (await sha256(page)) !== listed.sha256) {
    throw new Error("Beat 3 would show a report.html that does not belong to the manifest drawn above it.");
  }

  return { durationInFrames: TOTAL_FRAMES, props: { data } };
};

export const MyComposition = () => (
  <Composition
    id="WitnessDemo"
    component={WitnessDemo}
    durationInFrames={TOTAL_FRAMES}
    fps={FPS}
    width={layout.w}
    height={layout.h}
    defaultProps={{ data: null }}
    calculateMetadata={calculateMetadata}
  />
);

export const WitnessDemo: React.FC<Props> = ({ data }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: color.ground }}>
      {data ? <Film f={f} data={data} /> : null}
      {BEATS.map((beat) => (
        <Sequence key={beat.number} from={startOf(beat.number)} durationInFrames={beat.frames} layout="none">
          <Audio src={staticFile(voice(beat.number))} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
