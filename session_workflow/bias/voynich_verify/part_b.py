import json, random, collections
import numpy as np
from common import *

toks, rows = voy_tokens()
tc = collections.Counter(toks)
types = sorted(tc)
sec = latin_sections()
forms = sorted({w for s in sec.values() for w in s})
formset = set(forms)
lat_by_key = collections.defaultdict(list)
for w in forms:
    k, s, b = ksb(w)
    lat_by_key[(k, s % P, b % P)].append(w)
print('distinct latin ksb keys', len(lat_by_key))
rows_ = []
for w in types:
    k, s, b = ksb(w)
    key = (k, s % P, b % P)
    if key in lat_by_key:
        rawsame = all(ksb(x) == (k, s, b) for x in lat_by_key[key])
        rows_.append(dict(type=w, tokens=tc[w], k=k, s=s, b=b, latin=lat_by_key[key], exact=w in formset, rawsame=rawsame))
rows_.sort(key=lambda r: (-r['tokens'], r['type']))
print('matches', len(rows_), 'tokens', sum(r['tokens'] for r in rows_))
print('all raw same', all(r['rawsame'] for r in rows_))
print('by length', sorted(collections.Counter(r['k'] for r in rows_).items()))
tcnt = collections.Counter(r['tokens'] for r in rows_)
print('1 token', tcnt[1], '2 tokens', tcnt[2], '>=3', sum(v for t, v in tcnt.items() if t >= 3))
ex = [r for r in rows_ if r['exact']]
sh = [r for r in rows_ if r['k'] <= 2]
print('exact', [(r['type'], r['tokens']) for r in ex], 'tokens', sum(r['tokens'] for r in ex))
print('len<=2', [(r['type'], r['tokens']) for r in sh])
print('exact or short', len({r['type'] for r in ex} | {r['type'] for r in sh}))
print('all voynich types that are latin forms', sorted(set(types) & formset))
print('voynich types len<=2', sum(1 for w in types if len(w) <= 2))
for r in rows_:
    print(f"{r['type']} {r['tokens']}t L{r['k']} -> {','.join(r['latin'])}{' [exact]' if r['exact'] else ''}")
# b4
hitkeys = collections.Counter()
for r in rows_:
    hitkeys[(r['k'], r['s'] % P, r['b'] % P)] += 1
print('latin keys hit', len(hitkeys), 'types-per-key distribution', sorted(collections.Counter(hitkeys.values()).items()))
for key, n in hitkeys.items():
    if n >= 3: print('  key', key, n, lat_by_key[key], [r['type'] for r in rows_ if (r['k'], r['s'] % P, r['b'] % P) == key])
L6lat = {k for k in lat_by_key if k[0] == 6}
print('L6 latin keys', len(L6lat), 'hit', sum(1 for k in hitkeys if k[0] == 6), 'types', sum(n for k, n in hitkeys.items() if k[0] == 6))
v6 = [w for w in types if len(w) == 6]
print('voynich L6 types', len(v6), 'distinct keys', len({(6, ksb(w)[1] % P, ksb(w)[2] % P) for w in v6}))
print('all voynich distinct keys', len({(len(w), ksb(w)[1] % P, ksb(w)[2] % P) for w in types}))
json.dump(rows_, open('out_b.json', 'w'), indent=1)
