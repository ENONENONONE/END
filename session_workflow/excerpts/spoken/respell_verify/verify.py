#!/usr/bin/env python3
"""Independent recomputation of TEST 2 (phonetic respellings).
Written from the task definitions only. Seeds are stated at each use.
"""
import re, json, collections, statistics, math, sys
import numpy as np

SP = "<scratchpad>"
DICT = SP + "/cmu/cmudict.dict"
OUT = SP + "/spoken/respell_verify/"

P, G = 257, 3
# ---------- field tables ----------
DLOG3 = [None] * P
x = 1
for k in range(256):
    DLOG3[x] = k
    x = x * G % P
assert all(DLOG3[n] is not None for n in range(1, P))
DLOG5 = [None] * P
x = 1
for k in range(256):
    DLOG5[x] = k
    x = x * 5 % P
assert all(DLOG5[n] is not None for n in range(1, P))

def inv(n): return pow(n, 255, P)
def char(n): return None if n == 0 else DLOG3[n] % 2   # 0 = QR, 1 = QNR
def ring(n):
    if n == 0: return None
    d = DLOG5[n] % 64
    return min(d, 64 - d)
for n in range(1, P):   # equivalence stated in the task
    e = 7 * DLOG3[n] % 64
    assert ring(n) == min(e, 64 - e)

def gamma(x):
    if x == 137: return None
    return (x - 120) * inv((x + 120) % P) % P

REL_NAMES = ["sq", "neg", "inv", "x2", "half", "x17", "x5", "x3", "gamma"]
def rel_image(name, x):
    if name == "sq": return x * x % P
    if name == "neg": return (-x) % P
    if name == "inv": return None if x == 0 else inv(x)
    if name == "x2": return 2 * x % P
    if name == "half": return 129 * x % P
    if name == "x17": return 17 * x % P
    if name == "x5": return 5 * x % P
    if name == "x3": return 3 * x % P
    if name == "gamma": return gamma(x)

# REL[r][x][y] True if relation r holds x->y or y->x
REL = {}
for r in REL_NAMES:
    M = np.zeros((P, P), dtype=bool)
    for a in range(P):
        y = rel_image(r, a)
        if y is not None:
            M[a, y] = True
            M[y, a] = True
    REL[r] = M
LINK_REL = np.zeros((P, P), dtype=bool)
for r in REL_NAMES: LINK_REL |= REL[r]
LINK = LINK_REL.copy()
for a in range(P): LINK[a, a] = True

K = {0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120,
     128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256}
assert len(K) == 33
INK = np.array([n in K for n in range(P)])
CHAR = np.array([-1 if n == 0 else DLOG3[n] % 2 for n in range(P)])
RING = np.array([-1 if n == 0 else ring(n) for n in range(P)])

# ---------- respelling schemes (fixed tables) ----------
SCHEME_P = {"AA": "O", "AE": "A", "AH": "U", "AO": "AW", "AW": "OW", "AY": "AI", "EH": "E",
            "ER": "ER", "EY": "AY", "IH": "I", "IY": "EE", "OW": "OH", "OY": "OY", "UH": "OO",
            "UW": "OO", "B": "B", "CH": "CH", "D": "D", "DH": "TH", "F": "F", "G": "G", "HH": "H",
            "JH": "J", "K": "K", "L": "L", "M": "M", "N": "N", "NG": "NG", "P": "P", "R": "R",
            "S": "S", "SH": "SH", "T": "T", "TH": "TH", "V": "V", "W": "W", "Y": "Y", "Z": "Z",
            "ZH": "ZH"}
VOWELS = ["AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"]
SCHEME_M = {}
for ph, sp in SCHEME_P.items():
    if ph in VOWELS:
        SCHEME_M[ph] = sp[0]
    else:
        SCHEME_M[ph] = sp
SCHEME_M.update({"CH": "C", "DH": "D", "NG": "N", "SH": "S", "TH": "T", "ZH": "Z", "JH": "J", "HH": "H"})
assert all(len(v) == 1 for v in SCHEME_M.values())

def respell(phones, scheme):
    return "".join(scheme[re.sub(r"\d", "", ph)] for ph in phones)

def triple(word):
    letters = [ord(c) - 64 for c in word.upper() if "A" <= c <= "Z"]
    k = len(letters); s = sum(letters); b = sum((i + 1) * v for i, v in enumerate(letters))
    return k, s, b

