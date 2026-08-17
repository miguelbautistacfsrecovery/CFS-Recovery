import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { COLORS, EASE, FPS, STROKE } from "../theme";
import { Frame, SoftBackdrop, greyLine, line } from "../shared";

const clamp = {
  extrapolateLeft: "clamp" as const,
  extrapolateRight: "clamp" as const,
};

// Standing silhouette, centered. Local coordinates inside translate(960 0).
const BODY_PATH =
  "M -92 432 C -98 522 -70 562 -66 642 C -63 722 -68 802 -70 878 L 70 878 C 68 802 63 722 66 642 C 70 562 98 522 92 432 C 58 400 -58 400 -92 432 Z";
const HEAD = { cx: 0, cy: 318, r: 52 };

// Deterministic pseudo-random from an index, for varied but stable motion.
const rand = (i: number, salt: number) => {
  const x = Math.sin(i * 127.1 + salt * 311.7) * 43758.5453;
  return x - Math.floor(x);
};

const INNER_LINES = Array.from({ length: 16 }).map((_, i) => {
  const y = 300 + (i / 15) * 560;
  const amp = 10 + rand(i, 1) * 14;
  const phase = rand(i, 2) * Math.PI * 2;
  const period = (2.4 + rand(i, 3) * 2.6) * FPS;
  const yPeriod = (3 + rand(i, 6) * 3) * FPS;
  const rotPeriod = (4 + rand(i, 7) * 3) * FPS;
  const d = `M -190 ${y} C -120 ${y - amp} -60 ${y + amp} 0 ${y - amp * 0.6} C 60 ${
    y + amp
  } 120 ${y - amp} 190 ${y + amp * 0.5}`;
  return { d, phase, period, yPeriod, rotPeriod, i };
});

export const Shot2: React.FC = () => {
  const frame = useCurrentFrame();

  const sceneIn = interpolate(frame, [0, 22], [0, 1], { ...clamp, easing: EASE });

  // The bubble travels in from the right and stops flat against the
  // silhouette's outer edge. It never crosses the boundary.
  const bubbleX = interpolate(frame, [66, 130], [2080, 1064], {
    ...clamp,
    easing: EASE,
  });

  // Soft daylight backdrop with a barely-there drift (parallax under 8%).
  const parallax = Math.sin((frame / (9 * FPS)) * Math.PI * 2) * 10;

  return (
    <Frame>
      <svg
        viewBox="0 0 1920 1080"
        style={{ position: "absolute", inset: 0, opacity: sceneIn }}
      >
        <defs>
          <clipPath id="silhouette">
            <path d={BODY_PATH} transform="translate(960 0)" />
            <circle
              cx={960 + HEAD.cx}
              cy={HEAD.cy}
              r={HEAD.r}
              transform-origin="center"
            />
          </clipPath>
        </defs>

        {/* soft daylight */}
        <g style={{ translate: `${parallax}px 0px` }}>
          <SoftBackdrop id="bd2" cx={960} cy={560} rx={640} ry={460} opacity={0.35} />
        </g>

        {/* ground */}
        <path d="M 640 878 L 1280 878" {...greyLine} />

        {/* restless interior, contained entirely inside the silhouette */}
        <g clipPath="url(#silhouette)">
          <rect x={0} y={0} width={1920} height={1080} fill={COLORS.bg} />
          {INNER_LINES.map((l) => {
            const dx = Math.sin((frame / l.period) * Math.PI * 2 + l.phase) * 46;
            const dy =
              Math.sin((frame / l.yPeriod) * Math.PI * 2 + l.phase * 1.7) * 12;
            const rot =
              Math.sin((frame / l.rotPeriod) * Math.PI * 2 + l.phase * 0.6) * 4;
            return (
              <g
                key={l.i}
                style={{
                  translate: `${960 + dx}px ${dy}px`,
                  rotate: `${rot}deg`,
                }}
              >
                <path
                  d={l.d}
                  fill="none"
                  stroke={COLORS.grey}
                  strokeWidth={STROKE}
                  strokeLinecap="round"
                  opacity={0.6}
                />
              </g>
            );
          })}
        </g>

        {/* the outline holds perfectly still */}
        <g transform="translate(960 0)">
          <path d={BODY_PATH} {...line} />
          <circle cx={HEAD.cx} cy={HEAD.cy} r={HEAD.r} {...line} />
        </g>

        {/* "you look fine" arrives and stops at the boundary */}
        <g style={{ translate: `${bubbleX}px 470px` }}>
          {/* tail points left; its tip is the group origin */}
          <path
            d="M 0 0 L 30 -16 L 30 16 Z"
            fill={COLORS.bg}
            stroke={COLORS.ink}
            strokeWidth={STROKE}
            strokeLinejoin="round"
          />
          <rect
            x={28}
            y={-44}
            width={300}
            height={88}
            rx={24}
            fill={COLORS.bg}
            stroke={COLORS.ink}
            strokeWidth={STROKE}
          />
          <path
            d="M 30 -14 L 30 14"
            stroke={COLORS.bg}
            strokeWidth={STROKE + 2}
          />
          <text
            x={178}
            y={13}
            textAnchor="middle"
            fill={COLORS.ink}
            style={{ fontSize: 38, letterSpacing: 0.5 }}
          >
            you look fine
          </text>
        </g>
      </svg>
    </Frame>
  );
};
