#!/usr/bin/env python3
"""Independent recomputation of the look-elsewhere exercise (a)-(e).
Written from the shared definitions only. No random generator in this file (exact enumeration)."""
import json, re, math
from collections import Counter
from fractions import Fraction as F

P = 257
ROOT = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
VL = "<scratchpad>/vl/"
OUT = {}

# ---------- field helpers ----------
DL = {}
x = 1
for k in range(256):
    DL[x] = k
    x = x * 3 % P
assert len(DL) == 256
inv = lambda n: pow(n, P - 2, P)
ROOTS = {n: [] for n in range(P)}
for m in range(1, P):
    ROOTS[m * m % P].append(m)
ROOTS[0] = [0]

def gamma(n):
    d = (n + 120) % P
    if d == 0:
        return None  # infinity
    return (n - 120) * inv(d) % P

def readings(n, with_zero_rules=True):
    """list of (name, value) for cell n, n itself NOT included"""
    r = [("fold", (P - n) % P)]
    if n != 0:
        r.append(("inverse", inv(n)))
    r.append(("square", n * n % P))
    if n != 0:
        for i, m in enumerate(sorted(ROOTS[n])):
            r.append(("sqrt", m))
    else:
        r.append(("sqrt", 0))
    r.append(("double", 2 * n % P))
    r.append(("half", 129 * n % P))
    g = gamma(n)
    if g is not None:
        r.append(("gamma", g))
    r.append(("x17", 17 * n % P))
    r.append(("x5", 5 * n % P))
    r.append(("x3", 3 * n % P))
    if n != 0:
        r.append(("dlog3", DL[n]))
    return r

K33 = [0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120,
       128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256]
K12 = [1, 8, 16, 23, 44, 46, 62, 72, 73, 120, 136, 137]
assert len(K33) == 33 and len(set(K33)) == 33 and len(K12) == 12

def part_ab(K, tag):
    Ks = set(K)
    counts = {}
    byread = Counter()
    nread = 0
    for n in range(1, P):
        c = 0
        for name, v in readings(n):
            nread += 1
            if v in Ks:
                c += 1
                byread[name] += 1
        counts[n] = c
    tot = sum(counts.values())
    none = [n for n in range(1, P) if counts[n] == 0]
    hist = Counter(counts.values())
    inside = [n for n in range(1, P) if n in Ks]
    outside = [n for n in range(1, P) if n not in Ks]
    q = len(Ks) / P
    npr = [len(readings(n)) for n in range(1, P)]
    base_mean = sum(npr) / 256 * q
    base_one = sum(1 - (1 - q) ** m for m in npr) / 256
    res = dict(
        total_readings=nread, total_landings=tot, mean=tot / 256, mean_frac=str(F(tot, 256)),
        at_least_one=f"{256-len(none)}/256 = {(256-len(none))/256:.4f}",
        n_none_count=len(none), n_none=none, none_in_K=[n for n in none if n in Ks],
        hist=dict(sorted(hist.items())), max=max(counts.values()),
        argmax=[n for n in counts if counts[n] == max(counts.values())],
        by_reading=dict(byread),
        outside_mean=sum(counts[n] for n in outside) / len(outside),
        outside_n=len(outside),
        outside_one=f"{sum(1 for n in outside if counts[n])}/{len(outside)} = {sum(1 for n in outside if counts[n])/len(outside):.4f}",
        inside_mean=sum(counts[n] for n in inside) / len(inside), inside_n=len(inside),
        baseline_mean=round(base_mean, 4), baseline_one=round(base_one, 4),
        residues_in_K_nonzero=sum(1 for k in Ks if k and len(ROOTS[k]) == 2),
    )
    OUT[tag] = res
    return counts

cA = part_ab(K33, "a_K33")
cB = part_ab(K12, "b_K12")
OUT["a_n1_detail"] = [(nm, v, v in set(K33)) for nm, v in readings(1)]

