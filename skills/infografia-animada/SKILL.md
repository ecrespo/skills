---
name: infografia-animada
description: >
  Creates animated video infographics (MP4 + GIF) with Remotion from a reference image and
  caller-supplied content, using simple-icons for brand logos. Use whenever the user wants
  structured information (steps, phases, checklist, pipeline, timeline, decision tree, hub with
  branches) turned into a short animated piece: "animated infographic", "infografia animada",
  "video infographic", "animated poster", "vertical explainer", "animated carousel", "animate this
  infographic", or an existing static infographic (PNG, PDF, LinkedIn post) they want "in that style
  but animated". Also triggers when the content comes from an Obsidian note, a document or a list,
  when brand icons or a vertical/square format for Instagram, stories or a wiki are requested, even
  if Remotion, GIF or video are never mentioned. Takes precedence over generic Remotion or video
  skills when the result is an animated infographic. Not for voice-over videos, real footage, logo
  intros, banners, static infographics or slide decks.
---

# Animated infographics with Remotion

Turn a reference image plus the user's own content into a video infographic with staggered
entrances, self-drawing connector lines and a continuous dotted flow. The deliverables are an
MP4 and a GIF.

## Separation principle: form / content / palette / motion

These four inputs come from different places and must not be mixed:

| Source | What to take | What to ignore |
|---|---|---|
| Reference image | Only the **form**: structure type, how information is organised, typographic rhythm, layout, side alternation | Its texts, brands, figures and its colour palette |
| User content (text, Obsidian note, file) | All the **real text** | Nothing |
| Questions to the user | **Palette** and **which parts animate** | Nothing |
| This skill (`references/motion.md`) | The **motion methodology**, fixed | Nothing |

Mixing the reference image's content with the user's is the most common failure and the most
expensive to undo, because it contaminates every component.

## Workflow

### 1. Read the reference (form only)

Look at the image and classify the structure using `references/patterns.md`: numbered diagonal
bands, hub with branches, vertical list, decision tree, card grid, timeline. Note:

- how many nodes or steps the reference holds, and whether the real content fits or needs grouping,
- where the numeral, the title and the detail block sit, and whether they alternate sides,
- any illustrations: in the animated version they become detail cards or simple-icons logos, never
  copies of the original artwork.

Summarise the form in three or four lines for the user. That confirms the reference was read
correctly before any time goes into code.

### 2. Get the content

If the user names an Obsidian note, read it with the Obsidian tooling available in the session. If
they name a file, read the file. Count the content units (steps, nodes, items) and decide the
grouping: a 960x1280 canvas comfortably holds five to seven bands or six to eight nodes. With more
items, group them into phases and **list the individual items, numbered, inside each card**, each
with its own stagger. Users expect to find every item from their source; grouping without listing
them reads as lost content.

### 3. Ask before building

Ask in a single round of three or four questions. The full script and option presets live in
`references/questions.md`. The minimum:

1. **Palette**: background, ink, accent, cards, flow line, typography. Offer three presets plus a
   free-form option for the user's own hex values. Skip this if the palette is already in the request.
2. **What animates**: which elements get staggered entrances, whether connector lines carry the
   continuous flow, whether brand icons animate, whether backgrounds enter or stay fixed.
3. **Format**: 3:4 vertical 960x1280 (default), 9:16 1080x1920, 1:1 1080x1080, 16:9 1920x1080.
4. **Signature**: signature text (for example a handle) and its position.

Never re-ask what the user already specified; repeating settled decisions is irritating.

### 4. Set up the project

If a Remotion project already exists in the working folder, add a new composition to it instead of
creating a second project: the `npm install` is the bulk of the cost. Otherwise run
`scripts/setup_project.py`, which scaffolds a blank Remotion project, removes the Tailwind wiring
the blank template still ships, installs `@remotion/google-fonts`, `@remotion/paths` and
`simple-icons`, and copies the bundled templates.

Recommended layout under `src/<id>/`:

