# Extra: tablet-vocabulary control (real words, not Latin), local neighbourhood of the offset scan,
# and L6 detail.
import json, random, collections, re
import numpy as np
from common import *

toks, rows = voy_tokens()
tc = collections.Counter(toks)
types = sorted(tc)
sec = latin_sections()
forms = sorted({w for s in sec.values() for w in s})
L = latin_keysets(forms)
vm = VMat(types)
Kid = vm.keys(IDENT)
latlen = collections.Counter(len(w) for w in forms)
print('latin length dist', sorted(latlen.items()))

T = json.load(open('~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/emerald_tablet.json'))
eng = sorted({w.lower() for v in T.values() for w in v['words'] if re.fullmatch('[A-Za-z]+', w)} - set(forms))
bylen = collections.defaultdict(list)
for w in eng: bylen[len(w)].append(w)
short = {l: (n, len(bylen[l])) for l, n in latlen.items() if len(bylen[l]) < n}
print('tablet single words (not latin forms)', len(eng), 'lengths short of latin count', short)
r = random.Random(31337); res = collections.defaultdict(list)
for _ in range(300):
    samp = []
    for l, n in latlen.items():
        pool = bylen[l]
        samp += r.sample(pool, min(n, len(pool)))
    Le = latin_keysets(samp)
    res['n'].append(len(samp))
    res['ks'].append(int(np.isin(Kid['ks'], Le['ks']).sum()))
    res['ksb'].append(int(np.isin(Kid['ksb'], Le['ksb']).sum()))
    res['ksb_nonL6'].append(int((np.isin(Kid['ksb'], Le['ksb']) & (vm.k != 6)).sum()))
    res['ksb_L6'].append(int((np.isin(Kid['ksb'], Le['ksb']) & (vm.k == 6)).sum()))
print('tablet-vocabulary control seed 31337, sample size', set(res['n']))
for k2 in ('ks', 'ksb', 'ksb_L6', 'ksb_nonL6'):
    obsv = {'ks': 4528, 'ksb': 90, 'ksb_L6': 30, 'ksb_nonL6': 60}[k2]
    print('  ', k2, summ(res[k2], obsv))
print('   ratio ksb/ks', np.mean(res['ksb']) / np.mean(res['ks']))
# full tablet vocabulary once (all 890 minus latin), scaled
Lall = latin_keysets(eng)
print('all tablet single words:', len(eng), 'ks', int(np.isin(Kid['ks'], Lall['ks']).sum()), 'ksb', int(np.isin(Kid['ksb'], Lall['ksb']).sum()))

# local neighbourhood of the 2D offset scan
latk = [ksb(w) for w in forms]
def cs(ds, db, sel=None):
    ref = np.array(sorted({(k * P + (s + ds) % P) * P + (b + db) % P for k, s, b in latk}))
    h = np.isin(Kid['ksb'], ref)
    if sel is not None: h &= sel
    return int(h.sum())
for R_s, R_b in ((1, 5), (2, 10), (3, 15)):
    vals = [cs(a, b) for a in range(-R_s, R_s + 1) for b in range(-R_b, R_b + 1) if (a, b) != (0, 0)]
    v = np.array(vals)
    print(f'neighbourhood |ds|<={R_s}, |db|<={R_b}: n {len(v)}, mean {v.mean():.3f}, sd {v.std(ddof=1):.3f}, max {v.max()}, n>=90 {(v >= 90).sum()}')
v6 = np.array([cs(a, b, vm.k == 6) for a in range(-2, 3) for b in range(-10, 11) if (a, b) != (0, 0)])
print(f'L6 neighbourhood |ds|<=2,|db|<=10: mean {v6.mean():.3f} sd {v6.std(ddof=1):.3f} max {v6.max()} n>=30 {(v6 >= 30).sum()} of {len(v6)}')
# parity check of b-scan
print('b-shift parity effect: even d mean', np.mean([cs(0, d) for d in range(-20, 21, 2) if d]), 'odd d mean', np.mean([cs(0, d) for d in range(-19, 20, 2)]))
print('voynich b parity share even', np.mean(Kid['ksb'] % 2 == 0))

# L6 detail: voynich L6 (s) histogram near latin hit keys
v6s = collections.Counter(int(x) for x in (vm.C @ np.arange(1, 27))[vm.k == 6])
lat6 = sorted((ksb(w)[1], ksb(w)[2], w) for w in forms if len(w) == 6)
hit6 = {w for w in forms if len(w) == 6 and (6 * P + ksb(w)[1] % P) * P + ksb(w)[2] % P in set(Kid['ksb'][vm.k == 6].tolist())}
print('latin L6 forms: s, b, voynich L6 types with same s, hit?')
for s, b, w in lat6:
    print('  ', w, s, b, v6s[s], 'HIT' if w in hit6 else '')
