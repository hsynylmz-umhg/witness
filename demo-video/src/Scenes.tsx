import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, Sequence, staticFile } from "remotion";
import { Artefact } from "./Artefact";
import { BEATS, BOLTS_S, CAVEAT, at, framesOf, startOf } from "./beats";
import { Mark, MarkGeometry } from "./Mark";
import { drawOn, reveal, rule, step, typeOn } from "./motion";
import { Subtitles } from "./Subtitles";
import { color, font, frames, glyph, layout, leading, opacity, size, space, still, stroke, weight } from "./theme";

export type FilmData = {
  parts: string[];
  events: { part: string; order: number; evidence: string }[];
  findings: { kind: string; part: string; message: string }[];
  hashes: { record: string; report: string; manifest: string; input: string };
  mark: { mono: MarkGeometry; full: MarkGeometry };
};

type Scene = React.FC<{ f: number; data: FilmData }>;

const text = (n: number) => BEATS[n - 1].text;
const when = (n: number, key: string) => at(n, BEATS[n - 1].at[key]);
const end = (n: number) => startOf(n) + framesOf(BEATS[n - 1].seconds);

type Type = {
  x: number;
  y: number;
  w?: number;
  family?: string;
  fontSize?: number;
  colour?: string;
  align?: "left" | "center" | "right";
  lineHeight?: number;
  pre?: boolean;
};

const Text: React.FC<Type & { children: React.ReactNode }> = ({
  x,
  y,
  w,
  family = font.body,
  fontSize = size.sm,
  colour = color.ink,
  align = "left",
  lineHeight = leading.body,
  pre = false,
  children,
}) => (
  <div
    style={{
      position: "absolute",
      left: x,
      top: y,
      width: w,
      fontFamily: family,
      fontSize,
      lineHeight,
      color: colour,
      textAlign: align,
      fontWeight: weight.regular,
      whiteSpace: pre ? "pre" : w === undefined ? "nowrap" : "normal",
    }}
  >
    {children}
  </div>
);

// Words without figures type on; anything that states a figure lands whole in one frame.
const Typed: React.FC<Type & { f: number; from: number; value: string }> = ({ f, from, value, ...type }) => {
  const shown = typeOn(f, from, value);
  return (
    <Text {...type}>
      <span>{value.slice(0, shown)}</span>
      <span style={{ opacity: 0 }}>{value.slice(shown)}</span>
    </Text>
  );
};

const Stated: React.FC<Type & { f: number; from: number; children: React.ReactNode }> = ({ f, from, children, ...type }) =>
  step(f, from, 0) ? <Text {...type}>{children}</Text> : null;

const Layer: React.FC<{ clip: string; children: React.ReactNode }> = ({ clip, children }) => (
  <AbsoluteFill style={{ clipPath: clip }}>{children}</AbsoluteFill>
);

const HRule: React.FC<{ ends: [number, number]; y: number; colour?: string }> = ({ ends, y, colour = color.accent }) => (
  <div
    style={{
      position: "absolute",
      left: ends[0],
      top: y - stroke.rule / 2,
      width: Math.max(0, ends[1] - ends[0]),
      height: stroke.rule,
      background: colour,
    }}
  />
);

const VRule: React.FC<{ ends: [number, number]; x: number; colour?: string }> = ({ ends, x, colour = color.accent }) => (
  <div
    style={{
      position: "absolute",
      left: x - stroke.rule / 2,
      top: ends[0],
      width: stroke.rule,
      height: Math.max(0, ends[1] - ends[0]),
      background: colour,
    }}
  />
);

const Glyph: React.FC<{ pass: boolean }> = ({ pass }) => (
  <span style={{ color: pass ? color.verified : color.rejected }}>{pass ? glyph.pass : glyph.fail}</span>
);

