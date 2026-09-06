#!/usr/bin/env python3
"""to_gif.py - Convert a rendered MP4 into a looping GIF with a two-pass palette.

One shared palette (palettegen with stats_mode=diff) plus sierra2_4a dithering keeps
flat backgrounds clean and gradients banded rather than speckled, which is what an
infographic needs. Requires ffmpeg on PATH.

Usage:
  python3 scripts/to_gif.py out/video.mp4 out/video.gif
  python3 scripts/to_gif.py out/video.mp4 out/video.gif --width 720 --fps 12
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DITHERS = ("sierra2_4a", "bayer", "floyd_steinberg", "none")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", help="source MP4")
    ap.add_argument("output", help="destination GIF")
    ap.add_argument("--width", type=int, default=960, help="output width in px (height auto)")
    ap.add_argument("--fps", type=int, default=15, help="output frames per second")
    ap.add_argument("--max-colors", type=int, default=256, help="palette size (2-256)")
    ap.add_argument("--dither", default="sierra2_4a", choices=DITHERS, help="dithering algorithm")
    args = ap.parse_args()

    src, dst = Path(args.input), Path(args.output)
    if not src.is_file():
        print(f"ERROR: {src} not found", file=sys.stderr)
        return 2
    if not shutil.which("ffmpeg"):
        print("ERROR: ffmpeg not found on PATH", file=sys.stderr)
        return 2
    dst.parent.mkdir(parents=True, exist_ok=True)

    chain = (
        f"[0:v]fps={args.fps},scale={args.width}:-1:flags=lanczos,split[a][b];"
        f"[a]palettegen=max_colors={args.max_colors}:stats_mode=diff[p];"
        f"[b][p]paletteuse=dither={args.dither}"
    )
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
           "-filter_complex", chain, "-loop", "0", str(dst)]
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    size_mb = dst.stat().st_size / (1024 * 1024)
    print(f"{dst}  {size_mb:.1f} MB  ({args.width}px, {args.fps} fps, loop)")
    if size_mb > 15:
        print("Hint: over 15 MB. Try --width 720 or --fps 12 for sharing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
