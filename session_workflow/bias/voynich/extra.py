#!/usr/bin/env python3
# Extra checks beyond (a)-(g), labelled (h):
#  h0  seed-7 replay of the earlier control (random.Random(7), shuffle of [1..26], 300 draws) - only a guess at the earlier generator
#  h1  3000 uniform permutations (seed 3000) for the (k,s,b) count, to pin the tail probability
#  h2  Latin-side anagram control: shuffle letters inside each Latin form (keeps every (k,s)), 300 draws, seed 21
#  h3  Voynich-side anagram control: shuffle letters inside each Voynich type, identity values, 300 draws, seed 22
#  h4  positional tilt: b - (k+1)s/2 for Voynich types (identity) and Latin forms; mean by length
import random, statistics, collections, json
from common import *
OUT = "<scratchpad>/bias/voynich/"
toks = load_voynich(); tokc = collections.Counter(toks); VT = sorted(tokc)
sec = load_plate(); LAT = sorted(set(f for t in sec.values() for f in forms(t)))
S = latin_sets(LAT)
def summ(obs, arr):
    a = sorted(arr)
    return dict(obs=obs, mean=round(statistics.mean(a), 3), median=statistics.median(a), sd=round(statistics.pstdev(a), 3),
                min=a[0], max=a[-1], n_ge_obs=sum(x >= obs for x in a), n=len(a))
def ksb_count(val, types=VT, Sk=S['ksb']):
    return sum(keys_all(w, val)['ksb'] in Sk for w in types)
R = {}
obs = ksb_count(ID)
# h0
rng = random.Random(7); arr = []
for _ in range(300):
    v = list(range(1, 27)); rng.shuffle(v); arr.append(ksb_count(v))
R['h0_seed7_replay'] = summ(obs, arr)
# h1
rng = random.Random(3000); arr = []
for _ in range(3000):
    v = list(range(1, 27)); rng.shuffle(v); arr.append(ksb_count(v))
R['h1_3000perms'] = summ(obs, arr)
# h2 Latin anagram
rng = random.Random(21); arr = []; arr_ks = []
for _ in range(300):
    fake = []
    for f in LAT:
        l = list(f); rng.shuffle(l); fake.append(''.join(l))
    Sf = latin_sets(fake)
    arr.append(sum(keys_all(w)['ksb'] in Sf['ksb'] for w in VT))
    arr_ks.append(len(Sf['ks']))
R['h2_latin_anagram'] = summ(obs, arr); R['h2_latin_ks_set_size_constant'] = sorted(set(arr_ks)) == [len(S['ks'])]
# h3 Voynich anagram
rng = random.Random(22); arr = []
for _ in range(300):
    c = 0
    for w in VT:
        l = list(w); rng.shuffle(l)
        if keys_all(''.join(l))['ksb'] in S['ksb']: c += 1
    arr.append(c)
R['h3_voynich_anagram'] = summ(obs, arr)
# h4 tilt
def tilt(w):
    (k, s, b), sr = key(w)
    braw = sum(i * (ord(c) - 96) for i, c in enumerate(w, 1))
    return braw - (k + 1) * sr / 2
def by_len(ws, weight=None):
    d = collections.defaultdict(list)
    for w in ws: d[len(w)].append(tilt(w))
    return {L: (len(x), round(statistics.mean(x), 2)) for L, x in sorted(d.items()) if 3 <= L <= 11}
R['h4_tilt_voynich_by_len'] = by_len(VT)
R['h4_tilt_latin_by_len'] = by_len(LAT)
R['h4_tilt_mean_voynich'] = round(statistics.mean(tilt(w) for w in VT), 3)
R['h4_tilt_mean_latin'] = round(statistics.mean(tilt(f) for f in LAT), 3)
# final-letter shares
fv = collections.Counter(w[-1] for w in VT); fl = collections.Counter(f[-1] for f in LAT)
R['h4_final_letters_voynich_top'] = [(c, n, ord(c) - 96) for c, n in fv.most_common(6)]
R['h4_final_letters_latin_top'] = [(c, n, ord(c) - 96) for c, n in fl.most_common(6)]
json.dump(R, open(OUT + 'extra_results.json', 'w'), indent=1)
print(json.dumps(R, indent=1))