// Beat 1: the small mono mark and the question, set alone; the bolt B-roll uncovered in place.
const Opening: Scene = ({ f, data }) => {
  const L = layout.b1;
  const t = text(1);
  const bolts = when(1, "bolts");
  const boltsEnd = bolts + framesOf(BOLTS_S);
  if (f >= startOf(2) + frames.reveal) return null;
  return (
    <>
      <Layer clip={reveal(f, 0, { until: startOf(2) })}>
        <Mark
          f={f}
          at={when(1, "mark")}
          duration={frames.markSmall}
          x={(layout.w - L.markSize) / 2}
          y={L.markY}
          size={L.markSize}
          geometry={data.mark.mono}
          full={false}
        />
        <Typed
          f={f}
          from={when(1, "line")}
          value={t.line}
          x={layout.left}
          y={L.lineY}
          w={layout.right - layout.left}
          family={font.display}
          fontSize={size.lg}
          lineHeight={leading.tight}
          align="center"
        />
      </Layer>
      {f >= bolts && f < boltsEnd ? (
        <Artefact
          f={f}
          at={bolts}
          until={boltsEnd - frames.reveal}
          x={L.frame.x}
          y={L.frame.y}
          w={L.frame.w}
          h={L.frame.h}
          caption={t.caption}
          note={t.note}
        >
          <Sequence from={bolts} durationInFrames={framesOf(BOLTS_S)} layout="none">
            <OffthreadVideo
              muted
              src={staticFile("witness/bolts_beat1.mp4")}
              style={{ width: "100%", height: "100%", objectFit: "cover", filter: still.filter }}
            />
          </Sequence>
        </Artefact>
      ) : null}
    </>
  );
};

// Matched 1 to 2: the rule under the question becomes the header rule of the event log.
const OpeningRule: Scene = ({ f }) => {
  const from = when(1, "rule");
  if (f < from || f >= startOf(3) + frames.reveal) return null;
  const ends = rule(f, from, layout.b1.rule, { to: [layout.left, layout.right], toAt: startOf(2) });
  return (
    <Layer clip={reveal(f, 0, { until: startOf(3) })}>
      <HRule ends={ends} y={layout.b1.ruleY} />
    </Layer>
  );
};

