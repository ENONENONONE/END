#!/usr/bin/env python3
# Voynich (EVA) vs plate Latin (k,s,b) match excess: controls (a)-(g).
# Seeds: (a)/(c)/(g) permutations SEED_A=20260919; (d) bands-of-4 SEED_D4=4, bands-of-2 SEED_D2=2;
# (e) pseudo-Latin SEED_E=5 (token-weighted letters) and SEED_E2=55 (type-weighted letters); (f) reuses (a)'s permutations.
import json, random, statistics, collections, math, sys
from common import *

OUT = "<scratchpad>/bias/voynich/"
SEED_A, SEED_D4, SEED_D2, SEED_E, SEED_E2 = 20260919, 4, 2, 5, 55
N = 300
KEYS = ('cell', 'ks', 'ksb', 'rev', 'atb')
R = {}

toks = load_voynich()
tokc = collections.Counter(toks)
VT = sorted(tokc)
sec = load_plate()
LAT_ALL = sorted(set(f for t in sec.values() for f in forms(t)))
HALF1 = sorted(set(forms(sec['TABULA'] + ' ' + sec['TITLE'])))
HALF2 = sorted(set(forms(sec['CAPTION'] + ' ' + sec['PIMANDER'])))
R['n_tokens'] = len(toks); R['n_types'] = len(VT); R['n_latin_forms'] = len(LAT_ALL)
R['n_half1'] = len(HALF1); R['n_half2'] = len(HALF2); R['n_half_overlap'] = len(set(HALF1) & set(HALF2))

def summarize(obs, arr):
    arr = sorted(arr)
    return dict(obs=obs, mean=round(statistics.mean(arr), 3), median=statistics.median(arr),
                sd=round(statistics.pstdev(arr), 3), min=arr[0], max=arr[-1],
                p95=arr[int(0.95 * len(arr)) - 1], n_ge_obs=sum(a >= obs for a in arr), n=len(arr))

def vkeys(val):
    return {w: keys_all(w, val) for w in VT}

def count_sets(VK, S, types):
    c = {x: 0 for x in KEYS}
    for w in types:
        K = VK[w]
        for x in KEYS:
            tgt = 'ksb' if x in ('rev', 'atb') else x
            if K[x] in S[tgt]: c[x] += 1
    return c

S_ALL, S_H1, S_H2 = latin_sets(LAT_ALL), latin_sets(HALF1), latin_sets(HALF2)
VK0 = vkeys(ID)

# ---------- (b) the identity (k,s,b) matches ----------
lat_by_ksb = collections.defaultdict(list)
for f in LAT_ALL: lat_by_ksb[keys_all(f)['ksb']].append(f)
latset = set(LAT_ALL)
hits = [w for w in VT if VK0[w]['ksb'] in S_ALL['ksb']]
rows = []
for w in sorted(hits, key=lambda w: (-tokc[w], w)):
    rows.append(dict(type=w, tokens=tokc[w], len=len(w), key=list(VK0[w]['ksb']),
                     latin=lat_by_ksb[VK0[w]['ksb']], exact=w in latset))
exact = {r['type'] for r in rows if r['exact']}
short = {r['type'] for r in rows if r['len'] <= 2}
R['b'] = dict(n=len(rows), n_exact=len(exact), n_len_le2=len(short), n_exact_or_le2=len(exact | short),
              n_exact_and_le2=len(exact & short), rows=rows,
              tokens_in_matches=sum(r['tokens'] for r in rows),
              tokens_exact=sum(r['tokens'] for r in rows if r['exact']),
              len_hist=dict(sorted(collections.Counter(r['len'] for r in rows).items())))

# All Voynich types that are exact Latin spellings / of length <= 2 (string properties, independent of alphabet)
EXACT_ALL = {w for w in VT if w in latset}
SHORT_ALL = {w for w in VT if len(w) <= 2}
R['b']['voynich_types_that_are_latin_spellings'] = sorted(EXACT_ALL)
R['b']['voynich_types_len_le2'] = len(SHORT_ALL)
SUBSETS = {
    'all': VT,
    'no_exact': [w for w in VT if w not in EXACT_ALL],
    'no_le2': [w for w in VT if w not in SHORT_ALL],
    'no_exact_no_le2': [w for w in VT if w not in EXACT_ALL and w not in SHORT_ALL],
}
R['subset_sizes'] = {k: len(v) for k, v in SUBSETS.items()}

# ---------- (a), (c), (g): uniform random permutations of the 26 values on the Voynich side ----------
rngA = random.Random(SEED_A)
perms = []
for _ in range(N):
    v = list(range(1, 27)); rngA.shuffle(v); perms.append(v)
