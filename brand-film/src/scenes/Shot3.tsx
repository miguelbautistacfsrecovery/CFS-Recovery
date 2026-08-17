import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { COLORS, EASE, STROKE } from "../theme";
import { Frame, SoftBackdrop, greyLine } from "../shared";

const clamp = {
  extrapolateLeft: "clamp" as const,
  extrapolateRight: "clamp" as const,
};

const SURFACE_Y = 700;
const PANEL_W = 460;
const PANEL_H = 36;
const OFFSETS = [-16, 10, -8, 14, -6, -10]; // bottom to top; last is the placed one

const panelY = (i: number, gap: number) =>
  SURFACE_Y - PANEL_H * (i + 1) - gap * i;

const Panel: React.FC<{ x: number; y: number; label?: string }> = ({
  x,
  y,
  label,
}) => (
  <g>
    <rect
      x={x - PANEL_W / 2}
      y={y}
      width={PANEL_W}
      height={PANEL_H}
      rx={8}
      fill={COLORS.grey}
      fillOpacity={0.16}
      stroke={COLORS.ink}
      strokeWidth={STROKE}
    />
    {label ? (
      <text
        x={x}
        y={y + PANEL_H / 2 + 8}
        textAnchor="middle"
        fill={COLORS.ink}
        style={{ fontSize: 23, letterSpacing: 0.5 }}
      >
        {label}
      </text>
    ) : null}
  </g>
);

export const Shot3: React.FC = () => {
  const frame = useCurrentFrame();

  const sceneIn = interpolate(frame, [0, 22], [0, 1], { ...clamp, easing: EASE });

  // Hand lowers the final panel into place, then withdraws.
  const descend = interpolate(frame, [30, 82], [-470, 0], { ...clamp, easing: EASE });
  const ascend = interpolate(frame, [94, 150], [0, -580], { ...clamp, easing: EASE });
  const placed = frame >= 82;

  // The stack compresses under the weight.
  const gap = interpolate(frame, [84, 112], [16, 9], { ...clamp, easing: EASE });

  // Slow lateral wobble, three degrees maximum, decaying but never settling.
  const t = Math.max(0, frame - 96);
  const amplitude = 3 * (0.38 + 0.62 * Math.exp(-t / 120));
  const wobble = frame < 96 ? 0 : amplitude * Math.sin((t / 56) * Math.PI * 2);

  // Faint backdrop parallax against the hand's travel.
  const parallax = interpolate(frame, [30, 82], [0, 12], { ...clamp, easing: EASE });

  const carriedY = panelY(5, 16) + descend;
  const handY = placed ? panelY(5, 16) + ascend : carriedY;
  // The hand grips the panel toward its right end so the label stays visible.
  const handX = 960 + OFFSETS[5] + 128;

  return (
    <Frame>
      <svg
        viewBox="0 0 1920 1080"
        style={{ position: "absolute", inset: 0, opacity: sceneIn }}
      >
        {/* backdrop layer */}
        <g style={{ translate: `0px ${parallax}px` }}>
          <SoftBackdrop id="bd3" cx={960} cy={560} rx={700} ry={380} opacity={0.35} />
        </g>

        {/* surface */}
        <path d={`M 560 ${SURFACE_Y + 4} L 1360 ${SURFACE_Y + 4}`} {...greyLine} />

        {/* the stack */}
        <g
          style={{ rotate: `${wobble}deg` }}
          transform-origin={`960px ${SURFACE_Y}px`}
        >
          {OFFSETS.slice(0, 5).map((off, i) => (
            <Panel key={i} x={960 + off} y={panelY(i, gap)} />
          ))}
          {placed ? (
            <Panel
              x={960 + OFFSETS[5]}
              y={panelY(5, gap)}
              label="so much better"
            />
          ) : null}
        </g>

        {/* the carried panel, before it joins the stack */}
        {placed ? null : (
          <Panel x={handX} y={carriedY} label="so much better" />
        )}

        {/* the hand: a flat side-view hand resting on the panel's top edge,
            origin at the contact point, forearm leaving top right */}
        <g style={{ translate: `${handX}px ${handY}px` }}>
          {/* vertical forearm from the top of frame */}
          <path
            d="M -30 -110 L -30 -760"
            fill="none"
            stroke={COLORS.ink}
            strokeWidth={STROKE}
            strokeLinecap="round"
          />
          <path
            d="M 34 -105 L 34 -760"
            fill="none"
            stroke={COLORS.ink}
            strokeWidth={STROKE}
            strokeLinecap="round"
          />
          {/* downward hand, fingertips resting on the panel */}
          <path
            d="M -30 -110
               C -44 -102 -52 -84 -52 -62
               L -52 -18
               C -52 -4 -46 2 -38 2 C -31 2 -27 -3 -27 -12
               C -27 -3 -22 2 -15 2 C -8 2 -4 -3 -4 -12
               C -4 -3 1 2 8 2 C 15 2 19 -3 19 -12
               C 19 -3 24 2 31 2 C 39 2 44 -4 44 -16
               L 44 -30
               C 44 -46 52 -54 56 -66
               C 60 -80 56 -94 46 -102
               C 43 -104 38 -105 34 -105"
            fill={COLORS.bg}
            stroke={COLORS.ink}
            strokeWidth={STROKE}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </g>
      </svg>
    </Frame>
  );
};
