#!/usr/bin/env python3
"""git_history.py — Mine a git repository's history into feature clusters and eras.

Outputs:
  <outdir>/history.json  — machine-readable analysis (clusters, eras, hotspots)
  <outdir>/history.md    — human-readable summary for curation

Pure stdlib. Read-only: never mutates the repository.

Usage:
  python3 git_history.py /path/to/repo -o /path/to/outdir [--max-commits N]
                         [--since YYYY-MM-DD] [--until YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

FIELD_SEP = "\x1f"
REC_SEP = "\x1e"

CONVENTIONAL_RE = re.compile(
    r"^(?P<type>feat|fix|refactor|perf|docs|test|tests|chore|build|ci|style|revert)"
    r"(?:\((?P<scope>[^)]*)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$",
    re.IGNORECASE,
)

# Fallback keyword heuristics for non-conventional messages.
TYPE_KEYWORDS = [
    ("fix", re.compile(r"\b(fix|bug|hotfix|patch|corrig|arregl|solucion|repar)", re.I)),
    ("feat", re.compile(r"\b(add|feat|implement|new|create|agreg|a\u00f1ad|nuev|implement|cre)", re.I)),
    ("refactor", re.compile(r"\b(refactor|clean|rework|reorganiz|renombr|rename|restructur)", re.I)),
    ("docs", re.compile(r"\b(doc|readme|comment)", re.I)),
    ("test", re.compile(r"\b(test|spec|prueba|cobertura|coverage)", re.I)),
    ("chore", re.compile(r"\b(bump|upgrade|update dep|dependenc|version|release|merge|lint|format)", re.I)),
]

NOISE_TYPES = {"chore", "style", "ci", "build", "docs"}
GENERIC_SCOPES = {"core", "misc", "src", "app", "main", "general", "all", "repo", "project"}


def run_git(repo: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo)] + args,
        capture_output=True, text=True, check=True,
    )
    return result.stdout


def classify(subject: str) -> tuple[str, str | None, bool]:
    """Return (type, scope, is_conventional)."""
    m = CONVENTIONAL_RE.match(subject.strip())
    if m:
        return m.group("type").lower(), (m.group("scope") or None), True
    for ctype, pattern in TYPE_KEYWORDS:
        if pattern.search(subject):
            return ctype, None, False
    return "other", None, False


def dominant_dir(files: list[str]) -> str | None:
    """Dominant top-level (or second-level for src/ style layouts) directory."""
    counts: Counter[str] = Counter()
    for f in files:
        parts = Path(f).parts
        if not parts:
            continue
        if len(parts) == 1:
            counts["(root)"] += 1
        elif parts[0] in {"src", "app", "lib", "packages", "apps", "services"} and len(parts) > 2:
            counts[f"{parts[0]}/{parts[1]}"] += 1
        else:
            counts[parts[0]] += 1
    if not counts:
        return None
    return counts.most_common(1)[0][0]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", type=Path)
    ap.add_argument("-o", "--outdir", type=Path, required=True)
    ap.add_argument("--max-commits", type=int, default=5000)
    ap.add_argument("--since", default=None)
    ap.add_argument("--until", default=None)
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not (repo / ".git").exists():
        print(f"ERROR: {repo} is not a git repository (no .git). "
              "The evolution/user-story phases need the real repo, not an export.", file=sys.stderr)
        return 2

    log_args = [
        "log", "--no-merges", "--numstat", "--date=short",
        f"--max-count={args.max_commits}",
        f"--pretty=format:{REC_SEP}%H{FIELD_SEP}%h{FIELD_SEP}%ad{FIELD_SEP}%an{FIELD_SEP}%s",
    ]
    if args.since:
        log_args.append(f"--since={args.since}")
    if args.until:
        log_args.append(f"--until={args.until}")

    raw = run_git(repo, log_args)

    commits = []
    for record in raw.split(REC_SEP):
        record = record.strip("\n")
        if not record.strip():
            continue
        lines = record.split("\n")
        header = lines[0].split(FIELD_SEP)
        if len(header) != 5:
            continue
        full, short, date, author, subject = header
        files, added, deleted = [], 0, 0
        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            a, d, path = parts
            files.append(path)
            if a.isdigit():
                added += int(a)
            if d.isdigit():
                deleted += int(d)
        ctype, scope, conventional = classify(subject)
        commits.append({
            "hash": full, "short": short, "date": date, "author": author,
            "subject": subject, "type": ctype, "scope": scope,
            "conventional": conventional, "files": files,
            "added": added, "deleted": deleted,
        })

    commits.sort(key=lambda c: c["date"])  # oldest first

    # ---- Clusters: scope if useful, else dominant directory ----
    clusters: dict[str, list[dict]] = defaultdict(list)
    for c in commits:
        scope = (c["scope"] or "").strip().lower()
        if scope and scope not in GENERIC_SCOPES:
            key = f"scope:{scope}"
        else:
            dom = dominant_dir(c["files"])
            key = f"dir:{dom}" if dom else f"type:{c['type']}"
        clusters[key].append(c)

    cluster_list = []
    for key, cs in clusters.items():
        types = Counter(c["type"] for c in cs)
        noise = all(c["type"] in NOISE_TYPES for c in cs)
        cluster_list.append({
            "cluster": key,
            "commits": len(cs),
            "first": cs[0]["date"], "last": cs[-1]["date"],
            "churn": sum(c["added"] + c["deleted"] for c in cs),
            "types": dict(types),
            "probable_noise": noise,
            "hashes": [c["short"] for c in cs],
            "subjects_sample": [c["subject"] for c in cs[:8]],
        })
    cluster_list.sort(key=lambda x: (-x["commits"], x["first"]))

    # ---- Eras: by tags if any, else by quarter ----
    tags_raw = run_git(repo, [
        "tag", "--sort=creatordate",
        "--format=%(refname:short)\t%(creatordate:short)",
    ]).strip()
    tags = []
    for line in tags_raw.splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and parts[1]:
            tags.append({"tag": parts[0], "date": parts[1]})

    eras = []
    if tags:
        boundaries = [{"label": t["tag"], "end": t["date"]} for t in tags]
        boundaries.append({"label": "(no release / HEAD)", "end": "9999-99-99"})
        idx = 0
        bucket: list[dict] = []
        for c in commits:
            while c["date"] > boundaries[idx]["end"]:
                if bucket:
                    eras.append(_era(boundaries[idx]["label"], bucket))
                bucket = []
                idx += 1
            bucket.append(c)
        if bucket:
            eras.append(_era(boundaries[idx]["label"], bucket))
    else:
        by_quarter: dict[str, list[dict]] = defaultdict(list)
        for c in commits:
            y, m, _ = c["date"].split("-")
            q = (int(m) - 1) // 3 + 1
            by_quarter[f"{y}-Q{q}"].append(c)
        for label in sorted(by_quarter):
            eras.append(_era(label, by_quarter[label]))

    # ---- Hotspots & fix-prone files ----
    file_touches: Counter[str] = Counter()
    file_fixes: Counter[str] = Counter()
    for c in commits:
        for f in c["files"]:
            file_touches[f] += 1
            if c["type"] == "fix":
                file_fixes[f] += 1

    authors = Counter(c["author"] for c in commits)
    conventional_pct = (
        round(100 * sum(1 for c in commits if c["conventional"]) / len(commits), 1)
        if commits else 0.0
    )

    analysis = {
        "repo": str(repo),
        "total_commits_analyzed": len(commits),
        "date_range": [commits[0]["date"], commits[-1]["date"]] if commits else None,
        "conventional_commit_pct": conventional_pct,
        "authors": authors.most_common(),
        "tags": tags,
        "eras": eras,
        "clusters": cluster_list,
        "hotspots": file_touches.most_common(20),
        "fix_prone_files": [(f, n) for f, n in file_fixes.most_common(20) if n >= 2],
        "commits": commits,
    }

    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "history.json").write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    (args.outdir / "history.md").write_text(render_md(analysis), encoding="utf-8")
    print(f"OK: {len(commits)} commits → {len(cluster_list)} clusters, "
          f"{len(eras)} eras. Written to {args.outdir}/history.{{json,md}}")
    return 0


def _era(label: str, cs: list[dict]) -> dict:
    types = Counter(c["type"] for c in cs)
    return {
        "label": label,
        "from": cs[0]["date"], "to": cs[-1]["date"],
        "commits": len(cs), "types": dict(types),
        "top_subjects": [c["subject"] for c in sorted(
            cs, key=lambda x: -(x["added"] + x["deleted"]))[:5]],
        "hash_range": [cs[0]["short"], cs[-1]["short"]],
    }


def render_md(a: dict) -> str:
    lines = ["# Git history analysis", ""]
    if a["date_range"]:
        lines.append(f"**Repo:** `{a['repo']}` · **Commits:** {a['total_commits_analyzed']} "
                     f"({a['date_range'][0]} → {a['date_range'][1]}) · "
                     f"**Conventional commits:** {a['conventional_commit_pct']}%")
    lines += ["", "## Eras (basis for 03-EVOLUTION.md)", "",
              "| Era | From | To | Commits | Dominant types |",
              "|---|---|---|---|---|"]
    for e in a["eras"]:
        top_types = ", ".join(f"{k}:{v}" for k, v in
                              sorted(e["types"].items(), key=lambda x: -x[1])[:3])
        lines.append(f"| {e['label']} | {e['from']} | {e['to']} | {e['commits']} | {top_types} |")

    lines += ["", "## Feature clusters (basis for the user stories — CURATE before using)", ""]
    for cl in a["clusters"]:
        noise = " ⚠️ probable noise (do not generate a user story)" if cl["probable_noise"] else ""
        lines.append(f"### `{cl['cluster']}` — {cl['commits']} commits, "
                     f"churn {cl['churn']}{noise}")
        lines.append(f"*{cl['first']} → {cl['last']}* · hashes: "
                     f"`{cl['hashes'][0]}`…`{cl['hashes'][-1]}`")
        for s in cl["subjects_sample"]:
            lines.append(f"- {s}")
        lines.append("")

    lines += ["## Hotspots (most-touched files)", "",
              "| File | Touches |", "|---|---|"]
    for f, n in a["hotspots"][:15]:
        lines.append(f"| `{f}` | {n} |")

    if a["fix_prone_files"]:
        lines += ["", "## Files with recurring fixes (candidates for acceptance "
                      "criteria and for v2 redesign)", "",
                  "| File | Fix commits |", "|---|---|"]
        for f, n in a["fix_prone_files"]:
            lines.append(f"| `{f}` | {n} |")

    lines += ["", "## Authors", ""]
    for name, n in a["authors"]:
        lines.append(f"- {name}: {n} commits")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
