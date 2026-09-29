"""Post-launch loop: turn platform analytics into a Bayesian winner call and next traffic split."""

from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Any

from . import specs

OBJECTIVES = {
    "hook_rate": ("views_3s", "impressions"),
    "completion": ("completions", "views_3s"),
    "share_rate": ("shares", "impressions"),
}
COUNT_FIELDS = ("impressions", "views_3s", "completions", "shares", "saves", "follows")


def load(path: Path) -> dict[str, dict[str, int]]:
    totals: dict[str, dict[str, int]] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            variant = (row.get("variant") or "").strip()
            if not variant:
                continue
            agg = totals.setdefault(variant, dict.fromkeys(COUNT_FIELDS, 0))
            for key in COUNT_FIELDS:
                raw = (row.get(key) or "0").strip().replace(",", "")
                agg[key] += max(0, int(float(raw or 0)))
    return totals


def evaluate(totals: dict[str, dict[str, int]], objective: str = "hook_rate", draws: int = 20000,
             seed: int = 7) -> dict[str, Any]:
    if objective not in OBJECTIVES:
        raise ValueError(f"objective must be one of {sorted(OBJECTIVES)}")
    num_key, den_key = OBJECTIVES[objective]
    rng = random.Random(seed)
    names = sorted(totals)
    params = []
    for n in names:
        den = totals[n][den_key]
        hits = min(totals[n][num_key], den)
        params.append((1 + hits, 1 + den - hits))
    wins = dict.fromkeys(names, 0)
    for _ in range(draws):
        samples = [rng.betavariate(a, b) for a, b in params]
        wins[names[max(range(len(names)), key=samples.__getitem__)]] += 1
    p_best = {n: round(wins[n] / draws, 4) for n in names}

    rows = {}
    for n in names:
        t = totals[n]
        imp, v3 = t["impressions"], t["views_3s"]
        rows[n] = {
            **t,
            "hook_rate": round(v3 / imp, 4) if imp else None,
            "completion": round(t["completions"] / v3, 4) if v3 else None,
            "shares_per_1k": round(1000 * t["shares"] / imp, 2) if imp else None,
            "p_best": p_best[n],
        }
    leader = max(names, key=p_best.__getitem__) if names else None
    thin = [n for n in names if totals[n]["impressions"] < specs.MIN_IMPRESSIONS]
    if not names:
        decision = "no data"
    elif thin:
        decision = f"keep testing: under {specs.MIN_IMPRESSIONS} impressions for {thin}"
    elif p_best[leader] >= specs.WIN_PROBABILITY:
        decision = f"ship {leader}: P(best {objective}) = {p_best[leader]:.1%}"
    else:
        decision = f"keep testing: leader {leader} at {p_best[leader]:.1%} < {specs.WIN_PROBABILITY:.0%}"
    return {"objective": objective, "variants": rows, "leader": leader, "decision": decision,
            "next_traffic_split": p_best}
