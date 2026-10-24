#!/usr/bin/env python3
"""Look-elsewhere exercise: how easily a cell 'lands' in the key set K under the corpus's readings.
Exact enumeration throughout; no random generator is used (so no seed is needed).
Writes results.json and results.txt next to this script."""
import json, re, math, os, sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
TABLET = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/emerald_tablet.json"
VL = "<scratchpad>/vl/"

P = 257
DLOG = {pow(3, k, P): k for k in range(256)}
INV = lambda n: pow(n, P - 2, P)
K33 = {0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120,
       128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256}
K12 = {1, 8, 16, 23, 44, 46, 62, 72, 73, 120, 136, 137}
assert len(K33) == 33 and len(K12) == 12

def sqrt_roots(n):
    return sorted(r for r in range(P) if r * r % P == n)

def gamma(n):
    d = (n + 120) % P
    if d == 0:
        return None  # infinity
    return (n - 120) * INV(d) % P

def readings(n):
    """Readings R of a nonzero cell n, n itself excluded. Each square root counted separately.
    Returns list of (name, value); value None = infinity (never in K)."""
    out = [("fold", (P - n) % P), ("inverse", INV(n)), ("square", n * n % P)]
    for i, r in enumerate(sqrt_roots(n)):
        out.append((f"sqrt{i+1}", r))
    out += [("double", 2 * n % P), ("half", 129 * n % P), ("gamma", gamma(n)),
            ("x17", 17 * n % P), ("x5", 5 * n % P), ("x3", 3 * n % P), ("dlog3", DLOG[n])]
    return out

def readings_of_cell(c):
    """Readings for a cell that may be 0 (phrase cells). For 0: inverse and dlog undefined."""
    if c != 0:
        return readings(c)
    return [("fold", 0), ("square", 0), ("sqrt1", 0), ("double", 0), ("half", 0),
            ("gamma", gamma(0)), ("x17", 0), ("x5", 0), ("x3", 0)]

R = {}
res = {}
txt = []
def out(key, val, method):
    R[key] = dict(value=val, method=method)
    txt.append(f"{key}: {val}    [{method}]")

# ---------------- (a) and (b) ----------------
def part_ab(Kset, tag):
    counts = {}
    per_reading = {}
    nread = {}
    for n in range(1, 257):
        rs = readings(n)
        nread[n] = len(rs)
        c = 0
        for name, v in rs:
            key = "sqrt" if name.startswith("sqrt") else name
            if v is not None and v in Kset:
                c += 1
                per_reading[key] = per_reading.get(key, 0) + 1
        counts[n] = c
    tot = sum(counts.values())
    mean = Fraction(tot, 256)
    atleast = sum(1 for n in counts if counts[n] >= 1)
    none = [n for n in range(1, 257) if counts[n] == 0]
    total_readings = sum(nread.values())
    dist = {}
    for n in counts:
        dist[counts[n]] = dist.get(counts[n], 0) + 1
    # baseline: each reading an independent uniform draw over the 257 cells 0..256
    q = Fraction(len(Kset), 257)
    base_mean = sum(Fraction(nread[n]) * q for n in nread) / 256
    base_atleast = sum(1 - (1 - q) ** nread[n] for n in nread) / 256
    # within K itself vs outside K
    inK = [n for n in range(1, 257) if n in Kset]
    outK = [n for n in range(1, 257) if n not in Kset]
    mean_in = Fraction(sum(counts[n] for n in inK), len(inK))
    mean_out = Fraction(sum(counts[n] for n in outK), len(outK))
    frac_out_atleast = Fraction(sum(1 for n in outK if counts[n] >= 1), len(outK))
    return dict(total_landings=tot, total_readings=total_readings, mean=mean, atleast=atleast,
                frac_atleast=Fraction(atleast, 256), none=none, dist=dict(sorted(dist.items())),
                per_reading=dict(sorted(per_reading.items(), key=lambda x: -x[1])),
                base_mean=base_mean, base_atleast=base_atleast, mean_in=mean_in, mean_out=mean_out,
                n_outK=len(outK), frac_out_atleast=frac_out_atleast, max=max(counts.values()),
                argmax=[n for n in counts if counts[n] == max(counts.values())], counts=counts)

