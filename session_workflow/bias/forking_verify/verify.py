#!/usr/bin/env python3
# Independent recomputation of the forking-paths exercise. Main counts exhaustive; the added controls use random.Random(20260919).
import re, json, itertools
from math import comb
from collections import Counter

P = 257
G = 3
BASE = '<scratchpad>/'
OUT = BASE + 'bias/forking_verify/'
TAB = '~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/emerald_tablet.json'

K = {0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120, 128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256}
assert len(K) == 33

DLOG = {}
x = 1
for e in range(256):
    DLOG[x] = e
    x = x * G % P
assert len(DLOG) == 256

def val(c): return ord(c) - 96
def lsum(w): return sum(val(c) for c in w.lower() if 'a' <= c <= 'z')
def nlet(w): return sum(1 for c in w.lower() if 'a' <= c <= 'z')

# ---------------- text ----------------
txt = open(BASE + 'vl/plate_latin.txt', encoding='utf-8').read()
sec = {}
cur = None
for line in txt.splitlines():
    if line.startswith('#'): continue
    m = re.fullmatch(r'\[([A-Z]+)\]', line.strip())
    if m: cur = m.group(1); sec[cur] = ''; continue
    if cur: sec[cur] += line + ' '
tab = sec['TABULA'].strip()
sents = [s.strip() for s in tab.split('.') if s.strip()]
assert len(sents) == 15, len(sents)
toks = [re.findall(r'[a-z]+', s.lower()) for s in sents]

out = {}

# ---------------- (a) ----------------
def v_for_u(ws): return [w.replace('u', 'v') for w in ws]
def drop_et(ws): return [w for w in ws if w != 'et']
def que_split(ws):
    r = []
    for w in ws:
        if w.endswith('que') and len(w) > 3: r += [w[:-3], 'que']
        else: r.append(w)
    return r
def j_rule(ws): return [('j' + w[1:]) if (len(w) > 1 and w[0] == 'i' and w[1] in 'aeiou') else w for w in ws]
def ejus(ws): return [w.replace('eius', 'ejus') if w == 'eius' else w for w in ws]
def caelum(ws): return ['caelum' if w == 'coelum' else w for w in ws]

S = lambda ws: sum(lsum(w) for w in ws)
L = lambda ws: sum(len(w) for w in ws)

a1 = []
que_words = sorted({w for t in toks for w in t if w.endswith('que')})
jmatch = sorted({w for t in toks for w in t if len(w) > 1 and w[0] == 'i' and w[1] in 'aeiou'})
ncount_et = []
for i, t in enumerate(toks, 1):
    mod = S(t); vu = S(v_for_u(t)); et = S(drop_et(t)); qu = S(que_split(t)); jj = S(j_rule(t))
    assert qu == mod
    a1.append(dict(s=i, modern=mod, VforU=vu, et_dropped=et, que=qu, J=jj, n_et=t.count('et'), n_u=sum(w.count('u') for w in t), words=len(t), letters=L(t)))
out['a1'] = a1
out['a2'] = dict(que_words=que_words, j_rule_matches=jmatch)

def unif_exp(ms): return sum(1 - comb(P - 33, m) / comb(P, m) for m in ms)

single = []
for r in a1:
    cells = sorted({r[k] % P for k in ('modern', 'VforU', 'et_dropped', 'que', 'J')})
    single.append(dict(s=r['s'], cells=cells, inK=[c for c in cells if c in K]))
out['a3'] = dict(total_distinct=sum(len(x['cells']) for x in single),
                 sentences_hitK=sum(1 for x in single if x['inK']),
                 expected=unif_exp([len(x['cells']) for x in single]),
                 per=single)

# 8 combinations
def variants(t, extra=False):
    res = []
    opts = [(0, 1)] * (5 if extra else 3)
    for combo in itertools.product(*opts):
        w = list(t)
        if extra:
            vu, de, jr, ej, ca = combo
            if ej: w = ejus(w)
            if ca: w = caelum(w)
        else:
            vu, de, jr = combo
        if jr: w = j_rule(w)
        if de: w = drop_et(w)
        if vu: w = v_for_u(w)
        res.append((combo, S(w), L(w)))
    return res

a4 = []
for i, t in enumerate(toks, 1):
    vs = variants(t)
    cells = sorted({s % P for _, s, _ in vs})
    a4.append(dict(s=i, cells=cells, inK=[c for c in cells if c in K], sums=sorted({s for _, s, _ in vs})))
out['a4'] = dict(total_distinct=sum(len(x['cells']) for x in a4),
                 sentences_hitK=sum(1 for x in a4 if x['inK']),
                 expected=unif_exp([len(x['cells']) for x in a4]), per=a4)

# a5 exact integers
a5 = []
for i, t in enumerate(toks, 1):
    for combo, s, l in variants(t, extra=True):
        if s in (257, 1027, 514, 771, 1028):
            a5.append((i, combo, s))
