import React, { useState } from "react";
import {
  AbsoluteFill,
  Freeze,
  IFrame,
  Img,
  OffthreadVideo,
  Sequence,
  continueRender,
  delayRender,
  interpolateColors,
  staticFile,
} from "remotion";
import { Artefact } from "./Artefact";
import {
  BEATS,
  BOLTS_S,
  CAVEAT,
  LEAD,
  LINGER,
  at,
  endOf,
  framesOf,
  startOf,
} from "./beats";
import { Mark, MarkGeometry } from "./Mark";
import { drawOn, reveal, rule, step, typeOn } from "./motion";
import { Subtitles } from "./Subtitles";
import {
  color,
  font,
  frames,
  glyph,
  layout,
  leading,
  opacity,
  size,
  space,
  spine,
  still,
  stroke,
  weight,
} from "./theme";

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
// Continuity: beat n's first object arrives at lead(n); its last objects leave from linger(n).
const lead = (n: number) => startOf(n) - LEAD;
const linger = (n: number) => startOf(n + 1) + LINGER;

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
const Typed: React.FC<Type & { f: number; from: number; value: string }> = ({
  f,
  from,
  value,
  ...type
}) => {
  const shown = typeOn(f, from, value);
  return (
    <Text {...type}>
      <span>{value.slice(0, shown)}</span>
      <span style={{ opacity: 0 }}>{value.slice(shown)}</span>
    </Text>
  );
};

const Stated: React.FC<
  Type & { f: number; from: number; children: React.ReactNode }
> = ({ f, from, children, ...type }) =>
  step(f, from, 0) ? <Text {...type}>{children}</Text> : null;

const Layer: React.FC<{ clip: string; children: React.ReactNode }> = ({
  clip,
  children,
}) => <AbsoluteFill style={{ clipPath: clip }}>{children}</AbsoluteFill>;

const HRule: React.FC<{
  ends: [number, number];
  y: number;
  colour?: string;
  thickness?: number;
}> = ({ ends, y, colour = color.accent, thickness = stroke.rule }) => (
  <div
    style={{
      position: "absolute",
      left: ends[0],
      top: y - thickness / 2,
      width: Math.max(0, ends[1] - ends[0]),
      height: thickness,
      background: colour,
    }}
  />
);

const VRule: React.FC<{
  ends: [number, number];
  x: number;
  colour?: string;
}> = ({ ends, x, colour = color.accent }) => (
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
  <span style={{ color: pass ? color.verified : color.rejected }}>
    {pass ? glyph.pass : glyph.fail}
  </span>
);

// The spine: drawn once in beat 1 at one y and never moved; at each boundary its weight and colour
// step to the role of the incoming beat.
const Spine: Scene = ({ f }) => {
  const from = when(1, "rule");
  if (f < from) return null;
  const ends = rule(f, from, [layout.left, layout.right], {
    duration: frames.spine,
  });
  let k = 0;
  while (k + 1 < spine.roles.length && f >= startOf(spine.roles[k + 1].beat))
    k++;
  const previous = spine.roles[Math.max(0, k - 1)];
  const current = spine.roles[k];
  const p = k === 0 ? 1 : step(f, startOf(current.beat));
  const thickness = previous.weight + (current.weight - previous.weight) * p;
  const colour = interpolateColors(
    p,
    [0, 1],
    [previous.colour, current.colour],
  );
  return (
    <HRule ends={ends} y={spine.y} colour={colour} thickness={thickness} />
  );
};

