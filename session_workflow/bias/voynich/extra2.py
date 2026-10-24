#!/usr/bin/env python3
# h5: per-length (k,s,b) matches under the Latin-anagram (seed 21) and Voynich-anagram (seed 22) controls, same draws as extra.py; tilt SD by length.
import random, statistics, collections, json
from common import *
OUT="<scratchpad>/bias/voynich/"
toks=load_voynich(); VT=sorted(set(toks)); sec=load_plate(); LAT=sorted(set(f for t in sec.values() for f in forms(t))); S=latin_sets(LAT)
obs=collections.Counter(len(w) for w in VT if keys_all(w)['ksb'] in S['ksb'])
rng=random.Random(21); h2=collections.defaultdict(list)
for _ in range(300):
    fake=[]
    for f in LAT:
        l=list(f); rng.shuffle(l); fake.append(''.join(l))
    Sf=latin_sets(fake); c=collections.Counter(len(w) for w in VT if keys_all(w)['ksb'] in Sf['ksb'])
    for L in range(1,14): h2[L].append(c.get(L,0))
rng=random.Random(22); h3=collections.defaultdict(list)
for _ in range(300):
    c=collections.Counter()
    for w in VT:
        l=list(w); rng.shuffle(l)
        if keys_all(''.join(l))['ksb'] in S['ksb']: c[len(w)]+=1
    for L in range(1,14): h3[L].append(c.get(L,0))
def tilt(w):
    k=len(w); sr=sum(ord(c)-96 for c in w); braw=sum(i*(ord(c)-96) for i,c in enumerate(w,1)); return braw-(k+1)*sr/2
R={}
for L in range(1,12):
    tv=[tilt(w) for w in VT if len(w)==L]; tl=[tilt(f) for f in LAT if len(f)==L]
    R[L]=dict(obs=obs.get(L,0), latin_anagram_mean=round(statistics.mean(h2[L]),3), voynich_anagram_mean=round(statistics.mean(h3[L]),3),
              tilt_sd_voynich=round(statistics.pstdev(tv),2) if len(tv)>1 else None, tilt_sd_latin=round(statistics.pstdev(tl),2) if len(tl)>1 else None)
json.dump(R,open(OUT+'extra2_results.json','w'),indent=1); print(json.dumps(R,indent=1))