// Beat 2: the skipped clip's event log as ten procedure parts filling in the order they were seen.
const EventLog: Scene = ({ f, data }) => {
  const L = layout.b2;
  const t = text(2);
  const start = startOf(2);
  if (f < start || f >= startOf(3) + frames.reveal) return null;
  const pitch = (layout.right - L.stripLeft) / data.parts.length;
  const seen = data.events.slice().sort((a, b) => a.order - b.order);
  const spacing = (when(2, "eventsEnd") - when(2, "events")) / seen.length;
  const ids = when(2, "ids");
  const missing = data.findings.filter((x) => x.kind === "skipped").map((x) => x.part);
  const cell = stroke.cell;
  const first = seen[0];
  const checks: [string, string][] = [
    ["coverage", "skipped"],
    ["ordering", "order_discrepancy"],
    ["undocumented", "undocumented"],
  ];
  const rows: [string, number][] = [
    [t.rowPart, L.idsY],
    [t.rowOrder, L.cellY + (cell - size.sm * leading.body) / 2],
    [t.rowStill, L.evidenceY],
  ];
  return (
    <Layer clip={reveal(f, start, { until: startOf(3) })}>
      {rows.map(([label, y]) => (
        <Typed key={label} f={f} from={ids} value={label} x={layout.left} y={y} fontSize={size.xs} colour={color.inkMuted} />
      ))}
      {data.parts.map((part, i) => {
        const x = L.stripLeft + pitch * (i + 0.5);
        const event = data.events.filter((e) => e.part === part)[0];
        const landed = event ? when(2, "events") + Math.round(seen.indexOf(event) * spacing) : Infinity;
        const absent = missing.indexOf(part) >= 0;
        const perimeter = 4 * cell;
        return (
          <React.Fragment key={part}>
            <Stated f={f} from={ids} x={x - pitch / 2} w={pitch} y={L.idsY} family={font.mono} fontSize={size.xs} colour={color.inkMuted} align="center">
              {part}
            </Stated>
            {step(f, ids, 0) ? (
              <div
                style={{
                  position: "absolute",
                  left: x - cell / 2,
                  top: L.cellY,
                  width: cell,
                  height: cell,
                  boxSizing: "border-box",
                  borderStyle: "solid",
                  borderWidth: stroke.rule,
                  borderColor: color.rampHigh,
                }}
              />
            ) : null}
            {f >= landed ? (
              <div
                style={{
                  position: "absolute",
                  left: x - cell / 2,
                  top: L.cellY,
                  width: cell,
                  height: cell,
                  background: color.verified,
                  opacity: opacity.stateFill,
                }}
              />
            ) : null}
            <Stated
              f={f}
              from={landed}
              x={x - cell / 2}
              w={cell}
              y={L.cellY + (cell - size.md * leading.tight) / 2}
              family={font.display}
              fontSize={size.md}
              lineHeight={leading.tight}
              align="center"
            >
              {event ? String(event.order) : ""}
            </Stated>
            <Stated f={f} from={landed} x={x - pitch / 2} w={pitch} y={L.evidenceY} family={font.mono} fontSize={size.xs} colour={color.inkMuted} align="center">
              {event ? event.evidence : ""}
            </Stated>
            {absent && f >= when(2, "gap") ? (
              <>
                <svg width={layout.w} height={layout.h} style={{ position: "absolute", left: 0, top: 0 }}>
                  <rect
                    x={x - cell / 2}
                    y={L.cellY}
                    width={cell}
                    height={cell}
                    fill="none"
                    stroke={color.rejected}
                    strokeWidth={stroke.outline}
                    {...drawOn(f, when(2, "gap"), perimeter, frames.outline)}
                  />
                </svg>
                <Typed f={f} from={when(2, "gap")} value={t.gap} x={x - pitch / 2} w={pitch} y={L.evidenceY} fontSize={size.xs} colour={color.rejected} align="center" />
              </>
            ) : null}
          </React.Fragment>
        );
      })}
      {f >= when(2, "still") ? (
        <Artefact
          f={f}
          at={when(2, "still")}
          x={L.still.x}
          y={L.still.y}
          w={L.still.w}
          h={L.still.h}
          caption={`${first.evidence}.png${glyph.sep}${first.part}`}
        >
          <Img src={staticFile("witness/evidence-1.png")} style={{ width: "100%", height: "100%", objectFit: "cover", filter: still.filter }} />
        </Artefact>
      ) : null}
      {checks.map(([name, kind], k) => {
        const y = L.checksY + k * L.rowStep;
        const pass = data.findings.filter((x) => x.kind === kind).length === 0;
        return (
          <React.Fragment key={name}>
            <Stated f={f} from={when(2, name)} x={L.checksX} y={y}>
              <Glyph pass={pass} />
            </Stated>
            <Typed f={f} from={when(2, name)} value={t[name]} x={L.checksX + space.s3} y={y} />
          </React.Fragment>
        );
      })}
      {data.findings.map((finding, j) => {
        const y = L.findingsY + j * L.findingStep;
        return (
          <React.Fragment key={`${finding.kind}-${finding.part}`}>
            <Stated f={f} from={when(2, "finding")} x={L.checksX} y={y}>
              <Glyph pass={false} />
              {` ${finding.kind}${glyph.sep}${finding.part}`}
            </Stated>
            {finding.kind === "skipped" ? (
              <Typed
                f={f}
                from={when(2, "finding")}
                value={finding.message}
                x={L.checksX + space.s3}
                y={y + L.messageGap}
                w={layout.right - L.checksX - space.s3}
                fontSize={size.xs}
                colour={color.inkMuted}
              />
            ) : null}
          </React.Fragment>
        );
      })}
    </Layer>
  );
};