// Beat 1: the small mono mark and the question, set alone; the bolt B-roll for its full 8 s in place.
// The question then settles two type steps down and heads the event log until beat 3 is under way.
const Opening: Scene = ({ f, data }) => {
  const L = layout.b1;
  const t = text(1);
  const bolts = when(1, "bolts");
  const footage = framesOf(BOLTS_S);
  // Just after the boundary the question settles two type steps down and heads the log.
  const settle = step(f, startOf(2) + LEAD);
  return (
    <>
      {f < startOf(2) + frames.reveal ? (
        <Layer clip={reveal(f, 0, { until: startOf(2) })}>
          <Mark
            f={f}
            at={when(1, "mark")}
            duration={frames.markSmall}
            x={(layout.w - L.markSize) / 2}
            y={L.markY}
            size={L.markSize}
            geometry={data.mark.mono}
            variant="mono"
          />
        </Layer>
      ) : null}
      {f < linger(2) + frames.reveal ? (
        <Layer clip={reveal(f, 0, { until: linger(2) })}>
          <Typed
            f={f}
            from={when(1, "line")}
            value={t.line}
            x={layout.left}
            y={L.lineY}
            w={layout.right - layout.left}
            family={font.display}
            fontSize={size.lg + (size.sm - size.lg) * settle}
            lineHeight={leading.tight}
            align="center"
          />
        </Layer>
      ) : null}
      {f >= bolts && f < bolts + footage + frames.reveal ? (
        <Artefact
          f={f}
          at={bolts}
          until={bolts + footage}
          x={L.frame.x}
          y={L.frame.y}
          w={L.frame.w}
          h={L.frame.h}
          caption={t.caption}
          note={t.note}
        >
          <Sequence from={bolts} durationInFrames={footage} layout="none">
            <OffthreadVideo
              muted
              src={staticFile("witness/bolts_beat1.mp4")}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                filter: still.filter,
              }}
            />
          </Sequence>
          {f >= bolts + footage ? (
            <Sequence from={bolts} layout="none">
              <Freeze frame={footage - 1}>
                <OffthreadVideo
                  muted
                  src={staticFile("witness/bolts_beat1.mp4")}
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                    filter: still.filter,
                  }}
                />
              </Freeze>
            </Sequence>
          ) : null}
        </Artefact>
      ) : null}
    </>
  );
};