for tag, Kset in (("a", K33), ("b", K12)):
    r = part_ab(Kset, tag)
    res[tag] = {k: (str(v) if isinstance(v, Fraction) else v) for k, v in r.items() if k != "counts"}
    res[tag]["counts"] = r["counts"]
    ksz = len(Kset)
    out(f"{tag}.mean_landings", f"{float(r['mean']):.4f} ({r['mean']} = {r['total_landings']}/256)",
        f"n = 1..256, readings R excluding n itself (10 per non-residue, 12 per residue, {r['total_readings']} readings in all), count readings with value in K{ksz}; mean over n")
    out(f"{tag}.frac_at_least_one", f"{float(r['frac_atleast']):.4f} ({r['atleast']}/256)",
        f"fraction of n in 1..256 with at least one reading in K{ksz}")
    out(f"{tag}.n_with_none", f"{len(r['none'])} cells: {r['none']}",
        f"n in 1..256 with no reading in K{ksz}")
    out(f"{tag}.distribution_of_counts", r["dist"], "number of n with each landing count")
    out(f"{tag}.landings_by_reading", r["per_reading"],
        "landings in K summed over n, per reading type (sqrt = both roots together)")
    out(f"{tag}.max_count", f"{r['max']} at n = {r['argmax']}", "largest landing count and where")
    out(f"{tag}.mean_for_n_outside_K", f"{float(r['mean_out']):.4f} over {r['n_outK']} cells; at-least-one fraction {float(r['frac_out_atleast']):.4f} ({sum(1 for n in r['counts'] if n not in Kset and r['counts'][n]>=1)}/{r['n_outK']})",
        f"same count restricted to n in 1..256 not in K{ksz}")
    out(f"{tag}.mean_for_n_inside_K", f"{float(r['mean_in']):.4f}", f"same count restricted to n in K{ksz} (n != 0)")
    out(f"{tag}.baseline_independent_uniform", f"mean {float(r['base_mean']):.4f}, at-least-one {float(r['base_atleast']):.4f}",
        f"reference only: if each reading were an independent uniform draw over 0..256, P(hit)={ksz}/257 per reading, same number of readings per n")

# ---------------- (c) pairs ----------------
def part_c(Kset):
    hit = 0; hit_ne = 0; tri = 0; tri_ne = 0; N = 0; N_ne = 0
    per_op = dict(add=0, sub_ab=0, sub_ba=0, mul=0, div_ab=0, div_ba=0)
    for a in range(1, 257):
        ia = INV(a)
        for b in range(1, 257):
            ib = INV(b)
            vals = dict(add=(a + b) % P, sub_ab=(a - b) % P, sub_ba=(b - a) % P,
                        mul=a * b % P, div_ab=a * ib % P, div_ba=b * ia % P)
            h = False
            for k, v in vals.items():
                if v in Kset:
                    per_op[k] += 1; h = True
            t = vals["add"] in (256, 0, 1)
            N += 1; hit += h; tri += t
            if a != b:
                N_ne += 1; hit_ne += h; tri_ne += t
    return dict(N=N, hit=hit, N_ne=N_ne, hit_ne=hit_ne, tri=tri, tri_ne=tri_ne, per_op=per_op)

for tag, Kset in (("c", K33), ("c_K12", K12)):
    r = part_c(Kset)
    res[tag] = r
    ksz = len(Kset)
    out(f"{tag}.frac_any_of_six_in_K{ksz}", f"{r['hit']/r['N']:.4f} ({r['hit']}/{r['N']})",
        f"all ordered pairs a,b in 1..256 (a=b included); any of a+b, a-b, b-a, ab, a/b, b/a mod 257 in K{ksz}")
    out(f"{tag}.frac_any_of_six_in_K{ksz}_a_ne_b", f"{r['hit_ne']/r['N_ne']:.4f} ({r['hit_ne']}/{r['N_ne']})",
        "same, pairs with a != b only (a=b always gives a-b = 0 and a/b = 1)")
    out(f"{tag}.hits_per_operation", r["per_op"], f"pairs (a=b included) whose given result is in K{ksz}")
    if tag == "c":
        out("c.frac_sum_is_256_0_or_1", f"{r['tri']/r['N']:.4f} ({r['tri']}/{r['N']}); a!=b: {r['tri_ne']/r['N_ne']:.4f} ({r['tri_ne']}/{r['N_ne']})",
            "ordered pairs with a+b = 256, 0 or 1 mod 257")