// Beat 3: the hash chain from the current manifest, its recompute rule and its limit.
const Chain: Scene = ({ f, data }) => {
  const L = layout.b3;
  const t = text(3);
  const start = startOf(3);
  if (f < start || f >= startOf(4) + frames.reveal) return null;
  const nodes = [
    { x: L.points[0], from: when(3, "record"), label: t.record, value: data.hashes.record },
    { x: L.points[1], from: when(3, "report"), label: t.report, value: data.hashes.report },
    { x: L.points[2], from: when(3, "manifest"), label: t.manifest, value: data.hashes.manifest },
  ];
  const half = L.valueW / 2;
  const width = layout.right - layout.left;
  return (
    <Layer clip={reveal(f, start, { until: startOf(4) })}>
      <svg width={layout.w} height={layout.h} style={{ position: "absolute", left: 0, top: 0 }}>
        {nodes.map((node) =>
          f < node.from ? null : (
            <circle
              key={node.x}
              cx={node.x}
              cy={L.chainY}
              r={stroke.point}
              fill={color.ground}
              stroke={color.accent}
              strokeWidth={stroke.rule}
              {...drawOn(f, node.from, 2 * Math.PI * stroke.point, frames.reveal)}
            />
          ),
        )}
      </svg>
      {nodes.map((node) => (
        <React.Fragment key={node.x}>
          <Stated f={f} from={node.from} x={node.x - half} w={L.valueW} y={L.labelY} align="center">
            {node.label}
          </Stated>
          <Stated f={f} from={node.from} x={node.x - half} w={L.valueW} y={L.valueY} family={font.mono} fontSize={size.xs} align="center" pre>
            {`${node.value.slice(0, node.value.length / 2)}\n${node.value.slice(node.value.length / 2)}`}
          </Stated>
        </React.Fragment>
      ))}
      <Stated f={f} from={when(3, "recompute")} x={layout.left} w={width} y={L.formulaY} family={font.mono} fontSize={size.xs} colour={color.inkMuted} align="center">
        {`${t.recompute}${data.hashes.input}`}
      </Stated>
      <Typed f={f} from={when(3, "limit")} value={t.limit} x={layout.left} w={width} y={L.limitY} align="center" />
      <Typed f={f} from={when(3, "anchor")} value={t.anchor} x={layout.left} w={width} y={L.anchorY} colour={color.inkMuted} align="center" />
    </Layer>
  );
};

// Matched 3 to 4: the chain's line becomes the baseline the four figures stand on.
const ChainLine: Scene = ({ f }) => {
  const [p0, p1, p2] = layout.b3.points;
  const y = layout.b3.chainY;
  const four = startOf(4);
  if (f < when(3, "report") || f >= startOf(5) + frames.reveal) return null;
  if (f < four) {
    return (
      <>
        <HRule ends={rule(f, when(3, "report"), [p0, p1])} y={y} />
        {f >= when(3, "manifest") ? <HRule ends={rule(f, when(3, "manifest"), [p1, p2])} y={y} /> : null}
      </>
    );
  }
  return (
    <Layer clip={reveal(f, 0, { until: startOf(5) })}>
      <HRule ends={rule(f, four, [p0, p2], { duration: 0, to: [layout.left, layout.right], toAt: four })} y={layout.b4.baseY} />
    </Layer>
  );
};

// Beat 4: the risk gate's four figures, landing in spoken order with the caveat; then stillness.
const Gate: Scene = ({ f }) => {
  const L = layout.b4;
  const t = text(4);
  const start = startOf(4);
  if (f < start || f >= startOf(5) + frames.reveal) return null;
  const items = [
    { from: when(4, "cases"), value: t.cases, label: t.casesLabel, tone: color.inkMuted },
    { from: when(4, "tp"), value: t.tp, label: t.tpLabel, tone: color.verified },
    { from: when(4, "fp"), value: t.fp, label: t.fpLabel, tone: color.rejected },
    { from: when(4, "fn"), value: t.fn, label: t.fnLabel, tone: color.rejected },
  ];
  const half = L.columnW / 2;
  return (
    <Layer clip={reveal(f, start, { until: startOf(5) })}>
      {items.map((item, i) =>
        step(f, item.from, 0) ? (
          <React.Fragment key={item.label}>
            <Text x={L.columns[i] - half} w={L.columnW} y={L.figureY} family={font.display} fontSize={size.xl} lineHeight={leading.tight} align="center">
              {item.value}
            </Text>
            <div
              style={{
                position: "absolute",
                left: L.columns[i] - stroke.threshold / 2,
                top: L.baseY,
                width: stroke.threshold,
                height: L.tick,
                background: item.tone,
              }}
            />
            <Text x={L.columns[i] - half} w={L.columnW} y={L.labelY} colour={color.inkMuted} align="center">
              {item.label}
            </Text>
          </React.Fragment>
        ) : null,
      )}
      <Stated f={f} from={when(4, "fn")} x={layout.left} w={layout.right - layout.left} y={L.caveatY} fontSize={size.md} align="center">
        {t.caveat}
      </Stated>
    </Layer>
  );
};

