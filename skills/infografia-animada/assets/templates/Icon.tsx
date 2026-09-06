import React from "react";
import { useCurrentFrame } from "remotion";
import type { SimpleIcon } from "simple-icons";
import { useAppear } from "./useAppear";

// A simple-icons logo with a spring entrance and an optional continuous pulse.
// Paint it with a palette colour, not the brand hex, unless the user asks otherwise:
// eight brand colours would wreck a three-tone palette.
export const Icon: React.FC<{
  icon: SimpleIcon;
  size?: number;
  color: string;
  appearFrame: number;
  pulse?: boolean;
  background?: string; // solid background when a connector line ends on this icon
}> = ({ icon, size = 40, color, appearFrame, pulse = false, background }) => {
  const frame = useCurrentFrame();
  const { opacity, scale, translateY } = useAppear(appearFrame);
  const beat = pulse ? 1 + 0.03 * Math.sin(frame / 12) : 1;
  const pad = background ? size * 0.35 : 0;
  return (
    <div
      style={{
        width: size + pad * 2,
        height: size + pad * 2,
        borderRadius: "50%",
        background,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity,
        transform: `translateY(${translateY}px) scale(${scale * beat})`,
        transformOrigin: "center",
      }}
    >
      <svg width={size} height={size} viewBox="0 0 24 24" role="img" aria-label={icon.title}>
        <path d={icon.path} fill={color} />
      </svg>
    </div>
  );
};
