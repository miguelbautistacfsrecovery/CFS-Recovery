import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { COLORS, EASE, STROKE } from "../theme";
import {
  Frame,
  ICONS,
  SeatedProfileFigure,
  SoftBackdrop,
  greyLine,
} from "../shared";

const clamp = {
  extrapolateLeft: "clamp" as const,
  extrapolateRight: "clamp" as const,
};

const RING_CENTER = { x: 1404, y: 504 };
const RING_RADIUS = 132;

// The bubble travels from above the left figure until its leading edge
// meets the ring. It never enters it.
const BUBBLE_START = { x: 700, y: 380 };
const BUBBLE_END = { x: 1146, y: 466 };
const BUBBLE_W = 224;
const BUBBLE_H = 104;

export const Shot1: React.FC = () => {
  const frame = useCurrentFrame();

  const sceneIn = interpolate(frame, [0, 22], [0, 1], { ...clamp, easing: EASE });

  const bubbleIn = interpolate(frame, [28, 52], [0, 1], { ...clamp, easing: EASE });
  const driftX = interpolate(frame, [56, 138], [BUBBLE_START.x, BUBBLE_END.x], {
    ...clamp,
    easing: EASE,
  });
  const driftY = interpolate(frame, [56, 138], [BUBBLE_START.y, BUBBLE_END.y], {
    ...clamp,
    easing: EASE,
  });

  // Contact at ~f138. Dissolve with no impact: the shell fades, the icons
  // ease the last few pixels toward the ring and fade to nothing.
  const shellOpacity = interpolate(frame, [138, 160], [1, 0], { ...clamp, easing: EASE });
  const iconOpacity = interpolate(frame, [140, 170], [1, 0], { ...clamp, easing: EASE });
  const iconDrift = interpolate(frame, [140, 170], [0, 1], { ...clamp, easing: EASE });

  const captionOpacity = interpolate(frame, [146, 170], [0, 1], { ...clamp, easing: EASE });

  // Background layer parallax, well under 8% of the bubble's travel.
  const parallax = interpolate(frame, [56, 138], [0, -26], { ...clamp, easing: EASE });

  return (
    <Frame>
      <svg
        viewBox="0 0 1920 1080"
        style={{ position: "absolute", inset: 0, opacity: sceneIn }}
      >
        {/* backdrop layer, drifts slightly against the bubble */}
        <g style={{ translate: `${parallax}px 0px` }}>
          <SoftBackdrop id="bd1" cx={980} cy={620} rx={720} ry={340} />
        </g>

        {/* ground */}
        <path d="M 300 806 L 1660 806" {...greyLine} />

        {/* left figure, facing right */}
        <g transform="translate(540 700)">
          <SeatedProfileFigure />
        </g>

        {/* right figure, facing left */}
        <g transform="translate(1420 700) scale(-1 1)">
          <SeatedProfileFigure />
        </g>

        {/* faint ring of the same icons already around the second figure */}
        <g opacity={0.2}>
          {Array.from({ length: 8 }).map((_, i) => {
            const angle = (i / 8) * Math.PI * 2 - Math.PI / 2;
            const Icon = ICONS[i % 3];
            const x = RING_CENTER.x + Math.cos(angle) * RING_RADIUS;
            const y = RING_CENTER.y + Math.sin(angle) * RING_RADIUS;
            return (
              <g key={i} transform={`translate(${x} ${y}) scale(0.9)`}>
                <Icon />
              </g>
            );
          })}
        </g>

        {/* the released speech bubble */}
        <g
          opacity={bubbleIn}
          style={{ translate: `${driftX}px ${driftY}px` }}
        >
          <g opacity={shellOpacity}>
            <rect
              x={-BUBBLE_W / 2}
              y={-BUBBLE_H / 2}
              width={BUBBLE_W}
              height={BUBBLE_H}
              rx={26}
              fill={COLORS.bg}
              stroke={COLORS.ink}
              strokeWidth={STROKE}
            />
            <path
              d={`M ${-BUBBLE_W / 2 + 30} ${BUBBLE_H / 2 - 1} L ${-BUBBLE_W / 2 + 16} ${
                BUBBLE_H / 2 + 24
              } L ${-BUBBLE_W / 2 + 56} ${BUBBLE_H / 2 - 1}`}
              fill={COLORS.bg}
              stroke={COLORS.ink}
              strokeWidth={STROKE}
              strokeLinejoin="round"
            />
            <path
              d={`M ${-BUBBLE_W / 2 + 32} ${BUBBLE_H / 2 - 2} L ${-BUBBLE_W / 2 + 54} ${
                BUBBLE_H / 2 - 2
              }`}
              stroke={COLORS.bg}
              strokeWidth={STROKE + 2}
            />
          </g>
          {ICONS.map((Icon, i) => {
            // Each icon eases a short distance toward the ring as it dissolves.
            const towardRing = iconDrift * 54;
            return (
              <g
                key={i}
                opacity={iconOpacity}
                transform={`translate(${(i - 1) * 62 + towardRing * 0.9} ${
                  towardRing * 0.25
                })`}
              >
                <Icon />
              </g>
            );
          })}
        </g>

        {/* small caption, low in frame */}
        <text
          x={960}
          y={962}
          textAnchor="middle"
          fill={COLORS.ink}
          opacity={captionOpacity * 0.85}
          style={{ fontSize: 38, letterSpacing: 0.5 }}
        >
          found at 3:00 am
        </text>
      </svg>
    </Frame>
  );
};