// Beat 5: the geometry-only run in stated figures; no picture and no model output.
const Geometry: Scene = ({ f }) => {
  const L = layout.b5;
  const t = text(5);
  const start = startOf(5);
  if (f < start || f >= startOf(6) + frames.reveal) return null;
  const d = L.divider;
  return (
    <Layer clip={reveal(f, start)}>
      <VRule ends={rule(f, when(5, "divider"), [d.top, d.bottom])} x={d.x} colour={color.rampHigh} />
      <Typed f={f} from={when(5, "scope")} value={t.scope} x={layout.left} y={L.scopeY} fontSize={size.md} />
      <Typed f={f} from={when(5, "scene")} value={t.scene} x={layout.left} y={L.sceneY} colour={color.inkMuted} />
      <Typed f={f} from={when(5, "clean")} value={t.clean} x={L.clean} y={L.colY} colour={color.inkMuted} />
      <Stated f={f} from={when(5, "found")} x={L.clean} y={L.foundY} family={font.display} fontSize={size.xl} lineHeight={leading.tight}>
        {t.found}
      </Stated>
      <Typed f={f} from={when(5, "found")} value={t.foundLabel} x={L.clean} y={L.foundLabelY} />
      <Stated f={f} from={when(5, "missed")} x={L.clean} y={L.missedY} fontSize={size.md}>
        <Glyph pass={false} /> {t.missed}
      </Stated>
      <Stated f={f} from={when(5, "ratio")} x={L.clean} y={L.ratioY} fontSize={size.md}>
        {t.ratio}
      </Stated>
      <Typed f={f} from={when(5, "skipped")} value={t.skipped} x={L.skipped} y={L.colY} colour={color.inkMuted} />
      <Stated f={f} from={when(5, "swap")} x={L.skipped} y={L.swapY} fontSize={size.md}>
        <Glyph pass /> {t.swap}
      </Stated>
      <Stated f={f} from={when(5, "blank")} x={L.skipped} y={L.blankY} fontSize={size.md}>
        <Glyph pass={false} /> {t.blank}
      </Stated>
      <Stated f={f} from={when(5, "slid")} x={L.skipped + space.s2} w={L.colW - 2 * space.s2} y={L.slidY} fontSize={size.md}>
        {t.slid}
      </Stated>
    </Layer>
  );
};

// Matched 5 to 6: the outline around the cause opens, as a mask edge, into the frame of beat 6.
const Outline: Scene = ({ f }) => {
  const o = layout.b5.outline;
  const p = layout.b6.panel;
  const from = when(5, "outline");
  const six = startOf(6);
  if (f < from || f >= startOf(7) + frames.reveal) return null;
  const k = step(f, six, frames.reveal);
  const [x1, y1, x2, y2] = o.map((v, i) => v + (p[i] - v) * k);
  const perimeter = 2 * (o[2] - o[0] + o[3] - o[1]);
  return (
    <Layer clip={reveal(f, 0, { until: startOf(7) })}>
      <svg width={layout.w} height={layout.h} style={{ position: "absolute", left: 0, top: 0 }}>
        <rect
          x={x1}
          y={y1}
          width={x2 - x1}
          height={y2 - y1}
          fill="none"
          stroke={color.accent}
          strokeWidth={stroke.rule}
          {...(f < six ? drawOn(f, from, perimeter, frames.outline) : {})}
        />
      </svg>
    </Layer>
  );
};

