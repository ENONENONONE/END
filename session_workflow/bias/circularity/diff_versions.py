#!/usr/bin/env python3
"""(a) (b) (d) (e): diff successive tablet versions, letter-sum placement,
cells that gained words, K-cell counts vs uniform expectation.
No randomness used (exact hypergeometric/binomial expectations)."""
import json, os, collections
from fractions import Fraction
from math import comb

BASE = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
OUT = os.path.dirname(os.path.abspath(__file__))
VERS = [
    ("pre-terminus", "emerald_tablet.pre-terminus-20260918.json"),
    ("pre-aim", "emerald_tablet.pre-aim-20260918.json"),
    ("pre-rotate", "emerald_tablet.pre-rotate-20260918.json"),
    ("pre-toth", "emerald_tablet.pre-toth-20260918.json"),
    ("pre-rongorongo", "emerald_tablet.pre-rongorongo-20260919.json"),
    ("pre-plate", "emerald_tablet.pre-plate-20260919.json"),
    ("current", "emerald_tablet.json"),
]
K = [0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119,
     120, 128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256]
assert len(K) == 33
KS = set(K)
P = 257


def lsum(w):
    return sum(ord(c) - 64 for c in w.upper() if "A" <= c <= "Z")


def nletters(w):
    return sum(1 for c in w.upper() if "A" <= c <= "Z")


def load(fn):
    d = json.load(open(BASE + fn))
    # multiset of (cell, word)
    ms = collections.Counter()
    for c, v in d.items():
        for w in v["words"]:
            ms[(int(c), w)] += 1
    return d, ms


tabs = [(name, *load(fn)) for name, fn in VERS]
report = {"steps": []}
all_added = []  # (step, cell, word)
all_removed = []
for (n0, d0, m0), (n1, d1, m1) in zip(tabs, tabs[1:]):
    added = m1 - m0
    removed = m0 - m1
    moved = []
    add_list = sorted(((c, w) for (c, w), k in added.items() for _ in range(k)))
    rem_list = sorted(((c, w) for (c, w), k in removed.items() for _ in range(k)))
    tot0 = sum(m0.values()); tot1 = sum(m1.values())
    step = {"from": n0, "to": n1, "total_from": tot0, "total_to": tot1,
            "added_count": len(add_list), "removed_count": len(rem_list),
            "added": [{"cell": c, "word": w, "letter_sum_mod257": lsum(w) % P,
                       "letters": nletters(w),
                       "sum_placed": (lsum(w) % P == c)} for c, w in add_list],
            "removed": [{"cell": c, "word": w} for c, w in rem_list]}
    report["steps"].append(step)
    for c, w in add_list:
        all_added.append((f"{n0}->{n1}", c, w))
    for c, w in rem_list:
        all_removed.append((f"{n0}->{n1}", c, w))

# (b) letter-sum placement
nb = len(all_added)
placed = [a for a in all_added if lsum(a[2]) % P == a[1]]
notplaced = [a for a in all_added if lsum(a[2]) % P != a[1]]
report["b"] = {"added_total": nb, "sum_placed": len(placed),
               "not_sum_placed": len(notplaced),
               "fraction": f"{len(placed)}/{nb}",
               "fraction_float": len(placed) / nb if nb else None,
               "not_sum_placed_list": [{"step": s, "cell": c, "word": w,
                                        "sum_mod257": lsum(w) % P} for s, c, w in notplaced]}
# per-step placement
report["b"]["per_step"] = [
    {"step": f"{s['from']}->{s['to']}", "added": s["added_count"],
     "sum_placed": sum(1 for a in s["added"] if a["sum_placed"])}
    for s in report["steps"]]

# baseline: placement fraction of the 1129 words present at pre-terminus
d0 = tabs[0][1]
base_words = [(int(c), w) for c, v in d0.items() for w in v["words"]]
base_placed = sum(1 for c, w in base_words if lsum(w) % P == c)
report["b"]["baseline_pre_terminus"] = {"words": len(base_words), "sum_placed": base_placed,
                                        "fraction_float": base_placed / len(base_words)}
dcur = tabs[-1][1]
cur_words = [(int(c), w) for c, v in dcur.items() for w in v["words"]]
cur_placed = sum(1 for c, w in cur_words if lsum(w) % P == c)
report["b"]["current"] = {"words": len(cur_words), "sum_placed": cur_placed,
                          "fraction_float": cur_placed / len(cur_words)}

