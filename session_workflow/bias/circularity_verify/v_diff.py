"""Independent recompute of headlines a, a1-a7, b, b1, b2, d, d1, d2, e, e1-e5.
No random generator used."""
import json, os
from collections import Counter
from fractions import Fraction
from math import comb

D = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
ORDER = [
    ("pre-terminus", "emerald_tablet.pre-terminus-20260918.json"),
    ("pre-aim", "emerald_tablet.pre-aim-20260918.json"),
    ("pre-rotate", "emerald_tablet.pre-rotate-20260918.json"),
    ("pre-toth", "emerald_tablet.pre-toth-20260918.json"),
    ("pre-rongorongo", "emerald_tablet.pre-rongorongo-20260919.json"),
    ("pre-plate", "emerald_tablet.pre-plate-20260919.json"),
    ("current", "emerald_tablet.json"),
]
P = 257
K = {0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120,
     128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256}
assert len(K) == 33


def lsum(w):
    return sum(ord(c) - 64 for c in w.upper() if 'A' <= c <= 'Z')


def load(fn):
    d = json.load(open(D + fn))
    ms = Counter()
    for c, v in d.items():
        for w in v["words"]:
            ms[(int(c), w)] += 1
    return d, ms


vers = [(name,) + load(fn) for name, fn in ORDER]
out = []
p = out.append
for name, d, ms in vers:
    p(f"{name}: entries {sum(ms.values())}, distinct (cell,word) {len(ms)}, empty cells {sum(1 for v in d.values() if not v['words'])}")
    dup = [k for k, v in ms.items() if v > 1]
    if dup:
        p(f"   duplicate (cell,word) entries: {dup}")

added_all = []
removed_all = []
for i in range(len(vers) - 1):
    a, b = vers[i], vers[i + 1]
    add = b[2] - a[2]
    rem = a[2] - b[2]
    addl = sorted(add.elements(), key=lambda t: (t[0], t[1]))
    reml = sorted(rem.elements())
    added_all += [(i, c, w) for c, w in addl]
    removed_all += reml
    p(f"STEP {a[0]} -> {b[0]}: +{len(addl)} -{len(reml)}")
    p("   " + "; ".join(f"{w} {c}" for c, w in addl))
    if reml:
        p("   REMOVED: " + "; ".join(f"{w} {c}" for c, w in reml))
    # also check moves: word present in both but different cell
p(f"TOTAL added {len(added_all)} removed {len(removed_all)}")
# direct diff first vs last
first, last = vers[0][2], vers[-1][2]
p(f"direct pre-terminus->current: +{sum((last-first).values())} -{sum((first-last).values())}")

# (b) letter-sum placement
ls_ok = [(i, c, w) for i, c, w in added_all if lsum(w) % P == c]
p(f"(b) added at own letter sum: {len(ls_ok)}/{len(added_all)}")
for s in range(6):
    tot = [x for x in added_all if x[0] == s]
    ok = [x for x in tot if lsum(x[2]) % P == x[1]]
    p(f"   step {s}: {len(ok)}/{len(tot)}")
for name, d, ms in vers:
    tot = sum(ms.values())
    ok = sum(v for (c, w), v in ms.items() if lsum(w) % P == c)
    p(f"(b1) {name}: letter-sum placed {ok}/{tot} = {ok/tot:.4f}")

# a7: AIM, HERMES, I AM
for w in ["AIM", "HERMES", "I AM", "TOTH", "THOTH", "PYRAMIDUM"]:
    locs = [(name, sorted(c for (c, ww) in ms if ww == w)) for name, d, ms in vers]
    p(f"(a7) {w}: {locs}")

# (d)
cells_gained = sorted({c for _, c, _ in added_all})
d0, dN = vers[0][1], vers[-1][1]
net_inc = [c for c in cells_gained if len(dN[str(c)]["words"]) > len(d0[str(c)]["words"])]
p(f"(d) cells gained {len(cells_gained)}/257 = {len(cells_gained)/257:.4f}; net increase {len(net_inc)}")
n0, nN = sum(vers[0][2].values()), sum(vers[-1][2].values())
p(f"(d1) mean words/cell {n0/257:.4f} -> {nN/257:.4f}")
m0 = sum(len(d0[str(c)]["words"]) for c in cells_gained) / len(cells_gained)
m1 = sum(len(dN[str(c)]["words"]) for c in cells_gained) / len(cells_gained)
gain = Counter(c for _, c, _ in added_all)
p(f"(d2) gained cells mean {m0:.4f} -> {m1:.4f}; gain histogram {sorted(Counter(gain.values()).items())}; +4 cells {sorted(c for c,v in gain.items() if v==4)}")
# mean over non-gained cells, for reference
ng = [c for c in range(257) if c not in set(cells_gained)]
p(f"(d-extra) non-gained cells mean words {sum(len(d0[str(c)]['words']) for c in ng)/len(ng):.4f}")

# (e)
inK = [(i, c, w) for i, c, w in added_all if c in K]
p(f"(e) added in K: {len(inK)}; at 0: {sum(1 for x in added_all if x[1]==0)}")
n = len(added_all)


def binom_tail(n, k, pr):
    pr = Fraction(pr)
    return float(sum(comb(n, j) * pr**j * (1 - pr)**(n - j) for j in range(k, n + 1)))


exp_u = n * Fraction(32, 256)
p(f"   uniform 1..256 expected {float(exp_u):.4f}; ratio {len(inK)/float(exp_u):.4f}; P(X>={len(inK)}) = {binom_tail(n, len(inK), Fraction(32,256)):.4f}")
exp_u2 = n * Fraction(33, 257)
p(f"   uniform 0..256 (33/257) expected {float(exp_u2):.4f}; P = {binom_tail(n, len(inK), Fraction(33,257)):.4f}")
for s in range(6):
    tot = [x for x in added_all if x[0] == s]
    kk = [f"{w} {c}" for i, c, w in tot if c in K]
    p(f"(e1) step {s}: {len(kk)}/{len(tot)}: {kk}")
p(f"(e2) distinct K cells: {len({c for _,c,_ in inK})}: {sorted({c for _,c,_ in inK})}")
# e3
pre = vers[0][2]
lsw = [(c, w) for (c, w), v in pre.items() for _ in range(v) if lsum(w) % P == c]
lsk = sum(1 for c, w in lsw if c in K)
pr3 = Fraction(lsk, len(lsw))
p(f"(e3) letter-sum-placed pre-terminus in K {lsk}/{len(lsw)} = {float(pr3):.5f}; expected {float(n*pr3):.3f}; P(X>={len(inK)}) = {binom_tail(n, len(inK), pr3):.4f}")
# e5
tot0 = sum(pre.values())
k0 = sum(v for (c, w), v in pre.items() if c in K)
p(f"(e5) pre-terminus entries in K: {k0}/{tot0} = {k0/tot0:.4f}; K share of cells {33/257:.4f}")
# current tablet share
kN = sum(v for (c, w), v in vers[-1][2].items() if c in K)
p(f"(e5-extra) current entries in K: {kN}/{nN} = {kN/nN:.4f}")

open(os.path.join(os.path.dirname(__file__), "v_diff_out.txt"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
json.dump([[i, c, w] for i, c, w in added_all], open(os.path.join(os.path.dirname(__file__), "v_added.json"), "w"), ensure_ascii=False)