// Beat 2: the skipped clip's event log hung from the spine as ten procedure parts filling in the
// order they were seen; the checks and the report's findings.
const EventLog: Scene = ({ f, data }) => {
  const L = layout.b2;
  const t = text(2);
  const open = lead(2);
  // The parts and cells stay until the chain's first label needs their rows; the checks and findings,
  // which nothing in beat 3 displaces, stay LINGER frames.
  const strip = when(3, "record") - frames.reveal;
  if (f < open || f >= linger(2) + frames.reveal) return null;
  const pitch = (layout.right - L.stripLeft) / data.parts.length;
  const seen = data.events.slice().sort((a, b) => a.order - b.order);
  const spacing = (when(2, "eventsEnd") - when(2, "events")) / seen.length;
  const missing = data.findings
    .filter((x) => x.kind === "skipped")
    .map((x) => x.part);
  const cell = stroke.cell;
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
    <>
      <Layer clip={reveal(f, open, { until: strip })}>
        {rows.map(([label, y]) => (
          <Typed
            key={label}
            f={f}
            from={open}
            value={label}
            x={layout.left}
            y={y}
            fontSize={size.xs}
            colour={color.inkMuted}
          />
        ))}
        {data.parts.map((part, i) => {
          const x = L.stripLeft + pitch * (i + 0.5);
          const event = data.events.filter((e) => e.part === part)[0];
          const landed = event
            ? when(2, "events") + Math.round(seen.indexOf(event) * spacing)
            : Infinity;
          const absent = missing.indexOf(part) >= 0;
          return (
            <React.Fragment key={part}>
              <Text
                x={x - pitch / 2}
                w={pitch}
                y={L.idsY}
                family={font.mono}
                fontSize={size.xs}
                colour={color.inkMuted}
                align="center"
              >
                {part}
              </Text>
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
              <Stated
                f={f}
                from={landed}
                x={x - pitch / 2}
                w={pitch}
                y={L.evidenceY}
                family={font.mono}
                fontSize={size.xs}
                colour={color.inkMuted}
                align="center"
              >
                {event ? event.evidence : ""}
              </Stated>
              {absent && f >= when(2, "gap") ? (
                <>
                  <svg
                    width={layout.w}
                    height={layout.h}
                    style={{ position: "absolute", left: 0, top: 0 }}
                  >
                    <rect
                      x={x - cell / 2}
                      y={L.cellY}
                      width={cell}
                      height={cell}
                      fill="none"
                      stroke={color.rejected}
                      strokeWidth={stroke.outline}
                      {...drawOn(f, when(2, "gap"), 4 * cell, frames.outline)}
                    />
                  </svg>
                  <Typed
                    f={f}
                    from={when(2, "gap")}
                    value={t.gap}
                    x={x - pitch / 2}
                    w={pitch}
                    y={L.evidenceY}
                    fontSize={size.xs}
                    colour={color.rejected}
                    align="center"
                  />
                </>
              ) : null}
            </React.Fragment>
          );
        })}
      </Layer>
      <Layer clip={reveal(f, open, { until: linger(2) })}>
        {checks.map(([name, kind], k) => {
          const y = L.checksY + k * L.rowStep;
          const pass =
            data.findings.filter((x) => x.kind === kind).length === 0;
          return (
            <React.Fragment key={name}>
              <Stated f={f} from={when(2, name)} x={L.checksX} y={y}>
                <Glyph pass={pass} />
              </Stated>
              <Typed
                f={f}
                from={when(2, name)}
                value={t[name]}
                x={L.checksX + space.s3}
                y={y}
              />
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
    </>
  );
};

// One crop of the real report page laid out at report.width and scaled to `width`: the band runs from
// the top of the element `from` to the bottom of `to`, measured inside the loaded page, so the crop
// follows the report's own layout instead of guessed offsets.
const ReportStrip: React.FC<{ from: string; to: string; width: number }> = ({
  from,
  to,
  width,
}) => {
  const R = layout.b3.report;
  const scale = width / R.width;
  const [band, setBand] = useState<[number, number]>([0, 0]);
  const [handle] = useState(() => delayRender(`report crop ${from}`));
  const measure = (event: React.SyntheticEvent<HTMLIFrameElement>) => {
    const doc = event.currentTarget.contentDocument;
    const a = doc ? doc.querySelector(from) : null;
    const b = doc ? doc.querySelector(to) : null;
    if (!a || !b)
      throw new Error(`report.html has no ${from} or ${to} to crop.`);
    setBand([
      a.getBoundingClientRect().top - space.s1,
      b.getBoundingClientRect().bottom + space.s1,
    ]);
    continueRender(handle);
  };
  return (
    <div
      style={{
        position: "relative",
        width,
        height: (band[1] - band[0]) * scale,
        overflow: "hidden",
        background: color.report,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: 0,
          top: -band[0] * scale,
          width: R.width,
          height: R.height,
          transform: `scale(${scale})`,
          transformOrigin: "0 0",
        }}
      >
        <IFrame
          src={staticFile("witness/report.html")}
          onLoad={measure}
          style={{ width: R.width, height: R.height, border: 0 }}
        />
      </div>
    </div>
  );
};

// Matched 2 to 3: the still's frame stays and receives, in place, the report its hashes protect.
const StillFrame: Scene = ({ f, data }) => {
  const L = layout.b2.still;
  const arrive = startOf(2) - 2 * LEAD;
  const swap = lead(3);
  if (f < arrive || f >= linger(3) + frames.reveal) return null;
  const first = data.events.slice().sort((a, b) => a.order - b.order)[0];
  const width = L.w - 2 * space.s2;
  const R = layout.b3.report;
  return (
    <Artefact
      f={f}
      at={arrive}
      until={linger(3)}
      x={L.x}
      y={L.y}
      w={L.w}
      h={L.h}
      caption={
        f >= swap
          ? text(3).crop
          : `${first.evidence}.png${glyph.sep}${first.part}`
      }
    >
      <Img
        src={staticFile("witness/evidence-1.png")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          filter: still.filter,
        }}
      />
      {f >= swap ? (
        <AbsoluteFill
          style={{ background: color.ground, clipPath: reveal(f, swap) }}
        >
          <ReportStrip from={R.title[0]} to={R.title[1]} width={width} />
          <div style={{ height: space.s1 }} />
          <ReportStrip from={R.findings[0]} to={R.findings[1]} width={width} />
        </AbsoluteFill>
      ) : null}
    </Artefact>
  );
};

// Beat 3: three points on the spine carry the chain; two links drawn along it; recompute rule and limit.
const Chain: Scene = ({ f, data }) => {
  const L = layout.b3;
  const t = text(3);
  const open = lead(3);
  if (f < open || f >= linger(3) + frames.reveal) return null;
  const nodes = [
    {
      x: L.points[0],
      from: when(3, "record"),
      label: t.record,
      value: data.hashes.record,
    },
    {
      x: L.points[1],
      from: when(3, "report"),
      label: t.report,
      value: data.hashes.report,
    },
    {
      x: L.points[2],
      from: when(3, "manifest"),
      label: t.manifest,
      value: data.hashes.manifest,
    },
  ];
  const half = L.valueW / 2;
  const width = layout.right - layout.left;
  return (
    <>
      <Layer clip={reveal(f, open, { until: startOf(4) })}>
        <HRule
          ends={rule(f, when(3, "report"), [L.points[0], L.points[1]])}
          y={spine.y}
          thickness={stroke.outline}
        />
        {f >= when(3, "manifest") ? (
          <HRule
            ends={rule(f, when(3, "manifest"), [L.points[1], L.points[2]])}
            y={spine.y}
            thickness={stroke.outline}
          />
        ) : null}
        <svg
          width={layout.w}
          height={layout.h}
          style={{ position: "absolute", left: 0, top: 0 }}
        >
          {nodes.map((node) => (
            <circle
              key={node.x}
              cx={node.x}
              cy={spine.y}
              r={stroke.point}
              fill={color.ground}
              stroke={color.accent}
              strokeWidth={stroke.rule}
              {...drawOn(f, open, 2 * Math.PI * stroke.point, frames.reveal)}
            />
          ))}
        </svg>
        {nodes.map((node) => (
          <React.Fragment key={node.x}>
            <Stated
              f={f}
              from={node.from}
              x={node.x - half}
              w={L.valueW}
              y={L.labelY}
              align="center"
            >
              {node.label}
            </Stated>
            <Stated
              f={f}
              from={node.from}
              x={node.x - half}
              w={L.valueW}
              y={L.valueY}
              family={font.mono}
              fontSize={size.xs}
              align="center"
              pre
            >
              {`${node.value.slice(0, node.value.length / 2)}\n${node.value.slice(node.value.length / 2)}`}
            </Stated>
          </React.Fragment>
        ))}
      </Layer>
      <Layer clip={reveal(f, open, { until: linger(3) })}>
        <Stated
          f={f}
          from={when(3, "recompute")}
          x={layout.left}
          w={width}
          y={L.formulaY}
          family={font.mono}
          fontSize={size.xs}
          colour={color.inkMuted}
          align="center"
        >
          {`${t.recompute}${data.hashes.input}`}
        </Stated>
        <Typed
          f={f}
          from={when(3, "limit")}
          value={t.limit}
          x={layout.left}
          w={width}
          y={L.limitY}
          align="center"
        />
        <Typed
          f={f}
          from={when(3, "anchor")}
          value={t.anchor}
          x={layout.left}
          w={width}
          y={L.anchorY}
          colour={color.inkMuted}
          align="center"
        />
      </Layer>
    </>
  );
};

// Beat 4: the spine as baseline; ticks arrive first, the four figures land in spoken order with the
// caveat, then nothing moves until the boundary.
const Gate: Scene = ({ f }) => {
  const L = layout.b4;
  const t = text(4);
  const open = lead(4);
  if (f < open || f >= when(5, "clean") + frames.reveal) return null;
  const items = [
    {
      from: when(4, "cases"),
      value: t.cases,
      label: t.casesLabel,
      tone: color.inkMuted,
    },
    {
      from: when(4, "tp"),
      value: t.tp,
      label: t.tpLabel,
      tone: color.verified,
    },
    {
      from: when(4, "fp"),
      value: t.fp,
      label: t.fpLabel,
      tone: color.rejected,
    },
    {
      from: when(4, "fn"),
      value: t.fn,
      label: t.fnLabel,
      tone: color.rejected,
    },
  ];
  const half = L.columnW / 2;
  // Above the spine the figures leave as beat 5 opens; below it the ticks, labels and caveat stay
  // until beat 5's columns need the space.
  const below = when(5, "clean") - frames.reveal;
  return (
    <>
      <Layer clip={reveal(f, open, { until: linger(4) })}>
        {items.map((item, i) =>
          step(f, item.from, 0) ? (
            <Text
              key={item.label}
              x={L.columns[i] - half}
              w={L.columnW}
              y={L.figureY}
              family={font.display}
              fontSize={size.xl}
              lineHeight={leading.tight}
              align="center"
            >
              {item.value}
            </Text>
          ) : null,
        )}
      </Layer>
      <Layer clip={reveal(f, open, { until: below })}>
        {items.map((item, i) => {
          const landed = step(f, item.from, 0);
          return (
            <React.Fragment key={item.label}>
              <div
                style={{
                  position: "absolute",
                  left: L.columns[i] - stroke.threshold / 2,
                  top: spine.y,
                  width: stroke.threshold,
                  height: L.tick,
                  background: landed ? item.tone : color.rampHigh,
                }}
              />
              {landed ? (
                <Text
                  x={L.columns[i] - half}
                  w={L.columnW}
                  y={L.labelY}
                  colour={color.inkMuted}
                  align="center"
                >
                  {item.label}
                </Text>
              ) : null}
            </React.Fragment>
          );
        })}
        <Stated
          f={f}
          from={when(4, "fn")}
          x={layout.left}
          w={layout.right - layout.left}
          y={L.caveatY}
          fontSize={size.md}
          align="center"
        >
          {t.caveat}
        </Stated>
      </Layer>
    </>
  );
};

// Beat 5: the geometry-only run in stated figures under the spine as a section rule; no picture and no
// model output. The four figures of beat 4 are still leaving when it opens.
const Geometry: Scene = ({ f }) => {
  const L = layout.b5;
  const t = text(5);
  const start = startOf(5);
  if (f < start || f >= linger(5) + frames.reveal) return null;
  const d = L.divider;
  return (
    <Layer clip={reveal(f, start, { until: linger(5) })}>
      <VRule
        ends={rule(f, when(5, "divider"), [d.top, d.bottom])}
        x={d.x}
        colour={color.rampHigh}
      />
      <Typed
        f={f}
        from={when(5, "scope")}
        value={t.scope}
        x={layout.left}
        y={L.scopeY}
        fontSize={size.md}
      />
      <Typed
        f={f}
        from={when(5, "scene")}
        value={t.scene}
        x={layout.left}
        y={L.sceneY}
        colour={color.inkMuted}
      />
      <Typed
        f={f}
        from={when(5, "clean")}
        value={t.clean}
        x={L.clean}
        y={L.colY}
        colour={color.inkMuted}
      />
      <Stated
        f={f}
        from={when(5, "found")}
        x={L.clean}
        y={L.foundY}
        family={font.display}
        fontSize={size.xl}
        lineHeight={leading.tight}
      >
        {t.found}
      </Stated>
      <Typed
        f={f}
        from={when(5, "found")}
        value={t.foundLabel}
        x={L.clean}
        y={L.foundLabelY}
      />
      <Stated
        f={f}
        from={when(5, "missed")}
        x={L.clean}
        y={L.missedY}
        fontSize={size.md}
      >
        <Glyph pass={false} /> {t.missed}
      </Stated>
      <Stated
        f={f}
        from={when(5, "ratio")}
        x={L.clean}
        y={L.ratioY}
        fontSize={size.md}
      >
        {t.ratio}
      </Stated>
      <Typed
        f={f}
        from={when(5, "skipped")}
        value={t.skipped}
        x={L.skipped}
        y={L.colY}
        colour={color.inkMuted}
      />
      <Stated
        f={f}
        from={when(5, "swap")}
        x={L.skipped}
        y={L.swapY}
        fontSize={size.md}
      >
        <Glyph pass /> {t.swap}
      </Stated>
      <Stated
        f={f}
        from={when(5, "blank")}
        x={L.skipped}
        y={L.blankY}
        fontSize={size.md}
      >
        <Glyph pass={false} /> {t.blank}
      </Stated>
      <Stated
        f={f}
        from={when(5, "slid")}
        x={L.skipped + space.s2}
        w={L.colW - 2 * space.s2}
        y={L.slidY}
        fontSize={size.md}
      >
        {t.slid}
      </Stated>
    </Layer>
  );
};

// Matched 5 to 6 to 7: the outline around the cause opens, as a mask edge, into the chart's frame,
// and that frame becomes the overlay crop of beat 7.
const Outline: Scene = ({ f }) => {
  const o = layout.b5.outline;
  const p = layout.b6.panel;
  const from = when(5, "outline");
  const six = startOf(6);
  if (f < from || f >= linger(7) + frames.reveal) return null;
  const k = step(f, six, frames.reveal);
  const [x1, y1, x2, y2] = o.map((v, i) => v + (p[i] - v) * k);
  const perimeter = 2 * (o[2] - o[0] + o[3] - o[1]);
  return (
    <Layer clip={reveal(f, 0, { until: linger(7) })}>
      <svg
        width={layout.w}
        height={layout.h}
        style={{ position: "absolute", left: 0, top: 0 }}
      >
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

// Beat 6: the spine is the axis; tracks mark the unit run from 0 to the threshold at 2.0, two bars stop
// at 1.97 and 1.93 with the frames where extraction stopped; then the frame freezes.
const Refusal: Scene = ({ f }) => {
  const L = layout.b6;
  const t = text(6);
  const six = startOf(6);
  const seven = startOf(7);
  if (f < six || f >= linger(6) + frames.reveal) return null;
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
  const lineX = L.barX + L.barL;
  const rows = [
    {
      y: L.rows[0],
      label: t.clean,
      value: t.cleanValue,
      from: when(6, "clean"),
      stop: t.cleanStop,
    },
    {
      y: L.rows[1],
      label: t.skipped,
      value: t.skippedValue,
      from: when(6, "skipped"),
      stop: t.skippedStop,
    },
  ];
  const bars = when(6, "bars");
  return (
    <>
      {f < seven + frames.reveal ? (
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
          <svg
            width={w}
            height={h}
            style={{ position: "absolute", left: 0, top: 0 }}
          >
            {rows.map((row) => (
              <line
                key={`track-${row.label}`}
                x1={L.barX - x1}
                y1={row.y - y1}
                x2={lineX - x1}
                y2={row.y - y1}
                stroke={color.rampLow}
                strokeWidth={stroke.bar}
              />
            ))}
            {f >= bars
              ? rows.map((row) => {
                  const length = (L.barL * parseFloat(row.value)) / required;
                  return (
                    <line
                      key={row.label}
                      x1={L.barX - x1}
                      y1={row.y - y1}
                      x2={L.barX - x1 + length}
                      y2={row.y - y1}
                      stroke={color.ink}
                      strokeWidth={stroke.bar}
                      {...drawOn(f, bars, length, frames.bars)}
                    />
                  );
                })
              : null}
          </svg>
          {rows.map((row) => (
            <React.Fragment key={row.label}>
              <Typed
                f={f}
                from={six}
                value={row.label}
                x={L.labelX - x1}
                y={row.y - y1 - (size.sm * leading.body) / 2}
                colour={color.inkMuted}
              />
              <Stated
                f={f}
                from={row.from}
                x={L.valueX - x1}
                y={row.y - y1 - (size.lg * leading.tight) / 2}
                family={font.display}
                fontSize={size.lg}
                lineHeight={leading.tight}
              >
                {row.value}
              </Stated>
              <Stated
                f={f}
                from={when(6, "stopped")}
                x={L.valueX - x1}
                y={row.y - y1 + L.stopGap}
                family={font.mono}
                fontSize={size.xs}
                colour={color.inkMuted}
              >
                <Glyph pass={false} /> {row.stop}
              </Stated>
            </React.Fragment>
          ))}
        </div>
      ) : null}
      {f >= when(6, "threshold") && f < seven + frames.reveal ? (
        <Layer clip={reveal(f, six, { until: seven })}>
          <svg
            width={layout.w}
            height={layout.h}
            style={{ position: "absolute", left: 0, top: 0 }}
          >
            <line
              x1={lineX}
              y1={spine.y}
              x2={lineX}
              y2={L.lineBottom}
              stroke={color.accent}
              strokeWidth={stroke.threshold}
              {...drawOn(
                f,
                when(6, "threshold"),
                L.lineBottom - spine.y,
                frames.threshold,
              )}
            />
          </svg>
        </Layer>
      ) : null}
      <Layer clip={reveal(f, six, { until: linger(6) })}>
        <Typed
          f={f}
          from={when(6, "title")}
          value={t.title}
          x={layout.left}
          y={L.titleY}
          fontSize={size.md}
        />
        <Stated
          f={f}
          from={bars}
          x={L.barX}
          y={L.zeroY}
          family={font.mono}
          fontSize={size.xs}
          colour={color.inkMuted}
        >
          {t.zero}
        </Stated>
        <Stated
          f={f}
          from={when(6, "required")}
          x={lineX - L.requiredW / 2}
          w={L.requiredW}
          y={L.requiredY}
          align="center"
        >
          {t.required}
        </Stated>
      </Layer>
    </>
  );
};

// Beat 7: inside the chart's frame, the model overlays of both clips at one crop, clean then skipped;
// above the spine the measured run, each figure landing as it is spoken.
const Model: Scene = ({ f }) => {
  const L = layout.b7;
  const P = layout.b6.panel;
  const t = text(7);
  const seven = startOf(7);
  if (f < seven || f >= linger(7) + frames.reveal) return null;
  const c = L.crop;
  const scale = (P[2] - P[0] - 2 * space.s2) / c.w;
  const image: React.CSSProperties = {
    position: "absolute",
    left: -c.x * scale,
    top: -c.y * scale,
    width: c.srcW * scale,
    height: c.srcH * scale,
    filter: still.filter,
  };
  const swap = when(7, "skipped");
  // The row above the spine waits for beat 6's labels to leave.
  const clear = linger(6) + frames.reveal;
  const later = (key: string) => Math.max(when(7, key), clear);
  const [c0, c1, c2, c3] = L.columns;
  return (
    <>
      <Artefact
        f={f}
        at={seven}
        until={linger(7)}
        x={P[0]}
        y={P[1]}
        w={P[2] - P[0]}
        h={P[3] - P[1]}
        caption={f >= swap ? t.skipped : t.clean}
      >
        <Img
          src={staticFile("witness/model_clean_anchor48.png")}
          style={image}
        />
        <AbsoluteFill style={{ clipPath: reveal(f, swap) }}>
          <Img
            src={staticFile("witness/model_skipped_anchor28.png")}
            style={image}
          />
        </AbsoluteFill>
      </Artefact>
      <Layer clip={reveal(f, seven, { until: startOf(8) })}>
        <Typed
          f={f}
          from={later("meta")}
          value={t.meta}
          x={c0}
          y={L.labelY}
          colour={color.inkMuted}
        />
        <Stated
          f={f}
          from={later("model")}
          x={c0}
          y={L.valueY}
          family={font.mono}
          fontSize={size.lg}
          lineHeight={leading.tight}
        >
          {t.model}
        </Stated>
        <Stated
          f={f}
          from={later("anchors")}
          x={c1}
          y={L.valueY}
          family={font.display}
          fontSize={size.lg}
          lineHeight={leading.tight}
        >
          {t.anchors}
        </Stated>
        <Stated
          f={f}
          from={later("anchors")}
          x={c1}
          w={L.columnW + space.s4}
          y={L.noteY}
          fontSize={size.xs}
          colour={color.inkMuted}
        >
          {t.anchorsLabel}
        </Stated>
        <Stated
          f={f}
          from={later("cost")}
          x={c2}
          y={L.valueY}
          family={font.display}
          fontSize={size.lg}
          lineHeight={leading.tight}
        >
          {t.cost}
        </Stated>
        <Stated f={f} from={later("agree")} x={c3} y={L.valueY}>
          <Glyph pass />
        </Stated>
        <Typed
          f={f}
          from={later("agree")}
          value={t.agree}
          x={c3 + space.s3}
          w={L.columnW - space.s3}
          y={L.valueY}
        />
      </Layer>
    </>
  );
};

// Beat 8: the claim above the spine, now the closing rule; the overlay stays two seconds, then the
// stroke-only gradient mark is drawn on, five joints of one construction, and a slow rule beneath it.
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
      <Mark
        f={f}
        at={when(8, "mark")}
        duration={frames.markLarge}
        x={(layout.w - L.markSize) / 2}
        y={L.markY}
        size={L.markSize}
        geometry={data.mark.mono}
        rims={data.mark.full.rims}
        variant="stroke"
      />
      <HRule
        ends={rule(f, from, L.rule, { duration: when(8, "ruleEnd") - from })}
        y={L.ruleY}
      />
    </Layer>
  );
};

// Q6: from the moment beat 7's agreement lands, the calibration limit sits in the lower-left column
// above the subtitle band, types on once and does not move again.
const Caveat: Scene = ({ f }) => {
  const from = Math.max(when(7, "agree"), linger(6) + frames.reveal);
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
  const beat = BEATS.filter(
    (b) => f >= startOf(b.number) && f < endOf(b.number),
  )[0];
  if (
    !beat ||
    !beat.text.source ||
    !step(f, startOf(beat.number) + frames.reveal, 0)
  )
    return null;
  return (
    <Text
      x={layout.left}
      w={layout.right - layout.left}
      y={layout.sourceY}
      family={font.mono}
      fontSize={size.xs}
      colour={color.inkMuted}
      align="right"
    >
      {beat.text.source}
    </Text>
  );
};

export const Film: Scene = (props) => (
  <>
    <Spine {...props} />
    <Opening {...props} />
    <EventLog {...props} />
    <StillFrame {...props} />
    <Chain {...props} />
    <Gate {...props} />
    <Geometry {...props} />
    <Refusal {...props} />
    <Model {...props} />
    <Outline {...props} />
    <Close {...props} />
    <Source {...props} />
    <Caveat {...props} />
    <Subtitles f={props.f} />
  </>
);