# (d) cells that gained at least one word over the window
dfirst, mfirst = tabs[0][1], tabs[0][2]
dlast, mlast = tabs[-1][1], tabs[-1][2]
gained_cells = sorted({c for _, c, _ in all_added})
net_gain_cells = sorted(c for c in range(P)
                        if len(dlast[str(c)]["words"]) > len(dfirst[str(c)]["words"]))
report["d"] = {
    "cells_gained_any_added_word": len(gained_cells),
    "fraction_of_257": len(gained_cells) / P,
    "cells_with_net_count_increase": len(net_gain_cells),
    "mean_words_per_cell_before": len(base_words) / P,
    "mean_words_per_cell_after": len(cur_words) / P,
    "gained_cells": gained_cells,
    "words_per_gained_cell": dict(collections.Counter(c for _, c, _ in all_added)),
}
# mean words per cell among gained cells before/after
report["d"]["gained_cells_mean_before"] = sum(len(dfirst[str(c)]["words"]) for c in gained_cells) / len(gained_cells)
report["d"]["gained_cells_mean_after"] = sum(len(dlast[str(c)]["words"]) for c in gained_cells) / len(gained_cells)
# empty cells before/after
report["d"]["empty_cells_before"] = sum(1 for c in range(P) if not dfirst[str(c)]["words"])
report["d"]["empty_cells_after"] = sum(1 for c in range(P) if not dlast[str(c)]["words"])

# (e) added words in K cells vs uniform over 1..256
inK = [a for a in all_added if a[1] in KS]
K_nonzero = len(KS - {0})  # 32 of 1..256
exp_uniform_1_256 = Fraction(nb * K_nonzero, 256)
exp_uniform_0_256 = Fraction(nb * len(KS), 257)
# binomial tail P(X >= observed) under p = 32/256
p = Fraction(K_nonzero, 256)
obs = len(inK)
tail = sum(Fraction(comb(nb, x)) * p**x * (1 - p)**(nb - x) for x in range(obs, nb + 1))
# distinct K cells receiving additions
report["e"] = {
    "added_total": nb, "added_in_K": obs,
    "added_in_K_nonzero": sum(1 for a in inK if a[1] != 0),
    "expected_uniform_1_256": float(exp_uniform_1_256),
    "expected_uniform_1_256_exact": str(exp_uniform_1_256),
    "expected_uniform_0_256": float(exp_uniform_0_256),
    "ratio_obs_to_exp_1_256": float(Fraction(obs) / exp_uniform_1_256),
    "binomial_upper_tail_P(X>=obs)_p=32/256": float(tail),
    "distinct_K_cells_receiving": len({a[1] for a in inK}),
    "in_K_list": [{"step": s, "cell": c, "word": w} for s, c, w in inK],
    "baseline_pre_terminus_words_in_K": sum(1 for c, w in base_words if c in KS),
    "baseline_pre_terminus_fraction_in_K": sum(1 for c, w in base_words if c in KS) / len(base_words),
    "K_fraction_of_257": len(KS) / 257,
}
# K-cell additions per step
report["e"]["per_step"] = [
    {"step": f"{s['from']}->{s['to']}", "added": s["added_count"],
     "in_K": sum(1 for a in s["added"] if a["cell"] in KS)} for s in report["steps"]]
# restricted to sum-placed additions (their cell = their sum)
sp_inK = [a for a in placed if a[1] in KS]
report["e"]["sum_placed_added_in_K"] = len(sp_inK)
report["e"]["sum_placed_expected_1_256"] = len(placed) * K_nonzero / 256

report["removed_total"] = len(all_removed)
report["removed"] = [{"step": s, "cell": c, "word": w} for s, c, w in all_removed]

json.dump(report, open(os.path.join(OUT, "diff_report.json"), "w"), indent=1, ensure_ascii=False)

# human-readable
lines = []
for s in report["steps"]:
    lines.append(f"== {s['from']} ({s['total_from']}) -> {s['to']} ({s['total_to']}): +{s['added_count']} -{s['removed_count']}")
    for a in s["added"]:
        lines.append(f"   + {a['cell']:3d}  {a['word']}  (sum mod 257 = {a['letter_sum_mod257']}, {'placed' if a['sum_placed'] else 'NOT sum-placed'})")
    for r in s["removed"]:
        lines.append(f"   - {r['cell']:3d}  {r['word']}")
open(os.path.join(OUT, "diff_steps.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
print()
for k in ("b", "d", "e"):
    print(k, json.dumps({kk: vv for kk, vv in report[k].items() if not isinstance(vv, list) or len(vv) < 40}, ensure_ascii=False, indent=1))