// Beat 6: the threshold drawn at 2.0, two bars that stop short of it, the frames where extraction stopped.
const Refusal: Scene = ({ f }) => {
  const L = layout.b6;
  const t = text(6);
  const six = startOf(6);
  const seven = startOf(7);
  if (f < six || f >= seven + frames.reveal) return null;
  const [x1, y1, x2, y2] = L.panel;
  const w = x2 - x1;
  const h = y2 - y1;
  const o = layout.b5.outline;
  const opening: [number, number, number, number] = [
    ((o[1] - y1) / h) * 100,
    ((x2 - o[2]) / w) * 100,
    ((y2 - o[3]) / h) * 100,
    ((o[0] - x1) / w) * 100,
  ];
  const required = parseFloat(t.required);
  const lineX = L.barX + L.barL - x1;
  const rows = [
    { y: L.rows[0] - y1, label: t.clean, value: t.cleanValue, from: when(6, "clean"), stop: t.cleanStop },
    { y: L.rows[1] - y1, label: t.skipped, value: t.skippedValue, from: when(6, "skipped"), stop: t.skippedStop },
  ];
  const bars = when(6, "bars");
  return (
    <div
      style={{
        position: "absolute",
        left: x1,
        top: y1,
        width: w,
        height: h,
        background: color.ground,
        clipPath: reveal(f, six, { from: opening, until: seven }),
      }}
    >
      <Typed f={f} from={when(6, "title")} value={t.title} x={L.titleX - x1} y={L.titleY - y1} fontSize={size.md} />
      <svg width={w} height={h} style={{ position: "absolute", left: 0, top: 0 }}>
        {f >= bars
          ? rows.map((row) => {
              const length = (L.barL * parseFloat(row.value)) / required;
              return (
                <line
                  key={row.label}
                  x1={L.barX - x1}
                  y1={row.y}
                  x2={L.barX - x1 + length}
                  y2={row.y}
                  stroke={color.ink}
                  strokeWidth={stroke.bar}
                  {...drawOn(f, bars, length, frames.bars)}
                />
              );
            })
          : null}
        {f >= when(6, "threshold") ? (
          <line
            x1={lineX}
            y1={L.lineTop - y1}
            x2={lineX}
            y2={L.lineBottom - y1}
            stroke={color.accent}
            strokeWidth={stroke.threshold}
            {...drawOn(f, when(6, "threshold"), L.lineBottom - L.lineTop, frames.threshold)}
          />
        ) : null}
      </svg>
      {rows.map((row) => (
        <React.Fragment key={row.label}>
          <Typed f={f} from={bars} value={row.label} x={L.labelX - x1} y={row.y - (size.sm * leading.body) / 2} colour={color.inkMuted} />
          <Stated f={f} from={row.from} x={L.valueX - x1} y={row.y - (size.lg * leading.tight) / 2} family={font.display} fontSize={size.lg} lineHeight={leading.tight}>
            {row.value}
          </Stated>
          <Stated f={f} from={when(6, "stopped")} x={L.valueX - x1} y={row.y + L.stopGap} family={font.mono} fontSize={size.xs} colour={color.inkMuted}>
            <Glyph pass={false} /> {row.stop}
          </Stated>
        </React.Fragment>
      ))}
      <Stated f={f} from={bars} x={L.barX - x1} y={L.zeroY - y1} family={font.mono} fontSize={size.xs} colour={color.inkMuted}>
        {t.zero}
      </Stated>
      <Stated f={f} from={when(6, "required")} x={lineX - L.requiredW / 2} w={L.requiredW} y={L.requiredY - y1} align="center">
        {t.required}
      </Stated>
    </div>
  );
};