ctrl = {(sub, lat): {x: [] for x in KEYS} for sub in SUBSETS for lat in ('all', 'h1', 'h2')}
ctrl_len = collections.defaultdict(list)  # (k,s,b) matches by Voynich length, all types vs full Latin
LSETS = {'all': S_ALL, 'h1': S_H1, 'h2': S_H2}
for v in perms:
    VK = vkeys(v)
    for sub, types in SUBSETS.items():
        for lat, S in LSETS.items():
            if sub != 'all' and lat != 'all': continue
            c = count_sets(VK, S, types)
            for x in KEYS: ctrl[(sub, lat)][x].append(c[x])
    lh = collections.Counter(len(w) for w in VT if VK[w]['ksb'] in S_ALL['ksb'])
    for L in range(1, 16): ctrl_len[L].append(lh.get(L, 0))
for sub, types in SUBSETS.items():
    for lat, S in LSETS.items():
        if sub != 'all' and lat != 'all': continue
        obs = count_sets(VK0, S, types)
        R[f'ctrl_{sub}_{lat}'] = {x: summarize(obs[x], ctrl[(sub, lat)][x]) for x in KEYS}
obs_len = collections.Counter(len(w) for w in hits)
R['len_breakdown'] = {L: dict(obs=obs_len.get(L, 0), ctrl_mean=round(statistics.mean(ctrl_len[L]), 3),
                              ctrl_median=statistics.median(ctrl_len[L]),
                              n_types_len=sum(len(w) == L for w in VT),
                              n_latin_len=sum(len(f) == L for f in LAT_ALL))
                      for L in range(1, 16) if obs_len.get(L, 0) or statistics.mean(ctrl_len[L]) > 0}

# ---------- (d) frequency-banded permutations ----------
letc = collections.Counter(ch for t in toks for ch in t)
rank = sorted('abcdefghijklmnopqrstuvwxyz', key=lambda ch: (-letc.get(ch, 0), ch))
R['d_rank'] = ''.join(rank)
R['d_letter_counts'] = {ch: letc.get(ch, 0) for ch in rank}
def banded(width, seed):
    rng = random.Random(seed)
    bands = [rank[i:i + width] for i in range(0, 26, width)]
    out = {x: [] for x in KEYS}; nid = 0
    for _ in range(N):
        v = list(range(1, 27))
        for band in bands:
            vals = [ord(ch) - 96 for ch in band]; rng.shuffle(vals)
            for ch, val in zip(band, vals): v[ord(ch) - 97] = val
        if v == ID: nid += 1
        c = count_sets(vkeys(v), S_ALL, VT)
        for x in KEYS: out[x].append(c[x])
    obs = count_sets(VK0, S_ALL, VT)
    return dict(bands=[''.join(b) for b in bands], n_identity_draws=nid,
                **{x: summarize(obs[x], out[x]) for x in KEYS}), out
R['d4'], d4raw = banded(4, SEED_D4)
R['d2'], d2raw = banded(2, SEED_D2)
# (d) repeated without exact spellings and without length <= 2 as well
def banded_sub(width, seed, types):
    rng = random.Random(seed)
    bands = [rank[i:i + width] for i in range(0, 26, width)]
    arr = []
    for _ in range(N):
        v = list(range(1, 27))
        for band in bands:
            vals = [ord(ch) - 96 for ch in band]; rng.shuffle(vals)
            for ch, val in zip(band, vals): v[ord(ch) - 97] = val
        VK = {w: keys_all(w, v) for w in types}
        arr.append(sum(VK[w]['ksb'] in S_ALL['ksb'] for w in types))
    obs = sum(VK0[w]['ksb'] in S_ALL['ksb'] for w in types)
    return summarize(obs, arr)
R['d4_no_exact_no_le2'] = banded_sub(4, SEED_D4, SUBSETS['no_exact_no_le2'])
R['d2_no_exact_no_le2'] = banded_sub(2, SEED_D2, SUBSETS['no_exact_no_le2'])

# ---------- (e) pseudo-Latin ----------
lat_tok_letters = collections.Counter(ch for t in sec.values() for f in forms(t) for ch in f)
lat_type_letters = collections.Counter(ch for f in LAT_ALL for ch in f)
lens = [len(f) for f in LAT_ALL]
def pseudo(counter, seed, types=VT):
    rng = random.Random(seed)
    letters = sorted(counter); wts = [counter[c] for c in letters]
    arr = []; arr_exact = []; arr_ks = []
    for _ in range(N):
        fake = [''.join(rng.choices(letters, wts, k=L)) for L in lens]
        S = latin_sets(fake); fs = set(fake)
        arr.append(sum(VK0[w]['ksb'] in S['ksb'] for w in types))
        arr_ks.append(sum(VK0[w]['ks'] in S['ks'] for w in types))
        arr_exact.append(sum(w in fs for w in types))
    obs = sum(VK0[w]['ksb'] in S_ALL['ksb'] for w in types)
    obs_ks = sum(VK0[w]['ks'] in S_ALL['ks'] for w in types)
    obs_exact = sum(w in latset for w in types)
    return dict(ksb=summarize(obs, arr), ks=summarize(obs_ks, arr_ks), exact_spellings=summarize(obs_exact, arr_exact))
