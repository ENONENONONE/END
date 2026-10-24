#!/usr/bin/env python3
# h6: how the 90 identity matches distribute over Latin keys (types per Latin key), overall and at length 6.
import collections, json
from common import *
toks=load_voynich(); VT=sorted(set(toks)); sec=load_plate(); LAT=sorted(set(f for t in sec.values() for f in forms(t)))
latkeys=collections.defaultdict(list)
for f in LAT: latkeys[keys_all(f)['ksb']].append(f)
vk=collections.Counter(keys_all(w)['ksb'] for w in VT)
per={k:vk.get(k,0) for k in latkeys}
R=dict(n_latin_keys=len(latkeys), n_latin_keys_hit=sum(1 for v in per.values() if v), sum_hits=sum(per.values()),
       multiplicity_hist=dict(sorted(collections.Counter(per.values()).items())),
       keys_with_ge2=sorted(((v,latkeys[k]) for k,v in per.items() if v>=2), reverse=True))
L6=[k for k in latkeys if k[0]==6]
R['len6_latin_keys']=len(L6); R['len6_hit']=sum(1 for k in L6 if per[k]); R['len6_sum']=sum(per[k] for k in L6)
R['len6_types_voynich']=sum(1 for w in VT if len(w)==6); R['len6_distinct_voynich_keys']=len({keys_all(w)['ksb'] for w in VT if len(w)==6})
R['voynich_distinct_ksb_keys']=len(vk); R['voynich_types']=len(VT)
json.dump(R,open('extra3_results.json','w'),indent=1,default=str); print(json.dumps(R,indent=1,default=str))
