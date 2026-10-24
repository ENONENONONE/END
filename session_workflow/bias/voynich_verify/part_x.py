# Refutation tests: conditioning, scan of b offsets, distinct-key statistic, parse sensitivity, English control.
import json, random, collections, re
import numpy as np
from common import *

toks, rows = voy_tokens()
tc = collections.Counter(toks)
types = sorted(tc)
sec = latin_sections()
lat_tokens = [w for s in sec.values() for w in s]
forms = sorted(set(lat_tokens))
L = latin_keysets(forms)
vm = VMat(types)
obs = counts(vm, IDENT, L)
out = {}

# 1. mean letter value alignment
Vt = vm.C.sum(0).astype(float)            # type-weighted letter counts
Vk = np.zeros(26)
for w in toks:
    for c in w: Vk[ord(c) - 97] += 1
Lt = np.zeros(26)
for w in forms:
    for c in w: Lt[ord(c) - 97] += 1
Lk = np.zeros(26)
for w in lat_tokens:
    for c in w: Lk[ord(c) - 97] += 1
vals = np.arange(1, 27)
mv = lambda cnt, v: float(cnt @ np.asarray(v) / cnt.sum())
print('mean letter value: voynich types', round(mv(Vt, vals), 3), 'tokens', round(mv(Vk, vals), 3), '| latin forms', round(mv(Lt, vals), 3), 'tokens', round(mv(Lk, vals), 3))
# per-length mean s
for l in range(3, 10):
    vs = [ksb(w)[1] for w in types if len(w) == l]; ls_ = [ksb(w)[1] for w in forms if len(w) == l]
    print('   L', l, 'mean s voynich', round(np.mean(vs), 2), 'sd', round(np.std(vs), 2), '| latin', round(np.mean(ls_), 2), 'sd', round(np.std(ls_), 2))

# 2. big uniform sample; conditioning
r = random.Random(987654); N = 20000
mvs = []; ks_ = []; ksb_ = []; cell_ = []; keyhits = []
Lksb = L['ksb']
for _ in range(N):
    v = list(range(1, 27)); r.shuffle(v)
    K = vm.keys(v)
    hit = np.isin(K['ksb'], Lksb)
    ksb_.append(int(hit.sum())); ks_.append(int(np.isin(K['ks'], L['ks']).sum())); cell_.append(int(np.isin(K['cell'], L['cell']).sum()))
    keyhits.append(len(set(K['ksb'][hit].tolist())))
    mvs.append(mv(Vt, v))
mvs = np.array(mvs); ks_ = np.array(ks_); ksb_ = np.array(ksb_); cell_ = np.array(cell_); keyhits = np.array(keyhits)
mid = mv(Vt, vals); mlat = mv(Lt, vals)
print('N', N, 'seed 987654; ksb ge 90:', int((ksb_ >= 90).sum()), 'frac', (ksb_ >= 90).mean())
print('corr(ksb, ks)', round(np.corrcoef(ksb_, ks_)[0, 1], 4), 'corr(ksb, cell)', round(np.corrcoef(ksb_, cell_)[0, 1], 4), 'corr(ksb,|mv-mlat|)', round(np.corrcoef(ksb_, np.abs(mvs - mlat))[0, 1], 4))
out['uniform20000'] = summ(ksb_, 90)
# regression of ksb on ks
A = np.vstack([ks_, np.ones(N)]).T; coef = np.linalg.lstsq(A, ksb_, rcond=None)[0]
print('lin fit ksb = a*ks + c:', coef, 'predicted at ks=4528:', round(coef[0] * 4528 + coef[1], 2))
resid = ksb_ - (coef[0] * ks_ + coef[1]); print('resid sd', round(resid.std(), 3), 'identity resid', round(90 - (coef[0] * 4528 + coef[1]), 2), 'frac resid >= identity', (resid >= 90 - (coef[0] * 4528 + coef[1])).mean())
for lo, hi in ((4428, 4628), (4478, 4578), (4528, 10 ** 9)):
    m = (ks_ >= lo) & (ks_ <= hi)
    print(f'  condition ks in [{lo},{hi}]: n={int(m.sum())}, ksb mean {ksb_[m].mean():.3f} median {np.median(ksb_[m])} sd {ksb_[m].std(ddof=1):.3f}, ge90 {int((ksb_[m] >= 90).sum())} ({(ksb_[m] >= 90).mean():.4f})')
    out[f'cond_ks_{lo}_{hi}'] = summ(ksb_[m].tolist(), 90)
for tol in (0.25, 0.5):
    m = np.abs(mvs - mid) <= tol
    print(f'  condition |meanval - identity {mid:.3f}| <= {tol}: n={int(m.sum())}, ksb mean {ksb_[m].mean():.3f} median {np.median(ksb_[m])}, ge90 {int((ksb_[m] >= 90).sum())} ({(ksb_[m] >= 90).mean():.4f}); ks mean {ks_[m].mean():.1f}; cell mean {cell_[m].mean():.1f} ge8587 {(cell_[m] >= 8587).sum()}')