```
palette.ts     fixed palette (copy assets/templates/palette.ts and fill it in)
fonts.ts       Google Fonts loading (display / body / mono)
layout.ts      canvas, band or node geometry, and timing constants (appear frames)
content.ts     the real text, typed, no logic
useAppear.ts   entrance hook (assets/templates/useAppear.ts, unmodified)
FlowLine.tsx   self-drawing line plus continuous dotted flow (assets/templates/FlowLine.tsx)
Icon.tsx       animatable simple-icons logo (assets/templates/Icon.tsx)
<Pattern>.tsx  pattern components: Band, HubNode, Card, TimelineStep and so on
Lines.tsx      every connector line in one full-canvas SVG
Header.tsx / Footer.tsx
Infografia.tsx root composition
```

Register the composition in `src/Root.tsx` with the agreed dimensions and fps
(`assets/templates/Root.tsx` is a starting point). As a duration guide, entrances should finish by
roughly 60 percent of the runtime, leaving the rest with everything on screen and the flow running,
so a looping GIF never cuts mid-animation.

### 5. Motion methodology (fixed)

Read `references/motion.md` before writing components. In short:

- Every element enters through `useAppear(appearFrame)`: a spring (damping 200, mass 0.6) plus
  `interpolate` with clamped extrapolation for opacity, scale and translateY. Never instant, never
  linear.
- Stagger everything: large blocks every 24 to 28 frames, items inside a card every 4 to 5. Nothing
  arrives all at once.
- Lines draw themselves with `evolvePath` (stroke-dashoffset) and, once drawn, keep a `3 9` dotted
  pattern running with `strokeDashoffset = -((frame * 1.4) % 24)`. This continuous flow is what
  keeps the piece alive after the entrances land, so do not skip it.
- Icons enter through the same hook, with an optional gentle pulse or slow rotation when the user
  asked for it.

### 6. Brand icons with simple-icons

Read `references/icons.md`. The `simple-icons` package exports `siGithub`, `siDocker`, `siPython`
and around 3400 more, each with a `path` (24x24 viewBox) and a `hex`. The bundled `Icon.tsx`
template paints them in a palette colour rather than the brand hex, so eight logos cannot wreck a
three-tone palette. When a brand has no icon, fall back to a mono text chip: never approximate with
a different brand's logo and never substitute emoji.

### 7. Verify with a still before rendering video

Render one frame where everything is visible and the flow is running:

```bash
npx remotion still src/index.ts <CompositionId> out/preview.png --frame=<N>
```

Inspect it against this checklist before showing it:

- No line passes behind text with a transparent background. Lines run through gutters or stop at a
  card edge, and text cards always have solid backgrounds.
- Nothing overflows its card or band. The most frequent defect is chips wrapping to a second row:
  keep three or four chips per card, around 22 characters each, and give cards `minHeight` instead
  of a fixed `height`. Expect to fix this once and re-render the still.
- Every content item is present and identifiable.
- The signature is there.

Send the still to the user together with a small table of the chosen palette and format, and wait
for approval. A full render takes minutes and users would rather correct a picture than a video.

### 8. Final render and GIF

```bash
npx remotion render src/index.ts <CompositionId> out/<name>.mp4
python3 scripts/to_gif.py out/<name>.mp4 out/<name>.gif
```

`scripts/to_gif.py` runs the two-pass palette conversion with dithering and an infinite loop. A
960 px, 15 fps, 13 second GIF weighs around 8 MB; drop to 720 px or 12 fps when the user needs it
lighter. Deliver both files and their sizes.

## Pitfalls worth avoiding

- Copying text or brands from the reference image. Only its form carries over.
- Deriving the palette from the reference image when the user fixed one or is about to.
- CSS animation (`transition`, `animation`, Tailwind animation classes). Remotion renders frame by
  frame and ignores them; everything must derive from `useCurrentFrame()`.
- Letting motion stop once everything has entered. The dotted flow runs to the last frame.
- Rendering the full video before the user approved a still.
- Emoji as icons. Use simple-icons or text chips.

## Prerequisites

Node.js 18 or newer with `npx`, and `ffmpeg` on PATH for the GIF conversion. The first render also
downloads a headless Chrome build, which Remotion caches.
