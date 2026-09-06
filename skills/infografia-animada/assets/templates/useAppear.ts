import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// Entrance hook shared by every element of the infographic.
// Spring (damping 200, mass 0.6) plus clamped interpolation: never linear, never instant.
export const useAppear = (appearFrame: number, springDurationInFrames = 18) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame - appearFrame;
  const progress = spring({
    frame: localFrame,
    fps,
    config: { damping: 200, mass: 0.6 },
    durationInFrames: springDurationInFrames,
  });
  const opacity = interpolate(localFrame, [0, springDurationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = interpolate(progress, [0, 1], [0.86, 1]);
  const translateY = interpolate(progress, [0, 1], [14, 0]);
  return { opacity, scale, translateY };
};
