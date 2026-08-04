#!/usr/bin/env python3
"""arch_signals.py — Architecture signals mined from git history.

Detects: hotspots (churn × fixes), fix-prone files, temporal coupling (files that
change together — especially ACROSS module boundaries), knowledge concentration
(bus factor) per module.

Outputs: <outdir>/arch_signals.json, <outdir>/arch_signals.md
Pure stdlib, read-only.

Usage:
  python3 arch_signals.py /path/to/repo -o /path/to/outdir [--max-commits N]
                          [--min-cochanges N] [--min-confidence F]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

FIELD_SEP = "\x1f"
REC_SEP = "\x1e"
SRC_ROOTS = {"src", "app", "lib", "packages", "apps", "services"}
# Also matches Spanish fix-commit verbs (corrig-, arregl-, solucion-, repar-)
FIX_RE = re.compile(r"^fix[(:!]|\b(fix|bug|hotfix|corrig|arregl|solucion|repar)", re.I)
NOISE_FILE_RE = re.compile(
    r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|uv\.lock|"
    r"go\.sum|Cargo\.lock|.*\.snap|.*\.min\.js)$")


def module_of(path: str, depth: int = 2) -> str:
    parts = Path(path).parts
    if len(parts) == 1:
        return "(root)"
    if parts[0] in SRC_ROOTS and len(parts) > 2:
        return "/".join(parts[:min(depth + 1, len(parts) - 1)])
    return "/".join(parts[:min(depth, len(parts) - 1)])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", type=Path)
    ap.add_argument("-o", "--outdir", type=Path, required=True)
    ap.add_argument("--max-commits", type=int, default=1000)
    ap.add_argument("--min-cochanges", type=int, default=3,
                    help="minimum joint commits to report a pair (default 3)")
    ap.add_argument("--min-confidence", type=float, default=0.5,
                    help="minimum pair confidence (default 0.5)")
    ap.add_argument("--max-files-per-commit", type=int, default=20,
                    help="ignore massive commits for co-change (default 20)")
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not (repo / ".git").exists():
        print(f"ERROR: {repo} is not a git repository (no .git). History-based "
              "signals need the real repo.", file=sys.stderr)
        return 2

    raw = subprocess.run(
        ["git", "-C", str(repo), "log", "--no-merges", "--numstat", "--date=short",
         f"--max-count={args.max_commits}",
         f"--pretty=format:{REC_SEP}%h{FIELD_SEP}%ad{FIELD_SEP}%an{FIELD_SEP}%s"],
        capture_output=True, text=True, check=True).stdout

    commits = []
    for record in raw.split(REC_SEP):
        record = record.strip("\n")
        if not record.strip():
            continue
        lines = record.split("\n")
        header = lines[0].split(FIELD_SEP)
        if len(header) != 4:
            continue
        short, date, author, subject = header
        cfiles, churn = [], {}
        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            a, d, path = parts
            if NOISE_FILE_RE.search(path):
                continue
            cfiles.append(path)
            churn[path] = (int(a) if a.isdigit() else 0) + (int(d) if d.isdigit() else 0)
        commits.append({"hash": short, "date": date, "author": author,
                        "subject": subject, "is_fix": bool(FIX_RE.search(subject)),
                        "files": cfiles, "churn": churn})

    # ---- Per-file signals ----
    touches: Counter[str] = Counter()
    fixes: Counter[str] = Counter()
    churn_total: Counter[str] = Counter()
    for c in commits:
        for f in c["files"]:
            touches[f] += 1
            churn_total[f] += c["churn"].get(f, 0)
            if c["is_fix"]:
                fixes[f] += 1

    # hotspot score = touches × (1 + fixes) — files both busy and buggy rank first
    hotspots = sorted(
        ({"file": f, "touches": n, "fixes": fixes[f], "churn": churn_total[f],
          "score": n * (1 + fixes[f])} for f, n in touches.items()),
        key=lambda x: -x["score"])[:25]

    # ---- Temporal coupling (co-change pairs) ----
    pair_count: Counter[tuple[str, str]] = Counter()
    for c in commits:
        fs = [f for f in c["files"] if touches[f] >= 2]
        if 2 <= len(fs) <= args.max_files_per_commit:
            for a, b in combinations(sorted(set(fs)), 2):
                pair_count[(a, b)] += 1

    pairs = []
    for (a, b), n in pair_count.items():
        if n < args.min_cochanges:
            continue
        conf = n / min(touches[a], touches[b])
        if conf < args.min_confidence:
            continue
        ma, mb = module_of(a), module_of(b)
        pairs.append({"file_a": a, "file_b": b, "cochanges": n,
                      "confidence": round(conf, 2),
                      "cross_module": ma != mb, "module_a": ma, "module_b": mb})
    pairs.sort(key=lambda p: (-p["cross_module"], -p["cochanges"], -p["confidence"]))
    cross_pairs = [p for p in pairs if p["cross_module"]]

    # ---- Knowledge concentration per module ----
    mod_authors: dict[str, Counter] = defaultdict(Counter)
    for c in commits:
        seen_mods = {module_of(f) for f in c["files"]}
        for m in seen_mods:
            mod_authors[m][c["author"]] += 1
    bus_factor = []
    for m, authors in mod_authors.items():
        total = sum(authors.values())
        top_author, top_n = authors.most_common(1)[0]
        pct = round(100 * top_n / total, 1)
        bus_factor.append({"module": m, "commits": total, "authors": len(authors),
                           "top_author": top_author, "top_author_pct": pct})
    bus_factor.sort(key=lambda x: (-x["top_author_pct"], -x["commits"]))

    result = {
        "repo": str(repo),
        "commits_analyzed": len(commits),
        "date_range": ([commits[-1]["date"], commits[0]["date"]] if commits else None),
        "hotspots": hotspots,
        "fix_prone_files": [{"file": f, "fixes": n} for f, n in fixes.most_common(20)
                            if n >= 2],
        "temporal_coupling_pairs": pairs[:40],
        "cross_module_pairs": len(cross_pairs),
        "bus_factor_by_module": bus_factor[:20],
        "params": {"max_commits": args.max_commits,
                   "min_cochanges": args.min_cochanges,
                   "min_confidence": args.min_confidence},
    }

    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "arch_signals.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    (args.outdir / "arch_signals.md").write_text(render_md(result), encoding="utf-8")
    print(f"OK: {len(commits)} commits → {len(hotspots)} hotspots, "
          f"{len(pairs)} co-change pairs ({len(cross_pairs)} cross modules). "
          f"→ {args.outdir}/arch_signals.{{json,md}}")
    return 0


def render_md(r: dict) -> str:
    lines = ["# Architecture signals from git", ""]
    if r["date_range"]:
        lines.append(f"**Repo:** `{r['repo']}` · {r['commits_analyzed']} commits "
                     f"({r['date_range'][0]} → {r['date_range'][1]})")
    lines += ["", "## 🔴 Temporal coupling across modules — P1 evidence", "",
              "Pairs of files in different modules that change together: the boundary "
              "between those modules is fictitious or leaky.", ""]
    cross = [p for p in r["temporal_coupling_pairs"] if p["cross_module"]]
    if cross:
        lines += ["| File A | File B | Co-changes | Confidence |", "|---|---|---|---|"]
        for p in cross[:15]:
            lines.append(f"| `{p['file_a']}` | `{p['file_b']}` | {p['cochanges']} "
                         f"| {p['confidence']} |")
    else:
        lines.append("✅ No significant cross-module pairs "
                     "(threshold: ≥{} co-changes, confidence ≥{}).".format(
                         r["params"]["min_cochanges"], r["params"]["min_confidence"]))

    same = [p for p in r["temporal_coupling_pairs"] if not p["cross_module"]]
    if same:
        lines += ["", "## Intra-module temporal coupling (context)", "",
                  "| File A | File B | Co-changes | Confidence |", "|---|---|---|---|"]
        for p in same[:10]:
            lines.append(f"| `{p['file_a']}` | `{p['file_b']}` | {p['cochanges']} "
                         f"| {p['confidence']} |")

    lines += ["", "## Hotspots (touches × (1+fixes))", "",
              "| File | Touches | Fixes | Churn | Score |", "|---|---|---|---|---|"]
    for h in r["hotspots"][:15]:
        lines.append(f"| `{h['file']}` | {h['touches']} | {h['fixes']} "
                     f"| {h['churn']} | {h['score']} |")

    if r["fix_prone_files"]:
        lines += ["", "## Files with recurring fixes", "",
                  "| File | Fixes |", "|---|---|"]
        for f in r["fix_prone_files"]:
            lines.append(f"| `{f['file']}` | {f['fixes']} |")

    lines += ["", "## Knowledge concentration per module (bus factor)", "",
              "| Module | Commits | Authors | Dominant author | % |", "|---|---|---|---|---|"]
    for b in r["bus_factor_by_module"][:12]:
        flag = " ⚠️" if b["top_author_pct"] >= 90 and b["commits"] >= 10 else ""
        lines.append(f"| `{b['module']}` | {b['commits']} | {b['authors']} "
                     f"| {b['top_author']} | {b['top_author_pct']}%{flag} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