m = cell_ >= 8500
print(f'  condition cell >= 8500: n={int(m.sum())}, ksb mean {ksb_[m].mean():.3f}, ge90 {int((ksb_[m] >= 90).sum())} ({(ksb_[m] >= 90).mean():.4f}); ks mean {ks_[m].mean():.1f}')
print('identity mean value', mid, 'random mean-value dist mean', round(mvs.mean(), 3), 'sd', round(mvs.std(), 3), 'frac |mv-mlat| <= |mid-mlat|', (np.abs(mvs - mlat) <= abs(mid - mlat)).mean())
# distinct Latin keys hit
print('distinct latin keys hit: identity 76; uniform mean', round(keyhits.mean(), 3), 'sd', round(keyhits.std(ddof=1), 3), 'ge76', int((keyhits >= 76).sum()), 'of', N)
out['keyhits'] = summ(keyhits.tolist(), 76)
# type-per-key ratio
print('types per hit key: identity', 90 / 76, 'uniform', ksb_.sum() / keyhits.sum())

# 3. b-offset scan: shift every Latin b by d (mod 257), same for s scan
Kid = vm.keys(IDENT)
latk = [ksb(w) for w in forms]
def count_shift(ds, db):
    ref = np.array(sorted({(k * P + (s + ds) % P) * P + (b + db) % P for k, s, b in latk}))
    return int(np.isin(Kid['ksb'], ref).sum())
scan = {db: count_shift(0, db) for db in range(-60, 61)}
print('b scan d=-10..10', [scan[d] for d in range(-10, 11)])
arr = np.array([scan[d] for d in scan if d != 0])
print('b scan |d|<=60 excl 0: mean', round(arr.mean(), 3), 'sd', round(arr.std(ddof=1), 3), 'max', arr.max(), 'n ge 90', int((arr >= 90).sum()), 'of', len(arr))
out['bscan'] = scan
# 2D scan around 0: s shift -5..5, b shift -30..30
grid = {}
for ds in range(-5, 6):
    for db in range(-30, 31):
        grid[(ds, db)] = count_shift(ds, db)
g = np.array([v for k, v in grid.items() if k != (0, 0)])
print('2D scan ds in [-5,5], db in [-30,30] excl origin: n', len(g), 'mean', round(g.mean(), 3), 'max', g.max(), 'n ge 90', int((g >= 90).sum()))
top = sorted(grid.items(), key=lambda kv: -kv[1])[:8]; print('   top cells', top)
# the same b-scan restricted to length 6 and to lengths != 6
lens = np.array([len(w) for w in types])
def count_shift_len(db, sel):
    ref = np.array(sorted({(k * P + s % P) * P + (b + db) % P for k, s, b in latk}))
    return int((np.isin(Kid['ksb'], ref) & sel).sum())
s6 = [count_shift_len(d, lens == 6) for d in range(-30, 31)]
print('L6-only b scan d=-30..30:', s6, 'value at 0:', s6[30], 'mean excl 0', round(np.mean(s6[:30] + s6[31:]), 3), 'max excl 0', max(s6[:30] + s6[31:]))
sn6 = [count_shift_len(d, lens != 6) for d in range(-30, 31)]
print('non-L6 b scan value at 0:', sn6[30], 'mean excl 0', round(np.mean(sn6[:30] + sn6[31:]), 3), 'max excl 0', max(sn6[:30] + sn6[31:]), 'n ge', sum(1 for x in sn6[:30] + sn6[31:] if x >= sn6[30]))

# 4. token-weighted matches
hit = np.isin(Kid['ksb'], L['ksb']); tw = np.array([tc[w] for w in types])
print('token-weighted identity matches', int(tw[hit].sum()))
r = random.Random(1919); twc = []
for _ in range(300):
    v = list(range(1, 27)); r.shuffle(v)
    h = np.isin(vm.keys(v)['ksb'], L['ksb']); twc.append(int(tw[h].sum()))
out['token_weighted'] = summ(twc, int(tw[hit].sum())); print('token-weighted uniform seed 1919', out['token_weighted'])

# 5. parse sensitivity: commas break
toks2, _ = voy_tokens(comma_breaks=True); tc2 = collections.Counter(toks2); types2 = sorted(tc2)
vm2 = VMat(types2); o2 = counts(vm2, IDENT, L)
r = random.Random(1919); c2 = []
for _ in range(300):
    v = list(range(1, 27)); r.shuffle(v); c2.append(counts(vm2, v, L)['ksb'])
print('commas break: tokens', len(toks2), 'types', len(types2), 'identity', o2, 'uniform ksb', summ(c2, o2['ksb']))
out['commas_break'] = {'tokens': len(toks2), 'types': len(types2), 'obs': o2, 'ksb': summ(c2, o2['ksb'])}
# paragraph text only vs labels etc (locus type letter after the +/@/*/= marker)
pt = collections.Counter(); lt_ = collections.Counter()
for page, ln, loc, txt in rows:
    typ = loc[1] if len(loc) > 1 else '?'
    for w in words(txt):
        if re.fullmatch('[a-z]+', w):
            (pt if typ == 'P' else lt_)[w] += 1
print('locus P tokens', sum(pt.values()), 'types', len(pt), '; other loci tokens', sum(lt_.values()), 'types', len(lt_))
vmP = VMat(sorted(pt)); oP = counts(vmP, IDENT, L)
r = random.Random(1919); cP = []
for _ in range(300):
    v = list(range(1, 27)); r.shuffle(v); cP.append(counts(vmP, v, L)['ksb'])
print('paragraph-only identity', oP, 'uniform ksb', summ(cP, oP['ksb']))
out['paragraph_only'] = {'obs': oP, 'ksb': summ(cP, oP['ksb'])}
json.dump({k: v for k, v in out.items() if k != 'bscan'}, open('out_x.json', 'w'), indent=1, default=str)