# independent-draw reference for (c)
q = 33 / 257
out("c.baseline_six_independent", f"{1-(1-q)**6:.4f}", "reference only: 1-(224/257)^6, six independent uniform draws over 0..256")
out("c.baseline_sum_three_cells", f"{3/257:.4f}", "reference: 3/257, one uniform draw hitting one of three cells")

# ---------------- (d) tablet words ----------------
T = json.load(open(TABLET, encoding="utf-8"))
entries = [(int(c), w) for c, v in T.items() for w in v["words"]]
def kw(w):
    vals = [ord(ch) - 64 for ch in w.upper() if "A" <= ch <= "Z"]
    return len(vals), sum(vals)
def part_d(Kset, items):
    n = len(items); hit = 0; by_cell = 0; by_mirror = 0; by_R_only = 0; zero_letters = 0; cell_matches_pos = 0
    for pos, w in items:
        k, s = kw(w)
        if k == 0: zero_letters += 1
        c = s % P
        if c == pos: cell_matches_pos += 1
        m = (27 * k - s) % P
        a = c in Kset
        b = m in Kset
        rr = any(v is not None and v in Kset for _, v in readings_of_cell(c))
        if a: by_cell += 1
        if b: by_mirror += 1
        if a or b or rr: hit += 1
        if rr and not a and not b: by_R_only += 1
    return dict(n=n, hit=hit, by_cell=by_cell, by_mirror=by_mirror, by_R_only=by_R_only,
                zero_letters=zero_letters, cell_matches_pos=cell_matches_pos)
seen = set(); uniq = []
for pos, w in entries:
    if w not in seen:
        seen.add(w); uniq.append((pos, w))
for tag, Kset in (("d", K33), ("d_K12", K12)):
    r = part_d(Kset, entries); ru = part_d(Kset, uniq)
    res[tag] = dict(all=r, unique=ru)
    ksz = len(Kset)
    out(f"{tag}.frac_words_landing", f"{r['hit']/r['n']:.4f} ({r['hit']}/{r['n']}); unique strings {ru['hit']/ru['n']:.4f} ({ru['hit']}/{ru['n']})",
        f"each tablet word: cell = letter sum mod 257; lands if cell in K{ksz}, or any reading R of the cell in K{ksz}, or Atbash mirror 27k-s mod 257 in K{ksz}")
    out(f"{tag}.frac_cell_itself_in_K", f"{r['by_cell']/r['n']:.4f} ({r['by_cell']}/{r['n']})", "letter-sum cell itself in K")
    out(f"{tag}.frac_mirror_in_K", f"{r['by_mirror']/r['n']:.4f} ({r['by_mirror']}/{r['n']})", "Atbash mirror sum in K")
    out(f"{tag}.frac_only_via_readings", f"{r['by_R_only']/r['n']:.4f} ({r['by_R_only']}/{r['n']})", "landing only through a reading R (cell and mirror not in K)")
    if tag == "d":
        out("d.word_counts", f"{r['n']} entries, {ru['n']} unique strings, {r['zero_letters']} with no letters, {r['cell_matches_pos']} whose letter-sum cell equals their tablet position",
            "tablet census")
# all 257 cells as a reference for (d): fraction of cells c in 0..256 for which c or R(c) is in K33
cells_land = sum(1 for c in range(257) if c in K33 or any(v is not None and v in K33 for _, v in readings_of_cell(c)))
out("d.reference_cells_c_or_R_in_K33", f"{cells_land}/257 = {cells_land/257:.4f}", "cells 0..256 with the cell itself or a reading in K33 (no mirror; the mirror depends on word length)")

# ---------------- (e)(i) Voynich ----------------
def pois_pmf(k, lam):
    return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))
def pois_outside(lam, z):
    sd = math.sqrt(lam); lo = lam - z * sd; hi = lam + z * sd
    strict = sum(pois_pmf(k, lam) for k in range(0, 400) if k < lo or k > hi)
    incl = sum(pois_pmf(k, lam) for k in range(0, 400) if k <= lo or k >= hi)
    return strict, lo, hi, incl
phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
p_norm = 2 * (1 - phi(1.8))
for lam, lab in ((25.0, "lambda25"), (5351 / 257, "lambda_5351_over_257")):
    p, lo, hi, pin = pois_outside(lam, 1.8)
    out(f"e_i.{lab}.p_at_or_beyond_1.8sd", f"{pin:.4f}; expected of 14 = {14*pin:.4f}", "same, boundary values counted as outside (matters only when λ±1.8√λ is an integer)")
    out(f"e_i.{lab}.p_outside_1.8sd", f"{p:.4f} (band {lo:.3f}..{hi:.3f}, integers outside it)",
        f"Poisson(λ={lam:.4f}): P(X < λ-1.8√λ or X > λ+1.8√λ), exact pmf sum")
    out(f"e_i.{lab}.expected_of_14", f"{14*p:.4f}", "14 × p")
    out(f"e_i.{lab}.p_at_least_one_of_14", f"{1-(1-p)**14:.4f}", "1-(1-p)^14, cells treated as independent")
    out(f"e_i.{lab}.p_at_least_two_of_14", f"{1-(1-p)**14-14*p*(1-p)**13:.4f}", "binomial(14,p) tail ≥2")
out("e_i.normal_p_outside_1.8sd", f"{p_norm:.5f}; expected of 14 = {14*p_norm:.4f}; P(≥1) = {1-(1-p_norm)**14:.4f}",
    "two-sided normal tail 2(1-Φ(1.8))")
# Voynich line sums, observed spread over all 257 cells (reference)
sys.path.insert(0, VL)
import voy
pages, rows = voy.parse(VL + "ZL3b-n.txt")
line_cells = []; line_sums = []
for page, ln, loc, t in rows:
    ws = [w for w in voy.words(t) if re.fullmatch('[a-z]+', w)]
    if ws:
        line_sums.append(sum(ord(ch) - 96 for w in ws for ch in w)); line_cells.append(line_sums[-1] % P)
L = len(line_cells)
cnt = [0] * P
for c in line_cells: cnt[c] += 1
lam = L / P; sd = math.sqrt(lam)
outside_all = [c for c in range(P) if abs(cnt[c] - lam) > 1.8 * sd]
targets = [0, 1, 23, 44, 46, 62, 72, 73, 86, 92, 120, 136, 137, 256]
tz = {c: (cnt[c], round((cnt[c] - lam) / sd, 3)) for c in targets}
out("e_i.voynich_lines", f"{L} lines, mean {lam:.4f} per cell", "lines with ≥1 clean token (voy.parse/words, commas join, [a-z]+ tokens); line cell = letter sum (a=1..z=26) mod 257")
out("e_i.voynich_cells_outside_1.8sd_of_257", f"{len(outside_all)} of 257 ({len(outside_all)/257:.4f}); expected under Poisson(λ={lam:.3f}) {257*pois_outside(lam,1.8)[0]:.2f}",
    "reference: all 257 cells, |count-λ| > 1.8√λ")
out("e_i.voynich_14_targets_count_z", tz, "reference: observed count and z = (count-λ)/√λ at each of the 14 target cells, λ = lines/257")
ls_sorted = sorted(line_sums); mean_ls = sum(line_sums)/L
var_c = sum((c - lam)**2 for c in cnt)/P
out("e_i.voynich_line_sum_stats", f"min {ls_sorted[0]}, median {ls_sorted[L//2]}, mean {mean_ls:.2f}, max {ls_sorted[-1]}; lines with sum < 257: {sum(1 for x in line_sums if x < 257)}", "raw line sums before mod 257")
out("e_i.voynich_dispersion_index", f"{var_c/lam:.3f} (cell-count variance {var_c:.2f} vs Poisson {lam:.2f}); min cell count {min(cnt)}, max {max(cnt)}", "variance of the 257 cell counts / mean; 1.0 for Poisson-uniform")
base = len(outside_all)/257
out("e_i.expected_of_14_at_observed_base_rate", f"{14*base:.4f}; P(≥6 of 14) = {sum(math.comb(14,k)*base**k*(1-base)**(14-k) for k in range(6,15)):.4f}", "reference: 14 × (55/257), the fraction of all 257 cells outside ±1.8 SD in this same data; binomial tail")
out("e_i.voynich_14_targets_outside", sum(1 for c in targets if abs(cnt[c] - lam) > 1.8 * sd), "reference: how many of the 14 exceed ±1.8 SD under λ = lines/257")
res["e_i_counts"] = cnt