# ---------- (c) pairs ----------
def part_c(K, tag):
    Ks = set(K)
    any6 = any6_neq = 0
    perop = Counter()
    s01 = s01_neq = 0
    for a in range(1, P):
        ia = inv(a)
        for b in range(1, P):
            ib = inv(b)
            vals = {"a+b": (a + b) % P, "a-b": (a - b) % P, "b-a": (b - a) % P,
                    "a*b": a * b % P, "a/b": a * ib % P, "b/a": b * ia % P}
            hit = False
            for kname, v in vals.items():
                if v in Ks:
                    perop[kname] += 1
                    hit = True
            if hit:
                any6 += 1
                if a != b:
                    any6_neq += 1
            if (a + b) % P in (256, 0, 1):
                s01 += 1
                if a != b:
                    s01_neq += 1
    OUT[tag] = dict(any6=f"{any6}/65536 = {any6/65536:.4f}", any6_neq=f"{any6_neq}/65280 = {any6_neq/65280:.4f}",
                    per_op=dict(perop), sum_256_0_1=f"{s01}/65536 = {s01/65536:.4f}",
                    sum_256_0_1_neq=f"{s01_neq}/65280",
                    baseline_indep6=round(1 - (1 - len(Ks) / P) ** 6, 4))

part_c(K33, "c_K33")
part_c(K12, "c_K12")

# ---------- (d) tablet words ----------
T = json.load(open(ROOT + "emerald_tablet.json", encoding="utf-8"))
entries = []
nonascii = []
for pos in sorted(T, key=int):
    for w in T[pos]["words"]:
        vals = [ord(ch) - 64 for ch in w.upper() if "A" <= ch <= "Z"]
        if any(ch.isalpha() and not ("A" <= ch.upper() <= "Z") for ch in w):
            nonascii.append((pos, w))
        k = len(vals)
        s = sum(vals)
        entries.append((int(pos), w, k, s))

def part_d(K, tag):
    Ks = set(K)
    n_hit = cell_in = mir_in = only_R = 0
    uniq = {}
    for pos, w, k, s in entries:
        c = s % P
        mir = (27 * k - s) % P
        rv = [v for _, v in readings(c)]
        hit_cell = c in Ks
        hit_mir = mir in Ks
        hit_R = any(v in Ks for v in rv)
        h = hit_cell or hit_mir or hit_R
        n_hit += h
        cell_in += hit_cell
        mir_in += hit_mir
        only_R += (hit_R and not hit_cell and not hit_mir)
        uniq[w] = h
    N = len(entries)
    OUT[tag] = dict(frac=f"{n_hit}/{N} = {n_hit/N:.4f}",
                    unique=f"{sum(uniq.values())}/{len(uniq)} = {sum(uniq.values())/len(uniq):.4f}",
                    cell_in=f"{cell_in}/{N} = {cell_in/N:.4f}", mirror_in=f"{mir_in}/{N} = {mir_in/N:.4f}",
                    only_R=f"{only_R}/{N} = {only_R/N:.4f}")
    # reference: cells 0..256, cell itself or any R reading
    ref = sum(1 for c in range(P) if c in Ks or any(v in Ks for _, v in readings(c)))
    OUT[tag]["ref_cells_no_mirror"] = f"{ref}/257 = {ref/257:.4f}"
    # words without the mirror (cell + R only)
    nm = sum(1 for pos, w, k, s in entries if (s % P) in Ks or any(v in Ks for _, v in readings(s % P)))
    OUT[tag]["words_no_mirror"] = f"{nm}/{N} = {nm/N:.4f}"

part_d(K33, "d_K33")
part_d(K12, "d_K12")
OUT["d_census"] = dict(entries=len(entries), unique=len({w for _, w, _, _ in entries}),
                       no_letters=sum(1 for e in entries if e[2] == 0),
                       cell_eq_pos=sum(1 for pos, w, k, s in entries if s % P == pos),
                       nonascii_alpha=nonascii[:20], nonascii_count=len(nonascii))