out['a5'] = sorted(set(a5))

# a6: U/V, et/&, ejus, caelum (J rule omitted since no effect) -> 2^4
a6 = []
for i, t in enumerate(toks, 1):
    vs = []
    for vu, de, ej, ca in itertools.product((0, 1), repeat=4):
        w = list(t)
        if ej: w = ejus(w)
        if ca: w = caelum(w)
        if de: w = drop_et(w)
        if vu: w = v_for_u(w)
        vs.append(S(w))
    cells = sorted({s % P for s in vs})
    a6.append(dict(s=i, cells=cells, inK=[c for c in cells if c in K]))
out['a6'] = dict(total_distinct=sum(len(x['cells']) for x in a6),
                 sentences_hitK=sum(1 for x in a6 if x['inK']),
                 expected=unif_exp([len(x['cells']) for x in a6]), per=a6)

# a7 readings
INV = {n: pow(n, P - 2, P) for n in range(1, P)}
def sqrts(n):
    if n == 0: return [0]
    if pow(n, 128, P) != 1: return []
    return sorted({r for r in range(1, P) if r * r % P == n})
def readings(n):
    r = {}
    r['self'] = [n]
    r['fold'] = [(P - n) % P]
    r['inverse'] = [INV[n]] if n else []
    r['square'] = [n * n % P]
    r['sqrt'] = sqrts(n)
    r['double'] = [2 * n % P]
    r['half'] = [129 * n % P]
    r['gamma'] = [] if n == 137 else [(n - 120) * INV[(n + 120) % P] % P]
    r['x17'] = [17 * n % P]
    r['x5'] = [5 * n % P]
    r['x3'] = [3 * n % P]
    r['dlog'] = [DLOG[n]] if n else []
    return r
hitcells = [n for n in range(P) if any(v in K for vs in readings(n).values() for v in vs)]
ndist = [len({v for vs in readings(n).values() for v in vs}) for n in range(P)]
nread = [sum(len(vs) for vs in readings(n).values()) for n in range(P)]
pairs = {}
for i, t in enumerate(toks, 1):
    for combo, s, l in variants(t):
        pairs.setdefault((s % P, (27 * l - s) % P), set()).add(i)
readhit = Counter(); npairhit = 0; sent_hit = set(); sent_all = set()
for (c, a), ss in pairs.items():
    rr = readings(c)
    hits = [k for k, vs in rr.items() if any(v in K for v in vs)]
    if a in K: hits.append('atbash')
    sent_all |= ss
    if hits:
        npairhit += 1; sent_hit |= ss
        for h in hits: readhit[h] += 1
# uniform expectation per sentence without atbash: 1 - C(257-183, m)/C(257, m), m = distinct cells
exp7 = unif_exp_generic = sum(1 - comb(P - len(hitcells), len(x['cells'])) / comb(P, len(x['cells'])) for x in a4)
out['a7'] = dict(pairs=len(pairs), pairs_hit=npairhit, frac=npairhit / len(pairs), sentences_hit=len(sent_hit),
                 sentences_nohit=sorted(sent_all - sent_hit), baseline_cells=len(hitcells),
                 baseline_frac=len(hitcells) / P, min_read=min(ndist), max_read=max(ndist),
                 mean_distinct=sum(ndist) / P, reading_counts=dict(readhit.most_common()), exp_sentences=exp7,
                 pair_list=sorted(pairs.items() and [(k, sorted(v)) for k, v in pairs.items()]))

# ---------------- (b) ----------------
allw = [w for t in toks for w in t]
distinct = sorted(set(allw))
def subset_counts(words, k=4):
    vals = [lsum(w) for w in words]
    mx = sum(sorted(vals)[-k:])
    # dp[j][s] = number of j-subsets summing to s
    dp = [[0] * (mx + 1) for _ in range(k + 1)]
    dp[0][0] = 1
    for v in vals:
        for j in range(k, 0, -1):
            row, prev = dp[j], dp[j - 1]
            for s in range(mx, v - 1, -1):
                if prev[s - v]: row[s] += prev[s - v]
    return dp[k], mx
def bsummary(words):
    d, mx = subset_counts(words)
    tot = sum(d)
    assert tot == comb(len(words), 4)
    mult = {m: (d[m] if m <= mx else 0) for m in (257, 514, 771, 1028)}
    k_mod = sum(c for s, c in enumerate(d) if s % P in K)
    mode_s = max(range(len(d)), key=lambda s: d[s])
    # control: rank of 257 among integer targets
    nb = {s: d[s] for s in range(247, 268)}
    return dict(n=len(words), total=tot, exact257=d[257], frac257=d[257] / tot, exact514=mult[514], exact771=mult[771],
                exact1027=(d[1027] if 1027 <= mx else 0), multiples=sum(mult.values()), inK=k_mod, fracK=k_mod / tot,
                max_sum=mx, mode=mode_s, mode_count=d[mode_s], rank257=sorted(d, reverse=True).index(d[257]) + 1,
                neighbours=nb, mean_sum=sum(s * c for s, c in enumerate(d)) / tot)
