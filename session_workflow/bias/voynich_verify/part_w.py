# Extra: raw-key (no mod 257) control counts, and tilt of the tablet vocabulary.
import json, random, collections, re
import numpy as np
from common import *
toks, rows = voy_tokens(); tc = collections.Counter(toks); types = sorted(tc)
sec = latin_sections(); forms = sorted({w for s in sec.values() for w in s})
vm = VMat(types)
latraw = np.array(sorted({(k * 4096 + s) * 65536 + b for k, s, b in (ksb(w) for w in forms)}))
L = latin_keysets(forms)
r = random.Random(1919); modc = []; rawc = []
for _ in range(300):
    v = list(range(1, 27)); r.shuffle(v)
    k, s, b = vm.raw(v)
    rawc.append(int(np.isin((k * 4096 + s) * 65536 + b, latraw).sum()))
    modc.append(counts(vm, v, L)['ksb'])
print('uniform seed 1919: mod-257 key mean', np.mean(modc), 'raw key mean', np.mean(rawc), 'raw ge90', sum(x >= 90 for x in rawc), 'mod ge90', sum(x >= 90 for x in modc))
T = json.load(open('~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/emerald_tablet.json'))
eng = sorted({w.lower() for v in T.values() for w in v['words'] if re.fullmatch('[A-Za-z]+', w)} - set(forms))
t = lambda w: ksb(w)[2] - (len(w) + 1) * ksb(w)[1] / 2
print('tilt mean: tablet single words', round(np.mean([t(w) for w in eng]), 3), 'latin', round(np.mean([t(w) for w in forms]), 3), 'voynich', round(np.mean([t(w) for w in types]), 3))
for l in (5, 6, 7):
    print('  L', l, 'tablet', round(np.mean([t(w) for w in eng if len(w) == l]), 2), 'latin', round(np.mean([t(w) for w in forms if len(w) == l]), 2), 'voynich', round(np.mean([t(w) for w in types if len(w) == l]), 2))