# ---------- parse ----------
lines = open(DICT, encoding="utf-8").read().splitlines()
n_lines = len(lines)
pat = re.compile(r"^([a-z]+)(\((\d+)\))?$")
entries = collections.defaultdict(dict)   # word -> {variant_index: phones}
skip_apos = skip_other = 0
for ln in lines:
    ln = ln.split("#")[0].strip()
    if not ln: continue
    parts = ln.split()
    hw, phones = parts[0], parts[1:]
    if "'" in hw:
        skip_apos += 1; continue
    m = pat.match(hw)
    if not m:
        skip_other += 1; continue
    w = m.group(1); v = int(m.group(3)) if m.group(3) else 1
    entries[w][v] = phones
words = sorted(entries)
n_variant_words = sum(1 for w in words if len(entries[w]) > 1)
no_base = [w for w in words if 1 not in entries[w]]
first = {w: entries[w][min(entries[w])] for w in words}

res = {"data": {"lines": n_lines, "headwords": len(words), "skip_apostrophe": skip_apos,
                "skip_other_nonalpha": skip_other, "headwords_with_variants": n_variant_words,
                "headwords_without_unmarked_entry": no_base}}

# ---------- per-word arrays ----------
N = len(words)
A = np.zeros(N, dtype=np.int64); SA = np.zeros(N, dtype=np.int64); LA = np.zeros(N, dtype=np.int64)
RS = {}
for sch_name, sch in (("P", SCHEME_P), ("M", SCHEME_M)):
    B = np.zeros(N, dtype=np.int64); SB = np.zeros(N, dtype=np.int64); LB = np.zeros(N, dtype=np.int64)
    ident = np.zeros(N, dtype=bool); anag = np.zeros(N, dtype=bool); strs = []
    for i, w in enumerate(words):
        k, s, b = triple(w)
        A[i] = s % P; SA[i] = s; LA[i] = k
        r = respell(first[w], sch)
        strs.append(r)
        k2, s2, b2 = triple(r)
        B[i] = s2 % P; SB[i] = s2; LB[i] = k2
        ident[i] = (r == w.upper())
        anag[i] = (sorted(r) == sorted(w.upper()))
    RS[sch_name] = dict(B=B, SB=SB, LB=LB, ident=ident, anag=anag, strs=strs)

res["zero_cells"] = {"spelled": [words[i] for i in np.where(A == 0)[0]],
                     "P": [words[i] for i in np.where(RS["P"]["B"] == 0)[0]],
                     "M": [words[i] for i in np.where(RS["M"]["B"] == 0)[0]]}

def metrics(a, b):
    """a, b integer arrays of cells. returns dict metric -> (num, den)."""
    nz = (a != 0) & (b != 0)
    m1 = int(np.sum((CHAR[a] == CHAR[b]) & nz)); d12 = int(np.sum(nz))
    m2 = int(np.sum((RING[a] == RING[b]) & nz))
    m3 = int(np.sum(LINK[a, b])); m4 = int(np.sum(INK[b])); m5 = int(np.sum(a == b))
    n = len(a)
    return {"m1": (m1, d12), "m2": (m2, d12), "m3": (m3, n), "m4": (m4, n), "m5": (m5, n),
            "m3_rel_excl_eq": (int(np.sum(LINK_REL[a, b] & (a != b))), n)}

def rel_breakdown(a, b, excl_eq=False):
    msk = (a != b) if excl_eq else np.ones(len(a), dtype=bool)
    return {r: int(np.sum(REL[r][a, b] & msk)) for r in REL_NAMES}

def draw_partners(idx, keyL, keyR, rng):
    """For each word in idx, pick a random OTHER word from idx with the same (keyL, keyR).
    returns (self_idx, partner_idx) for words that have a partner."""
    strata = collections.defaultdict(list)
    for i in idx:
        strata[(int(keyL[i]), int(keyR[i]))].append(i)
    selfs, parts = [], []
    for key in sorted(strata):
        mem = np.array(strata[key])
        n = len(mem)
        if n < 2: continue
        u = rng.integers(0, n - 1, size=n)
        pos = np.arange(n)
        u = np.where(u >= pos, u + 1, u)
        selfs.append(mem); parts.append(mem[u])
    return np.concatenate(selfs), np.concatenate(parts)