out['b1'] = bsummary(distinct)
# full enumeration cross-check of exact 257
vals = [lsum(w) for w in distinct]
cnt = 0
for a, b, c, d_ in itertools.combinations(range(len(vals)), 4):
    if vals[a] + vals[b] + vals[c] + vals[d_] == 257: cnt += 1
out['b1']['enum257'] = cnt
out['b1']['sol_luna_ventus_terra'] = [lsum(w) for w in ('sol', 'luna', 'ventus', 'terra')]
distinct_v = sorted({w.replace('u', 'v') for w in distinct})
out['b2'] = bsummary(distinct_v)
out['b2']['sol_lvna_ventvs_terra'] = sum(lsum(w) for w in ('sol', 'lvna', 'ventvs', 'terra'))

# my own noun tag (dictionary part of speech; proper nouns included; inflected forms separate)
NOUNS = {'mendacio', 'miracula', 'rei', 'res', 'meditatione', 're', 'adaptatione', 'pater', 'sol', 'mater', 'luna',
         'ventus', 'ventre', 'nutrix', 'terra', 'telesmi', 'mundi', 'vis', 'terram', 'igne', 'ingenio', 'coelum', 'vim',
         'gloriam', 'obscuritas', 'fortitudinis', 'fortitudo', 'rem', 'mundus', 'adaptationes', 'modus', 'hermes',
         'trismegistus', 'partes', 'philosophiae', 'operatione', 'solis'}
ADJS = {'verum', 'certum', 'verissimum', 'subtile', 'subtilem', 'spisso', 'solidam', 'superius', 'inferius',
        'superiorum', 'inferiorum'}
missing = (NOUNS | ADJS) - set(distinct)
assert not missing, missing
out['b3_nouns'] = bsummary(sorted(NOUNS))
out['b3_nouns_v'] = bsummary(sorted({w.replace('u', 'v') for w in NOUNS}))
out['b3_nouns_adj'] = bsummary(sorted(NOUNS | ADJS))
out['b3_nouns_adj_v'] = bsummary(sorted({w.replace('u', 'v') for w in NOUNS | ADJS}))
out['distinct_words'] = distinct

# ---------------- (c) ----------------
def spans(seq, bounds=None):
    v = [lsum(w) for w in seq]
    n = len(v)
    targets = {257: [], 514: [], 771: [], 1027: [], 1028: []}
    zero = 0; alls = Counter(); nsp = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            if bounds and bounds[j] != bounds[i]: break
            s += v[j]; nsp += 1; alls[s] += 1
            if s in targets: targets[s].append(' '.join(seq[i:j + 1]))
            if s % P == 0: zero += 1
    return dict(n_words=n, n_spans=nsp, hits={k: len(x) for k, x in targets.items()}, spans=targets, zero_mod=zero,
                ctrl_mean_200_1100=sum(alls[t] for t in range(200, 1101)) / 901,
                ctrl_257_neigh={t: alls[t] for t in range(250, 265)})
seqs = {}
flat = [w for t in toks for w in t]; bnd = [i for i, t in enumerate(toks) for w in t]
seqs['modern'] = (flat, bnd)
seqs['V'] = ([w.replace('u', 'v') for w in flat], bnd)
fe = [(w, b) for w, b in zip(flat, bnd) if w != 'et']
seqs['modern_noet'] = ([w for w, b in fe], [b for w, b in fe])
seqs['V_noet'] = ([w.replace('u', 'v') for w, b in fe], [b for w, b in fe])
out['c'] = {}
for name, (sq, bd) in seqs.items():
    out['c'][name] = dict(whole=spans(sq), within=spans(sq, bd))

# ---------------- (d) ----------------
T = json.load(open(TAB, encoding='utf-8'))
tw = {w.upper(): int(k) for k, v in T.items() for w in v['words']}
out['tablet_nwords'] = sum(len(v['words']) for v in T.values())
pairs_d = [('EHYEH', 'EHEIEH'), ('IUNONI', 'JUNONI'), ('CAELUM', 'COELUM'), ('ALCHYMIA', 'ALCHIMIA'),
           ('PYRAMIDUM', 'PIRAMIDUM'), ('HENRIC', 'HENRICUS'), ('KHUNRATH', 'KUNRATH')]
d = []
for a, b in pairs_d:
    d.append(dict(a=a, sa=lsum(a), a_inK=lsum(a) % P in K, a_tab=tw.get(a), b=b, sb=lsum(b), b_inK=lsum(b) % P in K, b_tab=tw.get(b),
                  differ=lsum(a) % P != lsum(b) % P))
