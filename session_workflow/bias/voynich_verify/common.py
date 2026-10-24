# Independent re-implementation of the Voynich / plate-Latin key-matching exercise.
# Only voy.parse and voy.words are imported, as the task permits.
import sys, re, collections, random
import numpy as np
VL = "<scratchpad>/vl/"
sys.path.insert(0, VL)
from voy import parse, words

P = 257

def voy_tokens(comma_breaks=False, path=VL + "ZL3b-n.txt"):
    pages, rows = parse(path)
    toks = []
    for page, ln, loc, txt in rows:
        for w in words(txt, comma_breaks=comma_breaks):
            if re.fullmatch('[a-z]+', w):
                toks.append(w)
    return toks, rows

def latin_sections(path=VL + "plate_latin.txt"):
    sec = collections.OrderedDict(); cur = None
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        m = re.fullmatch(r'\[(TITLE|TABULA|PIMANDER|CAPTION)\]', line.strip())
        if m:
            cur = m.group(1); sec[cur] = []; continue
        sec[cur].extend(re.findall('[a-z]+', line.lower()))
    return sec

def ksb(w, vals=None):
    """raw (k, s, b); vals maps letter index 0..25 -> value; identity if None."""
    k = len(w); s = 0; b = 0
    for i, c in enumerate(w, 1):
        v = (ord(c) - 96) if vals is None else vals[ord(c) - 97]
        s += v; b += i * v
    return k, s, b

class VMat:
    """Matrix form of a list of types: count matrix C and position-weight matrix B (26 cols)."""
    def __init__(self, types):
        self.types = list(types)
        n = len(self.types)
        self.C = np.zeros((n, 26), dtype=np.int64)
        self.B = np.zeros((n, 26), dtype=np.int64)
        self.k = np.zeros(n, dtype=np.int64)
        for r, w in enumerate(self.types):
            self.k[r] = len(w)
            for i, c in enumerate(w, 1):
                j = ord(c) - 97
                self.C[r, j] += 1; self.B[r, j] += i
    def raw(self, vals):
        v = np.asarray(vals, dtype=np.int64)
        return self.k, self.C @ v, self.B @ v
    def keys(self, vals):
        k, s, b = self.raw(vals)
        fwd_s = s % P; fwd_b = b % P
        rev_b = ((k + 1) * s - b) % P
        at_s = (27 * k - s) % P
        at_b = (27 * k * (k + 1) // 2 - b) % P
        enc = lambda a, bb, c: (a * P + bb) * P + c
        return {
            'cell': fwd_s,
            'ks': k * P + fwd_s,
            'ksb': enc(k, fwd_s, fwd_b),
            'rev': enc(k, fwd_s, rev_b),
            'atb': enc(k, at_s, at_b),
        }

def latin_keysets(forms):
    ident = list(range(1, 27))
    cells = set(); ks = set(); ksb_ = set()
    for w in forms:
        k, s, b = ksb(w)
        cells.add(s % P); ks.add(k * P + s % P); ksb_.add((k * P + s % P) * P + b % P)
    return {'cell': np.array(sorted(cells)), 'ks': np.array(sorted(ks)), 'ksb': np.array(sorted(ksb_))}

def counts(vm, vals, L, mask=None):
    K = vm.keys(vals)
    out = {}
    for name in ('cell', 'ks', 'ksb', 'rev', 'atb'):
        ref = L['cell'] if name == 'cell' else L['ks'] if name == 'ks' else L['ksb']
        hit = np.isin(K[name], ref)
        if mask is not None:
            hit = hit & mask
        out[name] = int(hit.sum())
    return out

def summ(xs, obs):
    a = np.array(xs, dtype=float)
    return dict(mean=round(float(a.mean()), 3), median=float(np.median(a)), sd=round(float(a.std(ddof=1)), 3),
                min=int(a.min()), max=int(a.max()), p95=float(np.percentile(a, 95)),
                ge_obs=int((a >= obs).sum()), n=len(a), obs=obs)

IDENT = list(range(1, 27))
