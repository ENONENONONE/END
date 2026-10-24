import json, random, collections
import numpy as np
from common import *

toks, rows = voy_tokens()
tc = collections.Counter(toks)
types = sorted(tc)
sec = latin_sections()
lat_tokens = [w for s in sec.values() for w in s]
forms = sorted(set(lat_tokens))
print('voynich tokens', len(toks), 'types', len(types))
print('latin tokens', len(lat_tokens), 'forms', len(forms), {k: len(set(v)) for k, v in sec.items()})
print('latin letters token', sum(map(len, lat_tokens)), 'type', sum(map(len, forms)))
L = latin_keysets(forms)
vm = VMat(types)
obs = counts(vm, IDENT, L)
print('identity', obs)

# raw-key check (no mod) at identity
latraw = {ksb(w) for w in forms}
raw_hits = [w for w in types if ksb(w) in latraw]
print('raw (k,s,b) identity', len(raw_hits))
latraw_ks = {ksb(w)[:2] for w in forms}
print('raw (k,s) identity', sum(1 for w in types if ksb(w)[:2] in latraw_ks))
latraw_s = {ksb(w)[1] for w in forms}
print('raw s identity', sum(1 for w in types if ksb(w)[1] in latraw_s))

def perms(seed, n):
    r = random.Random(seed); out = []
    for _ in range(n):
        v = list(range(1, 27)); r.shuffle(v); out.append(v)
    return out

res = {}
for seed, n in ((1919, 300), (7, 300), (424242, 3000)):
    P_ = perms(seed, n)
    C = collections.defaultdict(list)
    nid = 0
    for v in P_:
        if v == IDENT: nid += 1
        c = counts(vm, v, L)
        for k2, x in c.items(): C[k2].append(x)
    res[seed] = {k2: summ(C[k2], obs[k2]) for k2 in C}
    res[seed]['identity_draws'] = nid
    print('seed', seed, n)
    for k2 in ('cell', 'ks', 'ksb', 'rev', 'atb'):
        print('  ', k2, res[seed][k2])
json.dump({'obs': obs, 'res': {str(k): v for k, v in res.items()}}, open('out_a.json', 'w'), indent=1)
