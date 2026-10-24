# Extras h1-h5, own seeds, plus replay of the investigator's seeds for exact comparison.
import json, random, collections
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
lens = np.array([len(w) for w in types])

def perms(seed, n):
    r = random.Random(seed); o = []
    for _ in range(n):
        v = list(range(1, 27)); r.shuffle(v); o.append(v)
    return o

def bylen(hitmask):
    return collections.Counter(lens[hitmask].tolist())

Kid = vm.keys(IDENT)
obs_len = bylen(np.isin(Kid['ksb'], L['ksb']))

# h1 Latin anagram
r = random.Random(2121); h1 = []; h1len = collections.Counter()
for _ in range(300):
    af = []
    for w in forms:
        l = list(w); r.shuffle(l); af.append(''.join(l))
    La = latin_keysets(af)
    hit = np.isin(Kid['ksb'], La['ksb']); h1.append(int(hit.sum())); h1len.update(bylen(hit))
out['h1'] = summ(h1, obs['ksb']); print('h1 latin anagram seed 2121', out['h1'])
# h2 Voynich anagram
r = random.Random(2222); h2 = []; h2len = collections.Counter()
for _ in range(300):
    at = []
    for w in types:
        l = list(w); r.shuffle(l); at.append(''.join(l))
    va = VMat(at)
    hit = np.isin(va.keys(IDENT)['ksb'], L['ksb']); h2.append(int(hit.sum())); h2len.update(bylen(hit))
out['h2'] = summ(h2, obs['ksb']); print('h2 voynich anagram seed 2222', out['h2'])
# uniform perms by length
uni = perms(1919, 300); ulen = collections.Counter(); uks = []; uksb = []
for v in uni:
    K = vm.keys(v); hit = np.isin(K['ksb'], L['ksb']); ulen.update(bylen(hit))
    uksb.append(int(hit.sum())); uks.append(int(np.isin(K['ks'], L['ks']).sum()))
print('h3 by length: L obs / latin-anagram / voynich-anagram / uniform')
out['h3'] = {}
for l in range(1, 12):
    row = (obs_len[l], round(h1len[l] / 300, 3), round(h2len[l] / 300, 3), round(ulen[l] / 300, 3))
    out['h3'][l] = row; print('  L', l, row)
print('   total >11 obs', sum(v for k, v in obs_len.items() if k > 11))
# h4 ratios
print('h4 identity', 90 / 4528, 'uniform', np.mean(uksb) / np.mean(uks), 'latin anagram', np.mean(h1) / 4528, 'voynich anagram', np.mean(h2) / 4528)
out['h4'] = dict(identity=90 / 4528, uniform=float(np.mean(uksb) / np.mean(uks)), lat_anag=float(np.mean(h1) / 4528), voy_anag=float(np.mean(h2) / 4528))
# h5 tilt
def tilt(w):
    k, s, b = ksb(w); return b - (k + 1) * s / 2
vt = np.array([tilt(w) for w in types]); lt = np.array([tilt(w) for w in forms])
print('h5 tilt mean voynich', round(vt.mean(), 3), 'latin', round(lt.mean(), 3))
for l in range(5, 10):
    a = np.array([tilt(w) for w in types if len(w) == l]); b = np.array([tilt(w) for w in forms if len(w) == l])
    print('   L', l, round(a.mean(), 2), round(a.std(), 2), '|', round(b.mean(), 2), round(b.std(), 2), len(a), len(b))
fv = collections.Counter(w[-1] for w in types).most_common(4); fl = collections.Counter(w[-1] for w in forms).most_common(4)
print('   finals voynich', fv, 'latin', fl)

# Replay of the investigator's own seeds (exact-comparison only)
print('--- replay seed 20260919')
C = collections.defaultdict(list)
for v in perms(20260919, 300):
    for k2, x in counts(vm, v, L).items(): C[k2].append(x)
for k2 in ('cell', 'ks', 'ksb', 'rev', 'atb'):
    a = np.array(C[k2]); print('  ', k2, round(a.mean(), 3), np.median(a), 'sd0', round(a.std(), 3), 'sd1', round(a.std(ddof=1), 3), a.min(), a.max(), 'ge', int((a >= obs[k2]).sum()))
a = []
for v in perms(3000, 3000):
    a.append(counts(vm, v, L)['ksb'])
a = np.array(a); print('--- replay seed 3000 x3000 ksb', round(a.mean(), 3), np.median(a), round(a.std(), 3), a.min(), a.max(), int((a >= 90).sum()))
json.dump(out, open('out_h.json', 'w'), indent=1)