def z(obs_rate, ctl_rate, n):
    se = math.sqrt(ctl_rate * (1 - ctl_rate) / n)
    return (obs_rate - ctl_rate) / se if se > 0 else float("nan")

def run_condition(sch, subset_mask, seeds, extra_draws_seed=None, n_extra=0):
    R = RS[sch]; B = R["B"]
    idx = np.where(subset_mask)[0]
    obs = metrics(A[idx], B[idx])
    obs_rel = rel_breakdown(A[idx], B[idx]); obs_rel_ne = rel_breakdown(A[idx], B[idx], True)
    ctl = []; ctl_rel = []; ctl_rel_ne = []; npairs = []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        s_, p_ = draw_partners(idx, LA, R["LB"], rng)
        ctl.append(metrics(A[s_], B[p_])); ctl_rel.append(rel_breakdown(A[s_], B[p_]))
        ctl_rel_ne.append(rel_breakdown(A[s_], B[p_], True)); npairs.append(len(s_))
    out = {"n": len(idx), "control_pairs_per_draw": npairs, "seeds": list(seeds), "metrics": {}}
    for m in ["m1", "m2", "m3", "m4", "m5", "m3_rel_excl_eq"]:
        num, den = obs[m]; rate = num / den
        crates = [c[m][0] / c[m][1] for c in ctl]
        cm = float(np.mean(crates))
        out["metrics"][m] = {"obs": [num, den, round(rate, 5)], "ctl_mean": round(cm, 5),
                             "ctl_range": [round(min(crates), 5), round(max(crates), 5)],
                             "z": round(z(rate, cm, den), 2)}
    out["rel_obs"] = obs_rel; out["rel_obs_excl_eq"] = obs_rel_ne
    out["rel_ctl_mean"] = {r: float(np.mean([c[r] for c in ctl_rel])) for r in REL_NAMES}
    out["rel_ctl_mean_excl_eq"] = {r: float(np.mean([c[r] for c in ctl_rel_ne])) for r in REL_NAMES}
    if n_extra:
        rng = np.random.default_rng(extra_draws_seed)
        rates = collections.defaultdict(list)
        for _ in range(n_extra):
            s_, p_ = draw_partners(idx, LA, R["LB"], rng)
            mm = metrics(A[s_], B[p_])
            for m in mm: rates[m].append(mm[m][0] / mm[m][1])
        out["extra_draws"] = {"seed": extra_draws_seed, "n": n_extra,
                              "per_metric": {m: {"mean": round(float(np.mean(v)), 5),
                                                  "sd": round(float(np.std(v, ddof=1)), 5),
                                                  "min": round(float(np.min(v)), 5),
                                                  "max": round(float(np.max(v)), 5)}
                                             for m, v in rates.items()}}
    # folded distance
    d_obs = np.minimum((A[idx] - B[idx]) % P, (B[idx] - A[idx]) % P)
    out["folded_distance_obs"] = {"median": float(np.median(d_obs)), "share_le10": round(float(np.mean(d_obs <= 10)), 5)}
    return out

allmask = np.ones(N, dtype=bool)
res["A_ident"] = {s: [int(RS[s]["ident"].sum()), N, round(RS[s]["ident"].sum() / N, 5)] for s in "PM"}
res["anagram_nonident"] = {s: int((RS[s]["anag"] & ~RS[s]["ident"]).sum()) for s in "PM"}

res["A_P_ALL"] = run_condition("P", allmask, [7001, 7002, 7003, 7004, 7005], 7100, 100)
res["A_P_NONID"] = run_condition("P", ~RS["P"]["ident"], [7011, 7012, 7013, 7014, 7015], 7110, 100)
res["A_M_ALL"] = run_condition("M", allmask, [7021, 7022, 7023, 7024, 7025], 7120, 100)
res["A_M_NONID"] = run_condition("M", ~RS["M"]["ident"], [7031, 7032, 7033, 7034, 7035], 7130, 100)
# stricter: exclude identical AND anagram respellings (same letter multiset -> same sum by construction)
res["A_P_NONANAG"] = run_condition("P", ~RS["P"]["anag"], [7041, 7042, 7043, 7044, 7045], 7140, 100)
res["A_M_NONANAG"] = run_condition("M", ~RS["M"]["anag"], [7051, 7052, 7053, 7054, 7055], 7150, 100)

