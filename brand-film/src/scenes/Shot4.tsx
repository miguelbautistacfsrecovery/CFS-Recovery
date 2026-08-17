import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { COLORS, EASE } from "../theme";
import { Frame, greyLine, line } from "../shared";

const clamp = {
  extrapolateLeft: "clamp" as const,
  extrapolateRight: "clamp" as const,
};

const BENCH_Y = 700;

// Front-facing seated figure. Origin at the bench line, centered.
const FrontFigure: React.FC = () => (
  <g>
    <circle cx={0} cy={-182} r={34} {...line} />
    <path
      d="M -62 0 L -62 -80 C -62 -118 -32 -134 0 -134 C 32 -134 62 -118 62 -80 L 62 0"
      {...line}
      fill={COLORS.bg}
    />
  </g>
);

export const Shot4: React.FC = () => {
  const frame = useCurrentFrame();

  const sceneIn = interpolate(frame, [0, 22], [0, 1], { ...clamp, easing: EASE });

  // The only cyan in the film: a soft light field blooming between them.
  const bloomOpacity = interpolate(frame, [30, 104], [0, 0.2], {
    ...clamp,
    easing: EASE,
  });
  const bloomScale = interpolate(frame, [30, 104], [0.65, 1], {
    ...clamp,
    easing: EASE,
    output: "perceptual-scale",
  });

  const lineOpacity = interpolate(frame, [76, 112], [0, 1], { ...clamp, easing: EASE });
  const lineRise = interpolate(frame, [76, 112], [14, 0], { ...clamp, easing: EASE });

  return (
    <Frame>
      <svg
        viewBox="0 0 1920 1080"
        style={{ position: "absolute", inset: 0, opacity: sceneIn }}
      >
        <defs>
          <radialGradient id="bloom">
            <stop offset="0%" stopColor={COLORS.cyan} stopOpacity={1} />
            <stop offset="55%" stopColor={COLORS.cyan} stopOpacity={0.45} />
            <stop offset="100%" stopColor={COLORS.cyan} stopOpacity={0} />
          </radialGradient>
        </defs>

        {/* cyan light field, behind the figures */}
        <g
          opacity={bloomOpacity}
          style={{ scale: String(bloomScale) }}
          transform-origin="960px 620px"
        >
          <circle cx={960} cy={620} r={240} fill="url(#bloom)" />
        </g>

        {/* bench */}
        <path d={`M 560 ${BENCH_Y} L 1360 ${BENCH_Y}`} {...greyLine} />

        {/* two figures, side by side, facing forward */}
        <g transform={`translate(866 ${BENCH_Y})`}>
          <FrontFigure />
        </g>
        <g transform={`translate(1054 ${BENCH_Y})`}>
          <FrontFigure />
        </g>

        {/* final line */}
        <text
          x={960}
          y={880}
          textAnchor="middle"
          fill={COLORS.ink}
          opacity={lineOpacity}
          style={{ fontSize: 54, letterSpacing: 0.5, translate: `0px ${lineRise}px` }}
        >
          you don&apos;t have to figure this out alone
        </text>
      </svg>
    </Frame>
  );
};
