# Structural patterns and layout recipes

Classify the reference into one of these patterns and follow its recipe. Measurements target
960x1280; scale them proportionally for other formats.

## A. Numbered diagonal bands (step poster)

Typical reference: stacked horizontal bands with slanted edges, a large numeral per band, a heavy
title alternating sides, and an illustration opposite it.

Recipe:

- Header 200 px, bands 150 px, footer 180 px, six bands.
- Fixed numeral column at x around 470, circular badge radius 30 in the accent colour.
- Even bands: title on the left, right-aligned (x 40 to 420), card on the right (x 534 to 910). Odd
  bands mirror it (card x 50 to 406, title x 520 to 920).
- An S-curve spine between numerals plus a short horizontal connector from numeral to card.
- The last spine segment descends into the footer card (rules, summary).
- Replace the illustration with the detail card (item list plus chips) or one large simple-icons
  logo on a solid disc.

## B. Hub with branches (centre plus satellites)

Typical reference: a central circle or card with four to eight nodes around it, joined by lines.

Recipe:

- Hub at the geometric centre (slightly high on vertical canvases), 220 to 260 px.
- Satellites on a ring at angle `i * 2 * pi / n - pi / 2`, radius around 330 px on a 960 px width.
  On 3:4, use an ellipse (rx 330, ry 400) to exploit the height.
- Each satellite: icon, title and a short card with a solid background.
- Hub-to-satellite lines straight or gently curved; the dotted flow radiates from the hub.
- Entrance order: hub first, then satellites clockwise every 12 to 16 frames, each line 4 frames
  after its satellite.

## C. Vertical list or checklist

Typical reference: rows with an icon on the left, a title and a description, separated by a
continuous vertical rule.

Recipe:

- Vertical line at x around 120 that draws top to bottom, with circular nodes per row.
- Rows 110 to 140 px; card on the right (x 180 to 910) with a solid background.
- The dotted flow travels the vertical line and the nodes cover it.

## D. Decision tree

Typical reference: a root node at the top, yes/no branches, leaves at the bottom.

Recipe:

- Levels 220 px apart. Nodes are cards with solid backgrounds; branch labels ("yes", "no") are chips
  over the line, also with solid backgrounds.
- Use elbowed lines (`M x0 y0 V ym H x1 V y1`) so branches stay readable.
- Enter level by level, left to right within a level.

## E. Card grid

Typical reference: a 2x3 or 3x3 grid of cards with icon, title and text.

Recipe:

- Grid gutter 24 px; cards with solid backgrounds and a 1 px border.
- If the cards relate to each other, run lines through the gutters. If not, skip lines but keep the
  icons gently pulsing so the piece does not go dead.
- Enter in reading order, 10 to 14 frames apart.

## F. Horizontal timeline or serpentine

Typical reference: milestones along a zigzagging line.

Recipe:

- A single serpentine path with milestone badges placed at equal path-length intervals
  (`getPointAtLength` from `@remotion/paths`).
- Cards alternate above and below the path, always clear of the stroke.

## Typography (shared)

- Display: a heavy geometric face (Poppins 800, Archivo Black) for titles and numerals.
- Body: Inter 400/600, 12.5 to 15 px on a 960 px width.
- Mono: JetBrains Mono 500 for paths, commands, tool names and uppercase kickers with
  `letterSpacing` 1.5 to 2.
- Load faces with `@remotion/google-fonts/<Face>`:
  `loadFont("normal", { weights: ["800"], subsets: ["latin"] })`.

## When the content does not fit the reference

If the reference shows five bands and the content has fifteen steps, group into five or six phases
and list the steps inside each card with their original numbers. Say so explicitly in the form
summary from step 1 of the workflow: "grouping N items into M blocks; every item stays listed".