# ---------- difference-preserving control (extra) ----------
# B' = A + D_j where D_j = SB_j - SA_j of a random other word in the same (spelled len, respelled len) stratum.
def diff_control(sch, subset_mask, seeds):
    R = RS[sch]; idx = np.where(subset_mask)[0]
    D = R["SB"] - SA
    outs = []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        s_, p_ = draw_partners(idx, LA, R["LB"], rng)
        a = A[s_]; b = (SA[s_] + D[p_]) % P
        mm = metrics(a, b)
        outs.append({m: mm[m][0] / mm[m][1] for m in mm})
    obs = metrics(A[idx], R["B"][idx])
    return {m: {"obs": round(obs[m][0] / obs[m][1], 5),
                "ctl_mean": round(float(np.mean([o[m] for o in outs])), 5),
                "ctl_range": [round(min(o[m] for o in outs), 5), round(max(o[m] for o in outs), 5)],
                "z": round(z(obs[m][0] / obs[m][1], float(np.mean([o[m] for o in outs])), obs[m][1]), 2)}
            for m in obs}
res["DIFFCTL_P_NONID"] = diff_control("P", ~RS["P"]["ident"], list(range(7201, 7211)))
res["DIFFCTL_M_NONID"] = diff_control("M", ~RS["M"]["ident"], list(range(7211, 7221)))
res["DIFFCTL_P_ALL"] = diff_control("P", allmask, list(range(7221, 7231)))
res["DIFFCTL_M_ALL"] = diff_control("M", allmask, list(range(7231, 7241)))

# ---------- (d) differences ----------
for s in "PM":
    D = (SA - RS[s]["SB"])
    c = collections.Counter(D.tolist())
    ni = ~RS[s]["ident"]
    cni = collections.Counter(D[ni].tolist())
    res["D_" + s] = {"mean": round(float(D.mean()), 3), "median": float(np.median(D)),
                     "sd_pop": round(float(D.std()), 3), "sd_sample": round(float(D.std(ddof=1)), 3),
                     "min": int(D.min()), "max": int(D.max()),
                     "top15": [(v, n, round(n / N, 5)) for v, n in c.most_common(15)],
                     "top5_nonident": [(v, n, round(n / int(ni.sum()), 5)) for v, n in cni.most_common(5)]}

# ---------- (c) the hi family ----------
fam_any = []; fam_first = []; fam_loose = []; fam_contains = []
for w in words:
    for v, ph in sorted(entries[w].items()):
        bare = [re.sub(r"\d", "", p) for p in ph]
        if ph == ["HH", "AY1"]:
            fam_any.append((w, v))
            if v == min(entries[w]): fam_first.append(w)
        if bare == ["HH", "AY"]:
            fam_loose.append((w, v, " ".join(ph)))
        if len(bare) > 2 and any(bare[i:i + 2] == ["HH", "AY"] for i in range(len(bare) - 1)):
            fam_contains.append((w, v))
def cellinfo(n):
    return {"cell": n, "dlog3": DLOG3[n] if n else None, "char": ("QR" if DLOG3[n] % 2 == 0 else "QNR") if n else None,
            "ring": ring(n) if n else None, "inK": n in K}
fam = {"exact_HH_AY1_any_pron": fam_any, "exact_first_pron": fam_first,
       "HH_AY_any_stress": fam_loose, "n_containing_HH_AY_longer": len(fam_contains),
       "cells": {w: dict(triple=triple(w), **cellinfo(triple(w)[1] % P)) for w, _, _ in fam_loose}}
fam["P"] = dict(str=respell(["HH", "AY1"], SCHEME_P), triple=triple(respell(["HH", "AY1"], SCHEME_P)))
fam["M"] = dict(str=respell(["HH", "AY1"], SCHEME_M), triple=triple(respell(["HH", "AY1"], SCHEME_M)))
fam["P"].update(cellinfo(fam["P"]["triple"][1] % P)); fam["M"].update(cellinfo(fam["M"]["triple"][1] % P))
# pairwise links
members5 = [w for w, v in fam_any]
links = []
cells = {w: triple(w)[1] % P for w in members5}
cells["hye"] = triple("hye")[1] % P
allm = members5 + ["hye"]
for i in range(len(allm)):
    for j in range(i + 1, len(allm)):
        a, b = cells[allm[i]], cells[allm[j]]
        rs = [r for r in REL_NAMES if REL[r][a, b]]
        if rs or a == b: links.append((allm[i], allm[j], a, b, rs, a == b))
    for sch in "PM":
        b = fam[sch]["triple"][1] % P; a = cells[allm[i]]
        rs = [r for r in REL_NAMES if REL[r][a, b]]
        if rs or a == b: links.append((allm[i], "resp" + sch, a, b, rs, a == b))
