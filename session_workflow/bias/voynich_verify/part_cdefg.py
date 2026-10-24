import json, random, collections, sys
import numpy as np
from common import *

toks, rows = voy_tokens()
tc = collections.Counter(toks)
types = sorted(tc)
sec = latin_sections()
lat_tokens = [w for s in sec.values() for w in s]
forms = sorted(set(lat_tokens))
formset = set(forms)
L = latin_keysets(forms)
vm = VMat(types)
obs = counts(vm, IDENT, L)
out = {}

def perms(seed, n):
    r = random.Random(seed); o = []
    for _ in range(n):
        v = list(range(1, 27)); r.shuffle(v); o.append(v)
    return o
UNI = perms(1919, 300)

# (c) removals
ex = np.array([w in formset for w in types]); sh = np.array([len(w) <= 2 for w in types])
for name, mask in (('no_exact', ~ex), ('no_short', ~sh), ('no_both', ~ex & ~sh)):
    o = counts(vm, IDENT, L, mask)
    C = collections.defaultdict(list)
    for v in UNI:
        for k2, x in counts(vm, v, L, mask).items(): C[k2].append(x)
    out['c_' + name] = {'ntypes': int(mask.sum()), **{k2: summ(C[k2], o[k2]) for k2 in C}}
    print('(c)', name, int(mask.sum()))
    for k2 in ('ksb', 'rev', 'atb', 'cell', 'ks'): print('   ', k2, out['c_' + name][k2])

# (d) frequency bands
lc = collections.Counter(c for w in toks for c in w)
rank = sorted('abcdefghijklmnopqrstuvwxyz', key=lambda c: (-lc[c], c))
print('(d) rank', ''.join(rank), [(c, lc[c]) for c in rank])
out['d_rank'] = ''.join(rank)
def band_perms(width, seed, n):
    r = random.Random(seed); o = []; nid = 0
    bands = [rank[i:i + width] for i in range(0, 26, width)]
    for _ in range(n):
        vals = list(range(1, 27))
        for bd in bands:
            vs = [ord(c) - 96 for c in bd]; r.shuffle(vs)
            for c, v in zip(bd, vs): vals[ord(c) - 97] = v
        if vals == IDENT: nid += 1
        o.append(vals)
    return o, bands, nid
BANDS = {}
for width, seed in ((4, 4444), (2, 2222)):
    PP, bands, nid = band_perms(width, seed, 300)
    BANDS[width] = PP
    C = collections.defaultdict(list); Cm = []
    for v in PP:
        for k2, x in counts(vm, v, L).items(): C[k2].append(x)
        Cm.append(counts(vm, v, L, ~ex & ~sh)['ksb'])
    out[f'd_band{width}'] = {'bands': ['' .join(b) for b in bands], 'identity_draws': nid,
                             **{k2: summ(C[k2], obs[k2]) for k2 in C},
                             'ksb_no_both': summ(Cm, counts(vm, IDENT, L, ~ex & ~sh)['ksb'])}
    print('(d) width', width, 'seed', seed, 'bands', '|'.join(''.join(b) for b in bands), 'identity draws', nid)
    for k2 in ('ksb', 'cell', 'ks', 'rev', 'atb'): print('   ', k2, out[f'd_band{width}'][k2])
    print('    ksb no_both', out[f'd_band{width}']['ksb_no_both'])

# (e) pseudo-Latin
def pseudo(seed, weight_src, n=300, mask=None):
    r = random.Random(seed)
    letters = [c for w in weight_src for c in w]
    lens = [len(w) for w in forms]
    Kid = vm.keys(IDENT)
    typeset = set(types)
    res = collections.defaultdict(list)
    for _ in range(n):
        pf = [''.join(r.choice(letters) for _ in range(l)) for l in lens]
        Lp = latin_keysets(pf)
        for name in ('ks', 'ksb'):
            hit = np.isin(Kid[name], Lp[name])
            if mask is not None: hit &= mask
            res[name].append(int(hit.sum()))
        res['exact'].append(len(typeset & set(pf)))
    return res