out['d'] = d
extra = ['IVNONI', 'CAELVM', 'COELVM', 'PYRAMIDVM', 'PIRAMIDVM', 'HENRICVS', 'KHVNRATH', 'KVNRATH',
         'HENRIC KHUNRATH', 'HENRICUS KHUNRATH', 'HENRICVS KHVNRATH']
out['d_extra'] = {w: dict(sum=lsum(w), inK=lsum(w) % P in K, tab=tw.get(w)) for w in extra}
out['d_exp'] = 14 * 33 / 257

json.dump(out, open(OUT + 'verify_out.json', 'w'), indent=1, default=str, ensure_ascii=False)

# ================= controls added by the verifier =================
import random
SEED = 20260919
rng = random.Random(SEED)
ctrl = {}
ctrl['nread_min_max'] = (min(nread), max(nread), min(nread[1:]), max(nread[1:]))
ctrl['ndist_nonzero_min_max'] = (min(ndist[1:]), max(ndist[1:]))
# sqrt counted per root value (investigator convention) vs per reading
per_root = 0
for (c, a), ss in pairs.items():
    per_root += sum(1 for r in sqrts(c) if r in K)
ctrl['sqrt_hits_per_root'] = per_root
# random 33-cell sets in place of K, sentence cells fixed (8-combination cells, a4; single-variant cells, a3; 16-combination, a6)
NR = 100000
def sent_hits(cellsets, KK): return sum(1 for cs in cellsets if any(c in KK for c in cs))
for name, per in (('a3', single), ('a4', a4), ('a6', a6)):
    cs = [x['cells'] for x in per]
    real = sent_hits(cs, K)
    dist = Counter()
    for _ in range(NR):
        KK = set(rng.sample(range(P), 33))
        dist[sent_hits(cs, KK)] += 1
    ge = sum(v for k, v in dist.items() if k >= real)
    ctrl['randK_' + name] = dict(real=real, mean=sum(k * v for k, v in dist.items()) / NR, p_ge=ge / NR, dist=dict(sorted(dist.items())))
# (b) fraction of 4-subsets landing in K vs random 33-sets
d4, mx4 = subset_counts(distinct)
cellmass = [0] * P
for s, c in enumerate(d4): cellmass[s % P] += c
tot4 = sum(d4)
realf = sum(cellmass[c] for c in K) / tot4
fr = []
for _ in range(20000):
    KK = rng.sample(range(P), 33)
    fr.append(sum(cellmass[c] for c in KK) / tot4)
fr.sort()
ctrl['randK_b1'] = dict(real=realf, mean=sum(fr) / len(fr), p_ge=sum(1 for f in fr if f >= realf) / len(fr),
                        q05=fr[int(0.05 * len(fr))], q95=fr[int(0.95 * len(fr))], cellmass_0=cellmass[0] / tot4,
                        cellmass_min=min(cellmass) / tot4, cellmass_max=max(cellmass) / tot4,
                        cellmass_uniform=1 / P)
# (a5) sentence variant sums within the cells {0, 256}: count and uniform expectation
allsums = {(r['s'], s) for r in a4 for s in r['sums']}
ctrl['a5_cells_0_256'] = dict(n_variant_sums=len(allsums), hits=sorted(x for x in allsums if x[1] % P in (0, 256)),
                              expected_uniform=len(allsums) * 2 / P)
# (c) span controls: count of spans at every integer target, rank of 257 / 514 / 771 / 1027, distinct word multisets
def span_counter(seq, bounds=None):
    v = [lsum(w) for w in seq]; n = len(v); cnt = Counter(); ms = {}
    for i in range(n):
        s = 0
        for j in range(i, n):
            if bounds and bounds[j] != bounds[i]: break
            s += v[j]; cnt[s] += 1
            ms.setdefault(s, set()).add(tuple(sorted(seq[i:j + 1])))
    return cnt, ms
ctrl['c'] = {}
for name, (sq, bd) in seqs.items():
    for scope, b in (('whole', None), ('within', bd)):
        cnt, ms = span_counter(sq, b)
        row = {}
        for t in (257, 514, 771, 1027, 1028):
            lo, hi = t - 30, t + 30
            window = [cnt[x] for x in range(lo, hi + 1) if x != t]
            row[t] = dict(count=cnt[t], distinct_multisets=len(ms.get(t, ())), window_mean=sum(window) / len(window),
                          window_max=max(window), n_window_ge=sum(1 for w in window if w >= cnt[t]))
        ctrl['c'][name + '_' + scope] = row
json.dump(ctrl, open(OUT + 'verify_controls.json', 'w'), indent=1, default=str)
print(json.dumps(ctrl, indent=1, default=str))