// Beat 7: the model overlays of both clips at one crop, clean then skipped, and the measured run.
const Model: Scene = ({ f }) => {
  const L = layout.b7;
  const t = text(7);
  const seven = startOf(7);
  const eight = startOf(8);
  if (f < seven || f >= eight + frames.reveal) return null;
  const c = L.crop;
  const scale = (L.frame.w - 2 * space.s2) / c.w;
  const frameH = Math.round(c.h * scale) + 2 * space.s2;
  const image: React.CSSProperties = {
    position: "absolute",
    left: -c.x * scale,
    top: -c.y * scale,
    width: c.srcW * scale,
    height: c.srcH * scale,
    filter: still.filter,
  };
  const swap = when(7, "skipped");
  return (
    <Layer clip={reveal(f, seven, { until: eight })}>
      <Artefact f={f} at={seven} x={L.frame.x} y={L.frame.y} w={L.frame.w} h={frameH} caption={f >= swap ? t.skipped : t.clean}>
        <Img src={staticFile("witness/model_clean_anchor48.png")} style={image} />
        <AbsoluteFill style={{ clipPath: reveal(f, swap) }}>
          <Img src={staticFile("witness/model_skipped_anchor28.png")} style={image} />
        </AbsoluteFill>
      </Artefact>
      <Typed f={f} from={when(7, "meta")} value={t.meta} x={L.colX} y={L.modelY} colour={color.inkMuted} />
      <Stated f={f} from={when(7, "model")} x={L.colX} y={L.nameY} family={font.mono} fontSize={size.lg} lineHeight={leading.tight}>
        {t.model}
      </Stated>
      <Stated f={f} from={when(7, "anchors")} x={L.colX} y={L.anchorsY} family={font.display} fontSize={size.lg} lineHeight={leading.tight}>
        {t.anchors}
      </Stated>
      <Stated f={f} from={when(7, "anchors")} x={L.colX} w={L.colW} y={L.anchorsLabelY} colour={color.inkMuted}>
        {t.anchorsLabel}
      </Stated>
      <Stated f={f} from={when(7, "cost")} x={L.colX} y={L.costY} family={font.display} fontSize={size.lg} lineHeight={leading.tight}>
        {t.cost}
      </Stated>
      <Stated f={f} from={when(7, "agree")} x={L.colX} y={L.agreeY}>
        <Glyph pass />
      </Stated>
      <Typed f={f} from={when(7, "agree")} value={t.agree} x={L.colX + space.s3} w={L.colW - space.s3} y={L.agreeY} />
    </Layer>
  );
};

// Beat 8: the claim, one slow drawn rule, and the full mark drawn on in the quiet at the end.
const Close: Scene = ({ f, data }) => {
  const L = layout.b8;
  const t = text(8);
  const eight = startOf(8);
  if (f < eight) return null;
  const from = when(8, "rule");
  return (
    <Layer clip={reveal(f, eight)}>
      <Typed
        f={f}
        from={when(8, "claim")}
        value={t.claim}
        x={(layout.w - L.claimW) / 2}
        w={L.claimW}
        y={L.claimY}
        family={font.display}
        fontSize={size.lg}
        lineHeight={leading.tight}
        align="center"
      />
      <HRule ends={rule(f, from, L.rule, { duration: when(8, "ruleEnd") - from })} y={L.ruleY} />
      <Mark
        f={f}
        at={when(8, "mark")}
        duration={frames.markLarge}
        x={(layout.w - L.markSize) / 2}
        y={L.markY}
        size={L.markSize}
        geometry={data.mark.full}
        full
      />
    </Layer>
  );
};

// Q6: from the moment beat 7's agreement lands, the calibration limit sits in the lower-left column
// above the subtitle band, types on once and does not move again.
const Caveat: Scene = ({ f }) => {
  const from = when(7, "agree");
  if (f < from) return null;
  const shown = typeOn(f, from, CAVEAT);
  return (
    <div
      style={{
        position: "absolute",
        left: layout.caveat.x,
        width: layout.caveat.w,
        bottom: layout.h - layout.caveat.bottom,
        fontFamily: font.body,
        fontSize: size.xs,
        lineHeight: leading.body,
        color: color.inkMuted,
      }}
    >
      <span>{CAVEAT.slice(0, shown)}</span>
      <span style={{ opacity: 0 }}>{CAVEAT.slice(shown)}</span>
    </div>
  );
};

// The source of the beat's figures, set small at the top right once the beat has opened.
const Source: Scene = ({ f }) => {
  const beat = BEATS.filter((b) => f >= startOf(b.number) && f < end(b.number))[0];
  if (!beat || !beat.text.source || !step(f, startOf(beat.number) + frames.reveal, 0)) return null;
  return (
    <Text x={layout.left} w={layout.right - layout.left} y={layout.sourceY} family={font.mono} fontSize={size.xs} colour={color.inkMuted} align="right">
      {beat.text.source}
    </Text>
  );
};

export const Film: Scene = (props) => (
  <>
    <ChainLine {...props} />
    <Opening {...props} />
    <OpeningRule {...props} />
    <EventLog {...props} />
    <Chain {...props} />
    <Gate {...props} />
    <Geometry {...props} />
    <Refusal {...props} />
    <Outline {...props} />
    <Model {...props} />
    <Close {...props} />
    <Source {...props} />
    <Caveat {...props} />
    <Subtitles f={props.f} />
  </>
);
