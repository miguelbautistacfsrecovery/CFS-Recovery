import React from "react";
import { AbsoluteFill } from "remotion";
import { COLORS, FONT, STROKE } from "./theme";

export const Frame: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        fontFamily: FONT,
        fontWeight: 500,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

export const line = {
  fill: "none",
  stroke: COLORS.ink,
  strokeWidth: STROKE,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

export const greyLine = {
  ...line,
  stroke: COLORS.grey,
};

// The three icons that travel in the shot 1 speech bubble and repeat in the
// receiving figure's ring. Each is drawn inside a ~40x40 box centered at 0,0.
export const MagnifierIcon: React.FC<{ color?: string }> = ({
  color = COLORS.ink,
}) => (
  <g>
    <circle cx={-3} cy={-3} r={10} {...line} stroke={color} />
    <path d="M 4.5 4.5 L 13 13" {...line} stroke={color} />
  </g>
);

export const CapsuleIcon: React.FC<{ color?: string }> = ({
  color = COLORS.ink,
}) => (
  <g transform="rotate(-35)">
    <rect x={-14} y={-7.5} width={28} height={15} rx={7.5} {...line} stroke={color} />
    <path d="M 0 -7.5 L 0 7.5" {...line} stroke={color} />
  </g>
);

export const LeafIcon: React.FC<{ color?: string }> = ({
  color = COLORS.ink,
}) => (
  <g>
    <path
      d="M 0 14 C -11 6 -12 -8 0 -15 C 12 -8 11 6 0 14 Z"
      {...line}
      stroke={color}
    />
    <path d="M 0 12 L 0 -6" {...line} stroke={color} />
  </g>
);

export const ICONS = [MagnifierIcon, CapsuleIcon, LeafIcon];

// Soft-edged warm backdrop, used for the subtle parallax layer.
export const SoftBackdrop: React.FC<{
  id: string;
  cx: number;
  cy: number;
  rx: number;
  ry: number;
  opacity?: number;
}> = ({ id, cx, cy, rx, ry, opacity = 0.4 }) => (
  <g>
    <defs>
      <radialGradient id={id}>
        <stop offset="0%" stopColor={COLORS.greySoft} stopOpacity={1} />
        <stop offset="70%" stopColor={COLORS.greySoft} stopOpacity={0.6} />
        <stop offset="100%" stopColor={COLORS.greySoft} stopOpacity={0} />
      </radialGradient>
    </defs>
    <ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill={`url(#${id})`} opacity={opacity} />
  </g>
);

// Seated figure in profile, facing right. Origin is at the hip.
// Mirror with scaleX(-1) for a figure facing left.
export const SeatedProfileFigure: React.FC = () => (
  <g>
    {/* head */}
    <circle cx={16} cy={-196} r={30} {...line} />
    {/* back */}
    <path d="M 0 0 C 2 -60 6 -120 10 -162" {...line} />
    {/* arm resting toward the knee */}
    <path d="M 8 -140 C 28 -108 44 -92 62 -84" {...line} />
    {/* thigh */}
    <path d="M 0 0 L 86 -2" {...line} />
    {/* shin */}
    <path d="M 86 -2 L 88 96" {...line} />
    {/* foot */}
    <path d="M 88 96 L 114 96" {...line} />
    {/* stool */}
    <path d="M -34 10 L 34 10" {...greyLine} />
    <path d="M -24 10 L -26 104" {...greyLine} />
    <path d="M 24 10 L 26 104" {...greyLine} />
  </g>
);