cellcount = Counter(s % P for _, _, _, s in entries)
OUT["d_words_at_K33_cells"] = sum(cellcount[c] for c in K33)

# ---------- (e)(i) Poisson ----------
def pois_pmf(lam, x):
    return math.exp(-lam + x * math.log(lam) - math.lgamma(x + 1))

def pois_outside(lam, z=1.8, inclusive_boundary=False):
    sd = math.sqrt(lam)
    lo, hi = lam - z * sd, lam + z * sd
    p = 0.0
    for x in range(0, 400):
        if inclusive_boundary:
            out = x <= lo + 1e-12 or x >= hi - 1e-12
        else:
            out = x < lo - 1e-12 or x > hi + 1e-12
        if out:
            p += pois_pmf(lam, x)
    return p, lo, hi

def binom_tail(n, p, k):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))

ei = {}
for lab, lam in (("lam25", 25.0), ("lam_obs", 5351 / 257)):
    p, lo, hi = pois_outside(lam)
    pb, _, _ = pois_outside(lam, inclusive_boundary=True)
    ei[lab] = dict(lam=round(lam, 4), band=(round(lo, 3), round(hi, 3)), p=round(p, 4), exp14=round(14 * p, 4),
                   P_ge1=round(binom_tail(14, p, 1), 4), P_ge2=round(binom_tail(14, p, 2), 4),
                   p_boundary_in=round(pb, 4), exp14_boundary=round(14 * pb, 4))
pn = math.erfc(1.8 / math.sqrt(2))
ei["normal"] = dict(p=round(pn, 5), exp14=round(14 * pn, 4), P_ge1=round(1 - (1 - pn) ** 14, 4))

# own Voynich parser (from the stated conventions, not voy.py)
def voy_lines(path):
    out = []
    for raw in open(path, encoding="ascii", errors="replace"):
        line = raw.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        m = re.match(r"^<(f\w+)\.(\w+),([^>]*)>\s*(.*)$", line)
        if not m:
            continue
        txt = m.group(4)
        txt = re.sub(r"<![^>]*>", "", txt)          # comments
        txt = re.sub(r"<[^>]*>", ".", txt)          # other tags break words
        txt = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", txt)  # alternatives: first
        txt = re.sub(r"@\d+;", "?", txt)
        txt = txt.replace("{", "").replace("}", "").replace("'", "")
        txt = txt.replace(",", "")                   # commas join
        toks = [t for t in txt.split(".") if t and re.fullmatch("[a-z]+", t)]
        out.append((m.group(1), m.group(2), toks))
    return out

