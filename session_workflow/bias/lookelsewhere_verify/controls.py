#!/usr/bin/env python3
"""Extra controls for the look-elsewhere exercise. numpy Generator PCG64, seed 20260919 throughout."""
import json, re, math
import numpy as np

SEED = 20260919
P = 257
HERE = "<scratchpad>/bias/lookelsewhere_verify/"
VL = HERE.replace("bias/lookelsewhere_verify/", "vl/")
ROOT = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
OUT = {"seed": SEED, "rng": "numpy.random.default_rng (PCG64)"}

K33 = [0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120,
       128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256]
K12 = [1, 8, 16, 23, 44, 46, 62, 72, 73, 120, 136, 137]

DL = np.zeros(P, dtype=int)
x = 1
for k in range(256):
    DL[x] = k
    x = x * 3 % P
INV = np.array([0] + [pow(n, P - 2, P) for n in range(1, P)])
roots = {n: [] for n in range(P)}
for m in range(1, P):
    roots[m * m % P].append(m)

def gam(n):
    d = (n + 120) % P
    return None if d == 0 else (n - 120) * INV[d] % P

# reading matrix: for n in 1..256, list of reading values (ragged -> pad with -1)
READ = []
for n in range(1, P):
    r = [(P - n) % P, INV[n], n * n % P] + roots[n] + [2 * n % P, 129 * n % P]
    g = gam(n)
    if g is not None:
        r.append(g)
    r += [17 * n % P, 5 * n % P, 3 * n % P, DL[n]]
    READ.append(r + [-1] * (12 - len(r)))
READ = np.array(READ)  # 256 x 12
# cell readings incl. cell 0 (for word test), padded
CREAD = []
for c in range(P):
    if c == 0:
        r = [0, 0, 0, 0, 0, 256, 0, 0, 0]  # fold, square, sqrt, double, half, gamma(0)=-1, x17, x5, x3
    else:
        r = list(READ[c - 1])
    CREAD.append(list(r) + [-1] * (12 - len(r)))
CREAD = np.array(CREAD)

def stats_a(Kmask):
    hit = np.where(READ >= 0, Kmask[np.clip(READ, 0, None)], False)
    cnt = hit.sum(1)
    return cnt.mean(), (cnt > 0).mean()

def rand_K(rng, size, pool):
    m = np.zeros(P, bool)
    m[rng.choice(pool, size, replace=False)] = True
    return m

rng = np.random.default_rng(SEED)
NK = 10000
res = {}
for lab, K, size, pool in (("K33", K33, 33, np.arange(P)), ("K12", K12, 12, np.arange(1, P))):
    Km = np.zeros(P, bool); Km[K] = True
    obs = stats_a(Km)
    sims = np.array([stats_a(rand_K(rng, size, pool)) for _ in range(NK)])
    res[lab] = dict(observed_mean=round(obs[0], 4), observed_one=round(obs[1], 4),
                    randK_mean_mean=round(sims[:, 0].mean(), 4), randK_mean_sd=round(sims[:, 0].std(), 4),
                    randK_one_mean=round(sims[:, 1].mean(), 4), randK_one_sd=round(sims[:, 1].std(), 4),
                    randK_one_p5_p95=[round(float(np.percentile(sims[:, 1], q)), 4) for q in (5, 50, 95)],
                    frac_randK_one_ge_obs=round(float((sims[:, 1] >= obs[1] - 1e-12).mean()), 4),
                    frac_randK_mean_ge_obs=round(float((sims[:, 0] >= obs[0] - 1e-12).mean()), 4))
OUT["a_b_randomK"] = res

# closure of K33 under the readings: fraction of K33 cells whose negation / inverse / square is in K33
Ks = set(K33)
OUT["K33_closure"] = dict(
    neg_in_K=sum(1 for k in K33 if (P - k) % P in Ks),
    inv_in_K=sum(1 for k in K33 if k and INV[k] in Ks),
    residues_nonzero=sum(1 for k in K33 if k and roots[k]),
    random_33set_expected_residues="16 of 32 nonzero on average")

# (c) random-K control, vectorised over pairs
a = np.repeat(np.arange(1, P), 256); b = np.tile(np.arange(1, P), 256)
OPS = np.stack([(a + b) % P, (a - b) % P, (b - a) % P, a * b % P, a * INV[b] % P, b * INV[a] % P])
def stats_c(Km):
    return Km[OPS].any(0).mean()
rng = np.random.default_rng(SEED + 1)
cres = {}
for lab, K, size, pool in (("K33", K33, 33, np.arange(P)), ("K12", K12, 12, np.arange(1, P))):
    Km = np.zeros(P, bool); Km[K] = True
    obs = stats_c(Km)
    sims = np.array([stats_c(rand_K(rng, size, pool)) for _ in range(2000)])
    cres[lab] = dict(observed=round(float(obs), 4), randK_mean=round(float(sims.mean()), 4), randK_sd=round(float(sims.std()), 4),
                     randK_p5_p50_p95=[round(float(np.percentile(sims, q)), 4) for q in (5, 50, 95)],
                     frac_randK_ge_obs=round(float((sims >= obs - 1e-12).mean()), 4))
OUT["c_randomK"] = cres
OUT["c_randomK_note"] = "seed 20260920 (SEED+1), 2000 random K sets each"

# (d) random-string control: same letter counts as each tablet entry, letters uniform A..Z
T = json.load(open(ROOT + "emerald_tablet.json", encoding="utf-8"))
ks = []
for pos in sorted(T, key=int):
    for w in T[pos]["words"]:
        ks.append(sum(1 for ch in w.upper() if "A" <= ch <= "Z"))