fam["links"] = links

def fam_metrics(cellsA, cellsB_list=None):
    """ordered pairs among cellsA (i != j) if cellsB_list None; else member i vs B."""
    if cellsB_list is None:
        a = np.array([x for i, x in enumerate(cellsA) for j, y in enumerate(cellsA) if i != j])
        b = np.array([y for i, x in enumerate(cellsA) for j, y in enumerate(cellsA) if i != j])
    else:
        a = np.array(cellsA); b = np.array(cellsB_list)
    return metrics(a, b)

by_len = collections.defaultdict(list)
by_len2 = collections.defaultdict(list)
for i, w in enumerate(words):
    by_len[int(LA[i])].append(i)
for s in "PM":
    for i, w in enumerate(words):
        by_len2[(s, int(LA[i]), int(RS[s]["LB"][i]))].append(i)

def fam_control(members, seed, ndraw=10000):
    rng = np.random.default_rng(seed)
    famset = set(allm)
    obs_ss = fam_metrics([cells[w] for w in members])
    outs = {"ss": collections.defaultdict(list), "P": collections.defaultdict(list), "M": collections.defaultdict(list)}
    pools = {w: [i for i in by_len[len(w)] if words[i] not in famset] for w in members}
    poolsR = {(s, w): [i for i in by_len2[(s, len(w), fam[s]["triple"][0])] if words[i] not in famset]
              for s in "PM" for w in members}
    for _ in range(ndraw):
        pick = [pools[w][rng.integers(len(pools[w]))] for w in members]
        mm = fam_metrics([int(A[i]) for i in pick])
        for m in mm: outs["ss"][m].append(mm[m][0] / mm[m][1] if mm[m][1] else float("nan"))
        for s in "PM":
            pickR = [poolsR[(s, w)][rng.integers(len(poolsR[(s, w)]))] for w in members]
            mm = fam_metrics([cells[w] for w in members], [int(RS[s]["B"][i]) for i in pickR])
            for m in mm: outs[s][m].append(mm[m][0] / mm[m][1] if mm[m][1] else float("nan"))
    obs = {"ss": obs_ss,
           "P": fam_metrics([cells[w] for w in members], [fam["P"]["triple"][1] % P] * len(members)),
           "M": fam_metrics([cells[w] for w in members], [fam["M"]["triple"][1] % P] * len(members))}
    rep = {}
    for key in ("ss", "P", "M"):
        rep[key] = {}
        for m in ("m1", "m2", "m3", "m4", "m5"):
            v = np.array(outs[key][m]); o = obs[key][m][0] / obs[key][m][1]
            rep[key][m] = {"obs": obs[key][m], "ctl_mean": round(float(np.nanmean(v)), 5),
                           "share_ge_obs": round(float(np.mean(v >= o - 1e-12)), 4),
                           "share_eq_obs": round(float(np.mean(np.abs(v - o) < 1e-12)), 4)}
    return rep
fam["control_5"] = fam_control(members5, 7300)
fam["control_4"] = fam_control(fam_first, 7310)
res["C"] = fam

# ---------- example checks ----------
ex = {}
for w in ["hi", "high", "heye", "hy", "jai", "ghost", "psalm", "island", "knight", "write", "gnome", "hour", "debt",
          "listen", "colonel", "wednesday", "jaskulski", "selley", "reissman", "kaboom", "schmaltz", "rechargeable",
          "counterterrorists"]:
    if w not in entries: ex[w] = None; continue
    ex[w] = {"spelled": triple(w), "P": (RS["P"]["strs"][words.index(w)], triple(RS["P"]["strs"][words.index(w)])),
             "M": (RS["M"]["strs"][words.index(w)], triple(RS["M"]["strs"][words.index(w)]))}
res["examples"] = ex

json.dump(res, open(OUT + "verify_results.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str)[:60000])
