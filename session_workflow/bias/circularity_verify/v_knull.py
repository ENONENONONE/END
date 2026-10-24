"""Length-matched letter-sum nulls for (e4) and extra controls. Exact, no RNG."""
import json, os
from collections import Counter
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
D = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
P = 257
K = {0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120,
     128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256}
added = json.load(open(os.path.join(HERE, "v_added.json")))


def letters(w):
    return [ord(c) - 64 for c in w.upper() if 'A' <= c <= 'Z']


def freq_from(words):
    cnt = Counter(x for w in words for x in letters(w))
    tot = sum(cnt.values())
    return [cnt.get(i, 0) / tot for i in range(27)]  # index 0 unused


def sumdist(k, f, cache={}):
    key = (k, tuple(f))
    if key in cache:
        return cache[key]
    d = [0.0] * P
    d[0] = 1.0
    for _ in range(k):
        nd = [0.0] * P
        for r, pr in enumerate(d):
            if pr:
                for v in range(1, 27):
                    if f[v]:
                        nd[(r + v) % P] += pr * f[v]
        d = nd
    cache[key] = d
    return d


def poisbin_tail(ps, x):
    dp = [1.0]
    for p in ps:
        nd = [0.0] * (len(dp) + 1)
        for j, q in enumerate(dp):
            nd[j] += q * (1 - p)
            nd[j + 1] += q * p
        dp = nd
    mean = sum(ps)
    var = sum(p * (1 - p) for p in ps)
    return mean, var ** 0.5, sum(dp[x:])


pre = json.load(open(D + "emerald_tablet.pre-terminus-20260918.json"))
prewords = [w for v in pre.values() for w in v["words"]]
f_pre = freq_from(prewords)
f_add = freq_from([w for _, _, w in added])
f_unif = [0.0] + [1 / 26] * 26
obs = sum(1 for _, c, _ in added if c in K)
Kn0 = K - {0}
for label, f in [("pre-terminus letter freqs (investigator's e4)", f_pre),
                 ("added-words' own letter freqs", f_add),
                 ("uniform letters 1..26", f_unif)]:
    ps = [sum(sumdist(len(letters(w)), f)[c] for c in K) for _, _, w in added]
    m, sd, tail = poisbin_tail(ps, obs)
    print(f"{label}: expected {m:.3f} sd {sd:.3f} P(X>={obs}) = {tail:.4f}")
    for lab, sel in [("steps0-4", lambda s: s < 5), ("step5", lambda s: s == 5)]:
        idx = [i for i, (s, c, w) in enumerate(added) if sel(s)]
        o = sum(1 for i in idx if added[i][1] in K)
        m2, sd2, t2 = poisbin_tail([ps[i] for i in idx], o)
        print(f"    {lab}: obs {o}/{len(idx)} expected {m2:.3f} P(X>={o}) = {t2:.4f}")