VLINES = voy_lines(VL + "ZL3b-n.txt")
sums = [sum(ord(c) - 96 for t in toks for c in t) for _, _, toks in VLINES if toks]
nlines = len(sums)
cells = Counter(s % P for s in sums)
lam = nlines / P
counts = [cells[c] for c in range(P)]
mean_c = sum(counts) / P
var_c = sum((x - mean_c) ** 2 for x in counts) / P
var_c1 = sum((x - mean_c) ** 2 for x in counts) / (P - 1)
sd = math.sqrt(lam)
out_cells = [c for c in range(P) if abs(cells[c] - lam) > 1.8 * sd]
p_obs, _, _ = pois_outside(lam)
targets = [0, 1, 23, 44, 46, 62, 72, 73, 86, 92, 120, 136, 137, 256]
tz = {c: (cells[c], round((cells[c] - lam) / sd, 2)) for c in targets}
n_out_t = sum(1 for c in targets if abs(cells[c] - lam) > 1.8 * sd)
srt = sorted(sums)
ei["voynich"] = dict(lines_total_parsed=len(VLINES), lines_with_clean=nlines, lam=round(lam, 4),
                     n_cells_outside=len(out_cells), expected_outside=round(257 * p_obs, 2),
                     dispersion_pop=round(var_c / mean_c, 3), var_pop=round(var_c, 2), dispersion_samp=round(var_c1 / mean_c, 3),
                     min_count=min(counts), max_count=max(counts),
                     sum_min=srt[0], sum_median=(srt[nlines // 2] if nlines % 2 else (srt[nlines // 2 - 1] + srt[nlines // 2]) / 2),
                     sum_mean=round(sum(sums) / nlines, 2), sum_max=srt[-1], below257=sum(1 for s in sums if s < 257),
                     targets=tz, targets_outside=n_out_t,
                     obs_rate_exp14=round(14 * len(out_cells) / 257, 4),
                     obs_rate_P_ge6=round(binom_tail(14, len(out_cells) / 257, 6), 4))
OUT["e_i"] = ei
json.dump(sums, open(VL.replace("vl/", "bias/lookelsewhere_verify/") + "voynich_line_sums.json", "w"))

# ---------- (e)(ii) ----------
p2 = 88 / 360
OUT["e_ii"] = dict(p=round(p2, 4), expected=round(21 * p2, 4),
                   **{f"P_ge{k}": round(binom_tail(21, p2, k), 4) for k in (5, 6, 7, 8, 9, 10)})
# coverage of 22 windows at G_n = 2.5*(55n mod 144), two index conventions
for lab, rng in (("n0_21", range(0, 22)), ("n1_22", range(1, 23))):
    cen = sorted(2.5 * (55 * n % 144) for n in rng)
    gaps = [(cen[(i + 1) % 22] - cen[i]) % 360 for i in range(22)]
    OUT["e_ii"]["coverage_" + lab] = dict(min_gap_deg=min(gaps), covered_deg=sum(min(4.0, g) for g in gaps),
                                         centres_below_180=sum(1 for c in cen if c < 180))

# ---------- (e)(iii) ----------
q = 2 / 1301
OUT["e_iii"] = dict(per=round(q, 5), P_ge1=round(1 - (1 - q) ** 30, 4), exp=round(30 * q, 4),
                    P_ge2=round(binom_tail(30, q, 2), 6))
v0 = [v for v in range(200, 1501) if v % P in (0, 256)]
vK = [v for v in range(200, 1501) if v % P in set(K33)]
OUT["e_iii"]["n_0_256"] = len(v0)
OUT["e_iii"]["P_ge1_0_256"] = round(1 - (1 - len(v0) / 1301) ** 30, 4)
OUT["e_iii"]["n_K33"] = len(vK)
OUT["e_iii"]["P_ge1_K33"] = round(1 - (1 - len(vK) / 1301) ** 30, 4)
OUT["e_iii"]["exp_K33"] = round(30 * len(vK) / 1301, 3)
txt = open(VL + "plate_latin.txt", encoding="utf-8").read()
sec = re.search(r"\[TABULA\]\s*(.*?)\s*\[PIMANDER\]", txt, re.S).group(1)
sec = "\n".join(l for l in sec.splitlines() if not l.startswith("#"))
sents = [s.strip() for s in sec.split(".") if s.strip()]
tab = []
for s_ in sents:
    plain = sum(ord(c) - 64 for c in s_.upper() if "A" <= c <= "Z")
    u = s_.upper().count("U")
    tab.append((plain, plain + u, u))
allsums = [x for a, b, _ in tab for x in (a, b)]
OUT["e_iii"]["n_sentences"] = len(sents)
OUT["e_iii"]["sums"] = tab
OUT["e_iii"]["range"] = (min(allsums), max(allsums))
OUT["e_iii"]["hits_257_1027"] = [x for x in allsums if x in (257, 1027)]
kh = [(x, x % P) for x in allsums if x % P in set(K33)]
OUT["e_iii"]["K33_hits"] = kh
OUT["e_iii"]["P_ge_obsK_binom"] = round(binom_tail(30, len(vK) / 1301, len(kh)), 4)

json.dump(OUT, open(VL.replace("vl/", "bias/lookelsewhere_verify/") + "verify_results.json", "w"), indent=1, default=str)
for k, v in OUT.items():
    print("==", k)
    print(json.dumps(v, default=str, ensure_ascii=False)[:3000])