for tag, seed, src, mask in (('tok', 5555, lat_tokens, None), ('type', 5566, forms, None), ('tok_no_both', 5555, lat_tokens, ~ex & ~sh)):
    rr = pseudo(seed, src, mask=mask)
    o_ksb = counts(vm, IDENT, L, mask)['ksb']
    out['e_' + tag] = {'seed': seed, 'ksb': summ(rr['ksb'], o_ksb), 'ks': summ(rr['ks'], counts(vm, IDENT, L, mask)['ks']),
                       'exact': summ(rr['exact'], 5)}
    print('(e)', tag, seed, out['e_' + tag])

# (f) cosine
Vc = np.zeros(26); Vt = np.zeros(26); Lc = np.zeros(26); Lt = np.zeros(26)
for w in toks:
    for c in w: Vc[ord(c) - 97] += 1
for w in types:
    for c in w: Vt[ord(c) - 97] += 1
for w in lat_tokens:
    for c in w: Lc[ord(c) - 97] += 1
for w in forms:
    for c in w: Lt[ord(c) - 97] += 1
def cos_perm(Vv, Lv, vals):
    x = np.zeros(26)
    for i in range(26): x[vals[i] - 1] += Vv[i]
    return float(x @ Lv / np.linalg.norm(x) / np.linalg.norm(Lv))
ksb_uni = [counts(vm, v, L)['ksb'] for v in UNI]
for tag, Vv, Lv in (('token', Vc, Lc), ('type', Vt, Lt)):
    cid = cos_perm(Vv, Lv, IDENT)
    cs = [cos_perm(Vv, Lv, v) for v in UNI]
    r = float(np.corrcoef(cs, ksb_uni)[0, 1])
    top = np.argsort(cs)[-30:]
    a = np.array(cs)
    out['f_' + tag] = dict(identity=round(cid, 5), mean=round(float(a.mean()), 5), median=round(float(np.median(a)), 5),
                           sd=round(float(a.std(ddof=1)), 5), min=round(float(a.min()), 5), max=round(float(a.max()), 5),
                           ge=int((a >= cid).sum()), r_with_ksb=round(r, 4), top30_ksb_mean=round(float(np.mean([ksb_uni[i] for i in top])), 3))
    print('(f)', tag, out['f_' + tag])
    for width in (4, 2):
        b = np.array([cos_perm(Vv, Lv, v) for v in BANDS[width]])
        print('   bands', width, 'mean', round(b.mean(), 5), 'median', round(float(np.median(b)), 5), 'range', round(b.min(), 5), round(b.max(), 5))
        out[f'f_{tag}_band{width}'] = dict(mean=round(b.mean(), 5), median=round(float(np.median(b)), 5), min=round(b.min(), 5), max=round(b.max(), 5))

# (g) halves
halves = {'TABULA+TITLE': sorted(set(sec['TABULA']) | set(sec['TITLE'])),
          'CAPTION+PIMANDER': sorted(set(sec['CAPTION']) | set(sec['PIMANDER']))}
print('(g) shared forms', len(set(halves['TABULA+TITLE']) & set(halves['CAPTION+PIMANDER'])))
for hn, hf in halves.items():
    Lh = latin_keysets(hf)
    oh = counts(vm, IDENT, Lh)
    C = collections.defaultdict(list)
    for v in UNI:
        for k2, x in counts(vm, v, Lh).items(): C[k2].append(x)
    out['g_' + hn] = {'nforms': len(hf), **{k2: summ(C[k2], oh[k2]) for k2 in C}}
    print('(g)', hn, len(hf))
    for k2 in ('cell', 'ks', 'ksb', 'rev', 'atb'): print('   ', k2, out['g_' + hn][k2])
json.dump(out, open('out_cdefg.json', 'w'), indent=1)