R['e_token_weighted'] = pseudo(lat_tok_letters, SEED_E)
R['e_type_weighted'] = pseudo(lat_type_letters, SEED_E2)
R['e_token_weighted_no_exact_no_le2'] = pseudo(lat_tok_letters, SEED_E, SUBSETS['no_exact_no_le2'])['ksb']

# ---------- (f) cosine similarity of letter profiles ----------
def vec(counter): return [counter.get(chr(97 + i), 0) for i in range(26)]
def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
def perm_vec(vc, v):  # Voynich letter i carries value v[i] -> lands on Latin letter with index v[i]-1
    out = [0] * 26
    for i in range(26): out[v[i] - 1] += vc[i]
    return out
vt_tok = vec(letc); vt_typ = vec(collections.Counter(ch for w in VT for ch in w))
lt_tok = vec(lat_tok_letters); lt_typ = vec(lat_type_letters)
f = {}
for name, a, bvec in (('token_token', vt_tok, lt_tok), ('type_type', vt_typ, lt_typ)):
    obs = cos(a, bvec)
    arr = [cos(perm_vec(a, v), bvec) for v in perms]
    arr_s = sorted(arr)
    f[name] = dict(obs=round(obs, 5), mean=round(statistics.mean(arr), 5), median=round(statistics.median(arr), 5),
                   sd=round(statistics.pstdev(arr), 5), min=round(arr_s[0], 5), max=round(arr_s[-1], 5),
                   n_ge_obs=sum(x >= obs for x in arr), n=N)
    if name == 'type_type':
        # relation between profile similarity and (k,s,b) match count across the 300 permutations
        m = ctrl[('all', 'all')]['ksb']
        mx, my = statistics.mean(arr), statistics.mean(m)
        num = sum((x - mx) * (y - my) for x, y in zip(arr, m))
        den = math.sqrt(sum((x - mx) ** 2 for x in arr) * sum((y - my) ** 2 for y in m))
        f[name]['pearson_r_cos_vs_ksb_matches'] = round(num / den, 4)
        top = sorted(zip(arr, m), reverse=True)[:30]
        f[name]['ksb_mean_top30_cos'] = round(statistics.mean(y for _, y in top), 3)
    if name == 'token_token':
        m = ctrl[('all', 'all')]['ksb']
        mx, my = statistics.mean(arr), statistics.mean(m)
        num = sum((x - mx) * (y - my) for x, y in zip(arr, m))
        den = math.sqrt(sum((x - mx) ** 2 for x in arr) * sum((y - my) ** 2 for y in m))
        f[name]['pearson_r_cos_vs_ksb_matches'] = round(num / den, 4)
        top = sorted(zip(arr, m), reverse=True)[:30]
        f[name]['ksb_mean_top30_cos'] = round(statistics.mean(y for _, y in top), 3)
R['f'] = f
# band-control cosines (how close the banded alphabets stay to identity's profile)
def band_cos(width, seed):
    rng = random.Random(seed); bands = [rank[i:i + width] for i in range(0, 26, width)]; arr = []
    for _ in range(N):
        v = list(range(1, 27))
        for band in bands:
            vals = [ord(ch) - 96 for ch in band]; rng.shuffle(vals)
            for ch, val in zip(band, vals): v[ord(ch) - 97] = val
        arr.append(cos(perm_vec(vt_typ, v), lt_typ))
    return dict(mean=round(statistics.mean(arr), 5), median=round(statistics.median(arr), 5),
                min=round(min(arr), 5), max=round(max(arr), 5))
R['f_band4_type_cos'] = band_cos(4, SEED_D4)
R['f_band2_type_cos'] = band_cos(2, SEED_D2)

json.dump(R, open(OUT + 'results.json', 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in R.items() if k != 'b'}, indent=1, default=str))
b = R['b']
print('\n(b)', {k: v for k, v in b.items() if k not in ('rows',)})
for r in b['rows']:
    print(f"{r['type']:<12} tok {r['tokens']:>5} len {r['len']:>2} key {tuple(r['key'])} exact {int(r['exact'])} latin {r['latin']}")
