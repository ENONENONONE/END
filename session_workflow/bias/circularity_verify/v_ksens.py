"""Sensitivity of (e): leave-one-K-cell-out; empirical length-matched null. Exact, no RNG."""
import json, os
from collections import Counter, defaultdict
from math import comb
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
D = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
P = 257
K = {0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120,
     128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256}
added = json.load(open(os.path.join(HERE, "v_added.json")))
L = lambda w: sum(1 for c in w.upper() if 'A' <= c <= 'Z')
S = lambda w: sum(ord(c) - 64 for c in w.upper() if 'A' <= c <= 'Z') % P
def btail(n, k, p):
    p = Fraction(p); return float(sum(comb(n, j) * p**j * (1-p)**(n-j) for j in range(k, n+1)))
def pb(ps, x):
    dp = [1.0]
    for p in ps:
        nd = [0.0]*(len(dp)+1)
        for j, q in enumerate(dp):
            nd[j] += q*(1-p); nd[j+1] += q*p
        dp = nd
    return sum(ps), sum(dp[x:])
n = len(added)
cnt = Counter(c for _, c, _ in added if c in K)
print("added per K cell:", sorted(cnt.items()))
rows = []
for c in sorted(K - {0}):
    K2 = K - {c}
    obs = sum(1 for _, cc, _ in added if cc in K2)
    rows.append((btail(n, obs, Fraction(len(K2 - {0}), 256)), c, obs))
rows.sort()
print("leave-one-out uniform P: min %.4f max %.4f" % (rows[0][0], rows[-1][0]))
print("  largest P when dropping:", rows[-3:])
# drop the two cells with most additions
for drop in [{128}, {46, 73, 128}, {119, 153, 138, 23}]:
    K2 = K - drop
    obs = sum(1 for _, cc, _ in added if cc in K2)
    print(f"  drop {sorted(drop)}: obs {obs}, expected {n*len(K2-{0})/256:.3f}, P {btail(n, obs, Fraction(len(K2-{0}),256)):.4f}")
# empirical length-matched null from pre-terminus letter-sum-placed words
pre = json.load(open(D + "emerald_tablet.pre-terminus-20260918.json"))
byk = defaultdict(lambda: [0, 0])
for c, v in pre.items():
    for w in v["words"]:
        if S(w) == int(c):
            byk[L(w)][1] += 1
            byk[L(w)][0] += int(c) in K
ps = []
for _, c, w in added:
    k = L(w)
    # pool neighbouring lengths if fewer than 20 words of that length
    ks = [k]; r = 0
    while sum(byk[j][1] for j in ks) < 20:
        r += 1; ks = [j for j in range(k-r, k+r+1) if j >= 1]
    a = sum(byk[j][0] for j in ks); b = sum(byk[j][1] for j in ks)
    ps.append(a/b)
obs = sum(1 for _, c, _ in added if c in K)
m, t = pb(ps, obs)
print(f"empirical length-matched (pre-terminus letter-sum words, lengths pooled to >=20): expected {m:.3f}, P(X>={obs}) {t:.4f}")
