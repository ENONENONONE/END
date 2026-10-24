# Seed sensitivity of the band controls (Atbash and ksb), several seeds.
import random, collections
import numpy as np
from common import *
toks, rows = voy_tokens(); tc = collections.Counter(toks); types = sorted(tc)
sec = latin_sections(); forms = sorted({w for s in sec.values() for w in s})
L = latin_keysets(forms); vm = VMat(types)
lc = collections.Counter(c for w in toks for c in w)
rank = sorted('abcdefghijklmnopqrstuvwxyz', key=lambda c: (-lc[c], c))
def run(width, seed):
    r = random.Random(seed); bands = [rank[i:i + width] for i in range(0, 26, width)]
    a = []; k = []
    for _ in range(300):
        vals = list(range(1, 27))
        for bd in bands:
            vs = [ord(c) - 96 for c in bd]; r.shuffle(vs)
            for c, v in zip(bd, vs): vals[ord(c) - 97] = v
        cc = counts(vm, vals, L); a.append(cc['atb']); k.append(cc['ksb'])
    a = np.array(a); k = np.array(k)
    return round(a.mean(), 3), int((a >= 56).sum()), round(k.mean(), 3), int((k >= 90).sum())
for width, seeds in ((4, (4, 41, 42, 43, 44)), (2, (2, 21, 22, 23, 24))):
    for s in seeds: print('width', width, 'seed', s, 'atb mean, ge56, ksb mean, ge90:', run(width, s))
