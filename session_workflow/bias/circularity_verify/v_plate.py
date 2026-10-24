"""Extra control for step 5: the plate's own vocabulary vs the plate words that were added.
Exact counts, no RNG."""
import json, os, re
from fractions import Fraction
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
PL = "<scratchpad>/vl/plate_latin.txt"
P = 257
K = {0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120,
     128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256}


def ls(w):
    return sum(ord(c) - 64 for c in w.upper() if 'A' <= c <= 'Z') % P


sec = {}
cur = None
for line in open(PL, encoding="utf-8"):
    line = line.rstrip("\n")
    if line.startswith("#") or not line.strip():
        continue
    m = re.fullmatch(r"\[([A-Z]+)\]", line.strip())
    if m:
        cur = m.group(1); sec[cur] = ""; continue
    sec[cur] += " " + line
text = " ".join(sec.values())
text_nob = re.sub(r"\[[^\]]*\]", lambda m: m.group()[1:-1], text)
toks = re.findall(r"[A-Za-z]+", text_nob)
TOK = [t.upper() for t in toks]
vocab = sorted(set(TOK))
added = json.load(open(os.path.join(HERE, "v_added.json")))
step5 = [(c, w) for s, c, w in added if s == 5]
joined = " " + " ".join(TOK) + " "
verbatim = [(c, w) for c, w in step5 if (" " + w + " ") in joined]
single_verbatim = [(c, w) for c, w in verbatim if " " not in w]
print("plate tokens", len(TOK), "distinct", len(vocab))
kv = [w for w in vocab if ls(w) in K]
print(f"distinct plate words in K: {len(kv)}/{len(vocab)} = {len(kv)/len(vocab):.4f}")
print(f"step-5 additions found verbatim in plate text: {len(verbatim)}/{len(step5)}")
print("   ", "; ".join(f"{w} {c}" for c, w in verbatim))
sv = {w for _, w in single_verbatim}
kin = [w for w in sv if ls(w) in K]
kout = [w for w in vocab if w not in sv and ls(w) in K]
print(f"single-word verbatim additions in K: {len(kin)}/{len(sv)} {sorted(kin)}")
print(f"plate distinct words NOT added, in K: {len(kout)}/{len(vocab)-len(sv)} = {len(kout)/(len(vocab)-len(sv)):.4f}")
# hypergeometric: P(>= kin of the sv drawn from vocab with len(kv) K-words)
N, Kc, n, x = len(vocab), len(kv), len(sv), len(kin)
ph = sum(comb(Kc, j) * comb(N - Kc, n - j) for j in range(x, min(Kc, n) + 1)) / comb(N, n)
print(f"hypergeometric P(X >= {x}) drawing {n} of {N} distinct plate words with {Kc} in K: {ph:.4f}; expected {n*Kc/N:.3f}")
nv = [(c, w) for c, w in step5 if (c, w) not in verbatim]
print(f"step-5 additions not verbatim in plate text: {len(nv)}")
print("   ", "; ".join(f"{w} {c}{'*' if c in K else ''}" for c, w in nv))
# chosen form vs plate form for normalised plate words (the pairs are listed by hand, from the plate text)
PAIRS = [("NEPTUNE", "NEPTUNO"), ("VULCAN", "VULCANO"), ("JUNO", "IUNONI"), ("ALCHYMIA", "ALCHYMIAE"),
         ("IGNIS", "IGNE"), ("HENRIC KHUNRATH", "HENRICUS KHUNRATH"), ("HUMIDUM RADICALE", "HUMIDO RADICALI"),
         ("CONFLAGRATION", "CONFLAGRATIONEM"), ("OPERATIO SOLIS", "OPERATIONE SOLIS"),
         ("LAPIS PHILOSOPHORUM", "LAPIDIS PHILOSOPHORUM"), ("RERUM NATURA", "RERUM NATURA"),
         ("PIMANDER", "PIMANDER"), ("MERCURIUS", "MERCURIUS")]
for a, b in PAIRS:
    print(f"   chosen {a} {ls(a)}{'*' if ls(a) in K else ''}   plate form {b} {ls(b)}{'*' if ls(b) in K else ''}")