# ---------------- (e)(ii) rongorongo stars ----------------
p = 88 / 360
exp_ = 21 * p
tail = sum(math.comb(21, k) * p**k * (1 - p)**(21 - k) for k in range(7, 22))
out("e_ii.p_per_star", f"{p:.4f} (88/360)", "22 windows × 4° = 88° maximum coverage, uniform azimuth")
out("e_ii.expected_stars_in_window", f"{exp_:.4f}", "21 × 88/360")
out("e_ii.p_7_or_more", f"{tail:.4f}", "binomial(21, 88/360) upper tail P(X ≥ 7)")
for kk in (5, 6, 8, 9, 10):
    t2 = sum(math.comb(21, k) * p**k * (1 - p)**(21 - k) for k in range(kk, 22))
    out(f"e_ii.p_{kk}_or_more", f"{t2:.4f}", f"binomial(21, 88/360) P(X ≥ {kk})")

# ---------------- (e)(iii) Tabula ----------------
span = list(range(200, 1501)); Ns = len(span)
q2 = Fraction(2, Ns)
out("e_iii.p_one_sum_is_257_or_1027", f"{float(q2):.5f} (2/{Ns})", "uniform over integers 200..1500 inclusive")
out("e_iii.p_at_least_one_of_30", f"{1-(1-float(q2))**30:.4f}", "1-(1-2/1301)^30, sums treated as independent")
out("e_iii.expected_hits_of_30", f"{30*float(q2):.4f}", "30 × 2/1301")
q0 = sum(1 for x in span if x % P in (0, 256))
out("e_iii.p_at_least_one_congruent_0_or_256", f"{1-(1-q0/Ns)**30:.4f} ({q0} of {Ns} values ≡ 0 or 256)", "any multiple of 257 or one less, same model")
qK = sum(1 for x in span if x % P in K33)
out("e_iii.p_at_least_one_in_K33", f"{1-(1-qK/Ns)**30:.4f} ({qK} of {Ns} values have mod 257 in K33); expected {30*qK/Ns:.3f}", "any of 30 sums with mod-257 cell in K33, same model")
# observed Tabula sums (both spellings), for reference
sec = {}; cur = None
for line in open(VL + "plate_latin.txt", encoding="utf-8"):
    line = line.rstrip("\n")
    if not line or line.startswith("#"): continue
    m = re.fullmatch(r"\[(\w+)\]", line.strip())
    if m: cur = m.group(1); sec[cur] = ""; continue
    sec[cur] += line + " "
sents = [s.strip() for s in sec["TABULA"].split(".") if re.search("[A-Za-z]", s)]
sums = []
for s in sents:
    a = sum(ord(ch) - 64 for ch in s.upper() if "A" <= ch <= "Z")
    u = s.upper().count("U")
    sums += [a, a + u]
inK = [x for x in sums if x % P in K33]
out("e_iii.observed_sentences", f"{len(sents)} sentences, {len(sums)} sums, range {min(sums)}..{max(sums)}", "TABULA section split on '.', plain and V-for-U spellings (tabula.py's 'as cut' = +count of U)")
out("e_iii.observed_sums_in_K33", f"{len(inK)} of {len(sums)}: {inK} -> cells {[x%P for x in inK]}", "reference: observed sums whose mod-257 cell is in K33")
bt = sum(math.comb(30, k) * (qK / Ns)**k * (1 - qK / Ns)**(30 - k) for k in range(len(inK), 31))
out("e_iii.p_that_many_or_more_in_K33", f"{bt:.4f}", f"reference: binomial(30, {qK}/{Ns}) P(X ≥ {len(inK)})")
exact_hits = [x for x in sums if x in (257, 1027)]
qq = float(q2)
out("e_iii.p_at_least_two_of_30", f"{1-(1-qq)**30-30*qq*(1-qq)**29:.6f}", "binomial(30, 2/1301) P(X ≥ 2), same independence model")
out("e_iii.observed_exact_257_or_1027", exact_hits, "observed sums equal to 257 or 1027")

json.dump(dict(results=R, detail={k: v for k, v in res.items()}), open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)
open(os.path.join(HERE, "results.txt"), "w").write("\n".join(txt) + "\n")
print("\n".join(txt))
