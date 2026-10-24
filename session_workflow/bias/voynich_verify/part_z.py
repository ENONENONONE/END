# Extra: parity structure of b, and a parity-preserving alphabet control.
import json, random, collections
import numpy as np
from common import *

toks, rows = voy_tokens()
tc = collections.Counter(toks)
types = sorted(tc)
sec = latin_sections()
forms = sorted({w for s in sec.values() for w in s})
L = latin_keysets(forms)
vm = VMat(types)
obs = counts(vm, IDENT, L)

# b parity given (k, s parity), identity values, both sides (raw b)
def par_table(ws):
    t = collections.Counter()
    for w in ws:
        k, s, b = ksb(w); t[(s % 2, b % 2)] += 1
    n = sum(t.values())
    return {f's{a}b{c}': round(t[(a, c)] / n, 4) for a in (0, 1) for c in (0, 1)}
print('Voynich (s parity, b parity) shares', par_table(types))
print('Latin   (s parity, b parity) shares', par_table(forms))
# odd-position letter parity: share of letters at odd positions that have odd value
def oddshare(ws, pos_parity):
    n = o = 0
    for w in ws:
        for i, c in enumerate(w, 1):
            if i % 2 == pos_parity:
                n += 1; o += (ord(c) - 96) % 2
    return round(o / n, 4)
print('share of odd-valued letters at odd positions: voynich', oddshare(types, 1), 'latin', oddshare(forms, 1))
print('share of odd-valued letters at even positions: voynich', oddshare(types, 0), 'latin', oddshare(forms, 0))
vow = set('aeiou')
print('EVA vowel-like glyphs a e i o y values', [ord(c) - 96 for c in 'aeioy'], '; Latin vowels a e i o u', [ord(c) - 96 for c in 'aeiou'])
# alternation: share of adjacent pairs that change value parity
def alt(ws):
    n = a = 0
    for w in ws:
        for x, y in zip(w, w[1:]):
            n += 1; a += ((ord(x) - 96) % 2) != ((ord(y) - 96) % 2)
    return round(a / n, 4)
print('adjacent parity change share: voynich', alt(types), 'latin', alt(forms))

# fraction of (k,s)-matched pairs with equal b, and equal b parity (raw values; mod 257 keys)
def pair_stats(vals):
    k, s, b = vm.raw(vals)
    lat = collections.defaultdict(list)
    for w in forms:
        kk, ss, bb = ksb(w); lat[(kk, ss % P)].append(bb % P)
    npair = eq = eqpar = 0
    for kk, ss, bb in zip(k.tolist(), s.tolist(), b.tolist()):
        for lb in lat.get((kk, ss % P), ()):
            npair += 1; eq += (bb % P) == lb; eqpar += ((bb % P) % 2) == (lb % 2)
    return npair, eq, eqpar
n, e, ep = pair_stats(IDENT)
print(f'identity: (k,s)-matched pairs {n}, equal b {e} ({e/n:.5f}), equal b parity {ep} ({ep/n:.4f})')
r = random.Random(1919); rs = []
for _ in range(100):
    v = list(range(1, 27)); r.shuffle(v); rs.append(pair_stats(v))
a = np.array(rs, dtype=float)
print(f'uniform perms (seed 1919, first 100): pairs mean {a[:,0].mean():.1f}; equal-b rate mean {np.mean(a[:,1]/a[:,0]):.5f}; equal-parity rate mean {np.mean(a[:,2]/a[:,0]):.4f}, sd {np.std(a[:,2]/a[:,0]):.4f}, share >= identity {(a[:,2]/a[:,0] >= ep/n).mean():.3f}')

# parity-preserving permutation control: odd letters get a shuffle of the odd values, even letters of the even values
def parity_perms(seed, n):
    r = random.Random(seed); out = []
    oddL = [i for i in range(26) if (i + 1) % 2 == 1]; evenL = [i for i in range(26) if (i + 1) % 2 == 0]
    for _ in range(n):
        vals = list(range(1, 27))
        ov = [i + 1 for i in oddL]; ev = [i + 1 for i in evenL]; r.shuffle(ov); r.shuffle(ev)
        for i, x in zip(oddL, ov): vals[i] = x
        for i, x in zip(evenL, ev): vals[i] = x
        out.append(vals)
    return out
C = collections.defaultdict(list)
for v in parity_perms(1313, 300):
    for k2, x in counts(vm, v, L).items(): C[k2].append(x)
print('parity-preserving perms seed 1313:')
for k2 in ('cell', 'ks', 'ksb', 'rev', 'atb'): print('   ', k2, summ(C[k2], obs[k2]))
ks_ = np.array(C['ks']); ksb_ = np.array(C['ksb'])
print('   ksb/ks ratio of means', ksb_.mean() / ks_.mean())
# parity-preserving, larger sample, conditioned on ks near 4528
PP = parity_perms(1414, 5000); ks2 = []; ksb2 = []
for v in PP:
    K = vm.keys(v); ks2.append(int(np.isin(K['ks'], L['ks']).sum())); ksb2.append(int(np.isin(K['ksb'], L['ksb']).sum()))
ks2 = np.array(ks2); ksb2 = np.array(ksb2)
print('parity-preserving seed 1414 x5000: ksb', summ(ksb2.tolist(), 90))
m = (ks2 >= 4428) & (ks2 <= 4628)
print(f'   conditioned ks in [4428,4628]: n {m.sum()}, ksb mean {ksb2[m].mean():.3f}, median {np.median(ksb2[m])}, ge90 {(ksb2[m] >= 90).sum()} ({(ksb2[m] >= 90).mean():.4f})')
coef = np.polyfit(ks2, ksb2, 1); pred = np.polyval(coef, 4528); res = ksb2 - np.polyval(coef, ks2)
print(f'   linear fit predicted at 4528: {pred:.2f}; identity residual {90 - pred:.2f}; share of residuals >= it {(res >= 90 - pred).mean():.4f}')
# parity-flipping control: odd letters get even values and vice versa (a mirror test)
def flip_perms(seed, n):
    r = random.Random(seed); out = []
    oddL = [i for i in range(26) if (i + 1) % 2 == 1]; evenL = [i for i in range(26) if (i + 1) % 2 == 0]
    for _ in range(n):
        vals = [0] * 26
        ov = [i + 1 for i in oddL]; ev = [i + 1 for i in evenL]; r.shuffle(ov); r.shuffle(ev)
        for i, x in zip(oddL, ev): vals[i] = x
        for i, x in zip(evenL, ov): vals[i] = x
        out.append(vals)
    return out
C3 = [counts(vm, v, L)['ksb'] for v in flip_perms(1515, 300)]
C3ks = [counts(vm, v, L)['ks'] for v in flip_perms(1515, 300)]
print('parity-swapping perms seed 1515: ksb', summ(C3, 90), 'ks mean', np.mean(C3ks), 'ratio', np.mean(C3) / np.mean(C3ks))
