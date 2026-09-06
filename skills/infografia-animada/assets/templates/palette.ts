// Fixed palette for the piece. Fill it in from the user's answer; never derive it
// from the reference image.
export const palette = {
  bg: "#0B1020", // page background
  bandA: "#132040", // odd band or block
  bandB: "#0D1529", // even band or block
  card: "#1A2A4A", // cards, always a solid background
  cardBorder: "#2C4270",
  ink: "#EEF3FF", // primary ink
  inkMuted: "#A3B3D3", // secondary ink
  accent: "#FFB020", // numerals and section titles
  flow: "#3DD6E8", // connector lines and dotted flow
  chipBg: "#0B1020",
} as const;
