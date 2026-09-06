# Motion methodology (fixed)

This methodology is part of the identity of the pieces. Do not change it for taste; only the user
may modify it, and when they do, apply the change across every component.

## 1. Entrance hook: `useAppear`

Copy `assets/templates/useAppear.ts` verbatim.

```ts
const { opacity, scale, translateY } = useAppear(appearFrame, 18);
// opacity: 0 to 1, linear, clamped over 18 frames
// scale: 0.86 to 1 and translateY: 14 to 0, both spring damping 200 / mass 0.6
```

Apply it in the element's `style`:

```tsx
style={{
  opacity,
  transform: `translateY(${translateY}px) scale(${scale})`,
  transformOrigin: "left center",
}}
```

`transformOrigin` matters. A right-aligned title should grow from the right ("right center"), a card
to the right of a numeral from its left edge, and so on. Without it, elements appear to slide into
place instead of settling.

For large backgrounds such as full-width bands, use only `opacity` and `translateY` from the hook:
scaling a 960 px polygon from 0.86 exposes gaps during the entrance.

## 2. Stagger

Nothing enters as a block. Cadences that work at 30 fps:

| Level | Separation |
|---|---|
| Large blocks (bands, hub satellites, grid cards) | 24 to 28 frames |
| Elements inside a block (numeral, title, card) | 4 to 6 frames |
| Items in a list inside a card | 4 to 5 frames |
| Header (kicker, title, subtitle) | 6 to 8 frames |

Centralise the appear frames in `layout.ts` (`bandAppear(k)`, `FOOTER_APPEAR` and friends) so
connector lines can synchronise with the nodes they join.

## 3. Lines: drawing plus continuous flow

Copy `assets/templates/FlowLine.tsx`. It takes an SVG path `d` and an `appearFrame`.

- Drawing: `evolvePath(progress, d)` from `@remotion/paths`, where `progress` comes from a spring
  (damping 200, mass 0.6, 24 frames). It returns `strokeDasharray` and `strokeDashoffset`.
- Flow: a second `<path>` on top with `strokeDasharray="3 9"` and
  `strokeDashoffset={-((frame * 1.4) % 24)}`. The period 24 is the pattern sum (3 + 9) times two, so
  the loop never jumps. Its opacity ramps from 0 to 1 between frames 20 and 34 after the appear.

Routing rules:

- A line connects nodes that have solid backgrounds (numeral badge, card, icon on a disc). Draw
  lines **below** the nodes so the anchor point stays hidden and clean.
- Lines run through gutters free of text. Where a crossing is unavoidable, that text must sit inside
  a card with a solid background.
- S-curves between alternating nodes: `M x y0 C x+w y0+60, x-w y1-60, x y1`, with `w` flipping sign.
  The real bulge is about 0.75 times `w`, which is what to budget for gutters.
- Put every line in a single full-canvas `<svg>` (`Lines.tsx`), above the backgrounds and below the
  HTML content.

## 4. Backgrounds with diagonal edges (band pattern)

One SVG polygon per band: boundary k runs from `(0, y_k + d_k)` to `(W, y_k - d_k)` with
`d_k = plus or minus 14`, alternating. Cards inside a band must fit within
`band_height - 2 * abs(d)`.

## 5. Duration

- Entrances complete at roughly 55 to 60 percent of the runtime.
- The remainder keeps everything visible with the flow running. For a looping GIF, leave at least
  four seconds in that state.
- 13 seconds (390 frames) suits six blocks; add about one second per extra block.

## 6. Forbidden

- `transition`, `animation`, `@keyframes`, Tailwind animation classes.
- `Math.random()` without a seed, or `Date.now()`: both break per-frame determinism.
- Linear entrances without a spring, and instant appearances.
