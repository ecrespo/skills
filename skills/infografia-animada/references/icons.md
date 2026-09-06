# Brand icons with simple-icons

The `simple-icons` npm package ships around 3400 brand logos as SVG paths in a 24x24 viewBox. It is
this skill's icon source: no emoji, no downloaded PNGs.

## Install

```bash
npm i --save-exact simple-icons
```

`scripts/setup_project.py` already does this for new projects.

## API

```ts
import { siGithub, siDocker, siPython } from "simple-icons";
siGithub.path  // "M12 .297c-6.63 0-12 5.373..."
siGithub.hex   // "181717" (brand colour, no leading #)
siGithub.title // "GitHub"
```

Export names are `si` plus the title in PascalCase with no spaces or dots
(`siVisualstudiocode`, `siNextdotjs`, `siAmazonwebservices`). When unsure, look it up:

```bash
node -e "const s=require('simple-icons');console.log(Object.keys(s).filter(k=>/docker|kube/i.test(k)))"
```

## The `Icon.tsx` template

`assets/templates/Icon.tsx` renders one icon:

```tsx
<Icon icon={siDocker} size={40} color={palette.flow} appearFrame={base + 8} />
```

- It fills the `path` with a palette colour. Use the brand `hex` only when the user asks: mixing
  eight brand colours destroys a three-tone palette.
- It enters through `useAppear`. The optional `pulse` prop adds a gentle heartbeat
  (`scale` 1 plus or minus 0.03 driven by `Math.sin(frame / 12)`), useful in grids without lines.
- Wrap it in a solid-background container (disc or rounded square) when a connector line ends on it.

## When the icon does not exist

Internal brands, abstract concepts ("consistency", "evidence") and logo-less tools get a mono text
chip with a border, or a numeric badge. Never approximate with another brand's logo.
