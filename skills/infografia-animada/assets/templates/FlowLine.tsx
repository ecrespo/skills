import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { evolvePath } from "@remotion/paths";
import { palette } from "./palette";

// A line that draws itself with stroke-dashoffset and, once drawn, keeps a dotted
// pattern running along the stroke forever. The continuous flow is what keeps the
// piece alive after every element has entered.
export const FlowLine: React.FC<{ d: string; appearFrame: number }> = ({
  d,
  appearFrame,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - appearFrame;
  const draw = spring({
    frame: local,
    fps,
    config: { damping: 200, mass: 0.6 },
    durationInFrames: 24,
  });
  const evolved = evolvePath(draw, d);
  const flowOpacity = interpolate(local, [20, 34], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // Period 24 = (3 + 9) * 2, so the loop never jumps.
  const flowOffset = -((frame * 1.4) % 24);
  return (
    <>
      <path
        d={d}
        fill="none"
        stroke={palette.flow}
        strokeOpacity={0.35}
        strokeWidth={2}
        strokeLinecap="round"
        strokeDasharray={evolved.strokeDasharray}
        strokeDashoffset={evolved.strokeDashoffset}
      />
      <path
        d={d}
        fill="none"
        stroke={palette.flow}
        strokeWidth={3}
        strokeLinecap="round"
        strokeDasharray="3 9"
        strokeDashoffset={flowOffset}
        style={{ opacity: flowOpacity }}
      />
    </>
  );
};