ks = np.array(ks)
Km33 = np.zeros(P, bool); Km33[K33] = True
Km12 = np.zeros(P, bool); Km12[K12] = True
cellhit33 = Km33 | np.where(CREAD >= 0, Km33[np.clip(CREAD, 0, None)], False).any(1)
cellhit12 = Km12 | np.where(CREAD >= 0, Km12[np.clip(CREAD, 0, None)], False).any(1)
rng = np.random.default_rng(SEED + 2)
fr33, fr12 = [], []
maxk = ks.max()
for _ in range(1000):
    L = rng.integers(1, 27, size=(len(ks), maxk))
    mask = np.arange(maxk)[None, :] < ks[:, None]
    s = (L * mask).sum(1)
    c = s % P
    mir = (27 * ks - s) % P
    fr33.append((cellhit33[c] | Km33[mir]).mean())
    fr12.append((cellhit12[c] | Km12[mir]).mean())
fr33 = np.array(fr33); fr12 = np.array(fr12)
OUT["d_random_strings"] = dict(seed=SEED + 2, reps=1000,
    K33_mean=round(float(fr33.mean()), 4), K33_sd=round(float(fr33.std()), 4),
    K33_p5_p95=[round(float(np.percentile(fr33, q)), 4) for q in (5, 95)], K33_frac_ge_0_7591=round(float((fr33 >= 955 / 1258 - 1e-12).mean()), 4),
    K12_mean=round(float(fr12.mean()), 4), K12_sd=round(float(fr12.std()), 4),
    K12_p5_p95=[round(float(np.percentile(fr12, q)), 4) for q in (5, 95)], K12_frac_ge_0_4332=round(float((fr12 >= 545 / 1258 - 1e-12).mean()), 4))

# (e)(i) Voynich: token shuffle across lines, preserving each line's token count
sums_obs = json.load(open(HERE + "voynich_line_sums.json"))
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
        txt = re.sub(r"<![^>]*>", "", txt)
        txt = re.sub(r"<[^>]*>", ".", txt)
        txt = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", txt)
        txt = re.sub(r"@\d+;", "?", txt)
        txt = txt.replace("{", "").replace("}", "").replace("'", "").replace(",", "")
        toks = [t for t in txt.split(".") if t and re.fullmatch("[a-z]+", t)]
        if toks:
            out.append([sum(ord(ch) - 96 for ch in t) for t in toks])
    return out
lines = voy_lines(VL + "ZL3b-n.txt")
assert [sum(l) for l in lines] == sums_obs
tokvals = np.array([v for l in lines for v in l])
lens = np.array([len(l) for l in lines])
bounds = np.concatenate([[0], np.cumsum(lens)])
obs_counts = np.bincount(np.array(sums_obs) % P, minlength=P)
rng = np.random.default_rng(SEED + 3)
R = 2000
simc = np.zeros((R, P))
for r in range(R):
    perm = rng.permutation(tokvals)
    cs = np.add.reduceat(perm, bounds[:-1])
    simc[r] = np.bincount(cs % P, minlength=P)
mu = simc.mean(0); sd = simc.std(0)
z = (obs_counts - mu) / sd
targets = [0, 1, 23, 44, 46, 62, 72, 73, 86, 92, 120, 136, 137, 256]
lam = len(sums_obs) / P
# how often the shuffle itself puts a cell outside +/-1.8 sqrt(lam) (the Poisson band)
out_poisson_band = (np.abs(simc - lam) > 1.8 * math.sqrt(lam)).sum(1)
# for target cells: in the shuffled texts, how many of the 14 fall outside the Poisson band
out14 = (np.abs(simc[:, targets] - lam) > 1.8 * math.sqrt(lam)).sum(1)
OUT["e_i_shuffle"] = dict(seed=SEED + 3, reps=R,
    control_mean_at_targets={t: round(float(mu[t]), 2) for t in targets},
    control_sd_at_targets={t: round(float(sd[t]), 2) for t in targets},
    z_vs_shuffle={t: round(float(z[t]), 2) for t in targets},
    targets_outside_1p8_vs_shuffle=int((np.abs(z[targets]) > 1.8).sum()),
    all_cells_outside_1p8_vs_shuffle=int((np.abs(z) > 1.8).sum()),
    control_mean_range=[round(float(mu.min()), 2), round(float(mu.max()), 2)],
    control_mean_cells_60_100=round(float(mu[60:101].mean()), 2),
    shuffle_cells_outside_poisson_band_mean=round(float(out_poisson_band.mean()), 2),
    shuffle_targets_outside_poisson_band_mean=round(float(out14.mean()), 3),
    shuffle_P_targets_outside_ge6=round(float((out14 >= 6).mean()), 4))

# (e)(i) additional: what the "25" could be -- line sums of lines with >=1 clean token vs all parsed lines
OUT["e_i_note_lambda"] = dict(lines_5351_over_257=round(5351 / 257, 3), lines_needed_for_25=25 * 257)

# (e)(iii) dependence-aware version: per sentence, hit if plain or V-for-U sum in {257,1027}
q4 = 4 / 1301
OUT["e_iii_pairs"] = dict(per_sentence=round(q4, 5), P_ge1_15_sentences=round(1 - (1 - q4) ** 15, 4))

json.dump(OUT, open(HERE + "controls_results.json", "w"), indent=1, default=str)
print(json.dumps(OUT, indent=1, default=str))
