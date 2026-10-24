#!/usr/bin/env python3
"""(e) extra references for the K-cell count of the 129 added words, and the
review's 'the cell of W' constructions. Exact computations, no randomness.
 null 1: cells uniform over 1..256 (task spec): 129 × 32/256.
 null 2: cells distributed like the 1006 letter-sum-placed words already in the
         pre-terminus tablet (empirical cell frequencies).
 null 3: length-matched letter sums: for each added word of k letters, the
         exact distribution of the sum of k i.i.d. letters drawn with the letter
         frequencies of all 1129 pre-terminus tablet words, taken mod 257;
         expected count = Σ P(sum mod 257 ∈ K).
Also: 'cell of <WORD>' / 'that of <WORD>' constructions in the review and how
many name a word added in the window."""
import json, os, re
from collections import Counter
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
K = {0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119,
     120, 128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256}
P = 257
D = json.load(open(os.path.join(HERE, "diff_report.json")))
added = [(a["cell"], a["word"], a["letters"]) for st in D["steps"] for a in st["added"]]
pre = json.load(open(BASE + "emerald_tablet.pre-terminus-20260918.json"))
cur = json.load(open(BASE + "emerald_tablet.json"))


def lsum(w):
    return sum(ord(c) - 64 for c in w.upper() if "A" <= c <= "Z")


base = [(int(c), w) for c, v in pre.items() for w in v["words"]]
base_sp = [c for c, w in base if lsum(w) % P == c]
n = len(added)
obs = sum(1 for c, _, _ in added if c in K)

# null 2
f2 = sum(1 for c in base_sp if c in K) / len(base_sp)
exp2 = n * f2

# null 3
letters = Counter(ch for _, w in base for ch in w.upper() if "A" <= ch <= "Z")
tot = sum(letters.values())
pl = [0.0] * 27
for ch, c in letters.items():
    pl[ord(ch) - 64] = c / tot


def dist_mod(k):
    d = [0.0] * P
    d[0] = 1.0
    for _ in range(k):
        nd = [0.0] * P
        for s, ps in enumerate(d):
            if ps == 0:
                continue
            for v in range(1, 27):
                if pl[v]:
                    nd[(s + v) % P] += ps * pl[v]
        d = nd
    return d


cache = {}
exp3 = 0.0
var3 = 0.0
for c, w, k in added:
    if k not in cache:
        cache[k] = sum(dist_mod(k)[x] for x in K)
    exp3 += cache[k]
    var3 += cache[k] * (1 - cache[k])
# Poisson-binomial upper tail P(X >= obs) under null 3 (exact DP)
probs = [cache[k] for _, _, k in added]
dp = [1.0]
for p in probs:
    nd = [0.0] * (len(dp) + 1)
    for i, q in enumerate(dp):
        nd[i] += q * (1 - p)
        nd[i + 1] += q * p
    dp = nd
tail3 = sum(dp[obs:])
# binomial tail under null 2
tail2 = sum(comb(n, x) * f2**x * (1 - f2)**(n - x) for x in range(obs, n + 1))

# review: 'cell of W' constructions
S = json.load(open(os.path.join(HERE, "review_sentences.json")))
vocab = sorted({w for v in cur.values() for w in v["words"] if re.search(r"[A-Z]", w)}, key=lambda w: (-len(w), w))
alt = "|".join(re.escape(w) for w in vocab)
cp = re.compile(r"(?:the cells? of|that of)\s+(" + alt + r")(?![A-Za-z])")
added_words = {w for _, w, _ in added}
hits = []
for s in S:
    for m in cp.finditer(s["text"]):
        hits.append((s["i"], m.group(1)))
nwin = sum(1 for _, w in hits if w in added_words)
out = {
    "observed_in_K": obs, "n_added": n,
    "null1_uniform_1_256_expected": n * 32 / 256,
    "null2_baseline_sum_placed_words": len(base_sp),
    "null2_fraction_in_K": f2, "null2_expected": exp2, "null2_binom_tail_P(X>=obs)": tail2,
    "null3_expected": exp3, "null3_sd": var3 ** 0.5, "null3_poisson_binomial_tail_P(X>=obs)": tail3,
    "null3_P_inK_by_length": {str(k): v for k, v in sorted(cache.items())},
    "review_cell_of_constructions_total": len(hits),
    "review_cell_of_naming_window_added_word": nwin,
    "review_cell_of_window_words": [w for _, w in hits if w in added_words],
}
json.dump(out, open(os.path.join(HERE, "k_nulls.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
