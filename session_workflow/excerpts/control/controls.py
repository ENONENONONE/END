#!/usr/bin/env python3
"""Control renderings of the f1r paragraph-1 excerpt under rules R1, R2, R3.

RNG: Python's random module (Mersenne Twister), one random.Random(seed) per control;
C1 seed 101, C2 seed 102, C3 seed 103, C2 distribution seeds 1000..1999.
No network. Inputs are read-only; output goes to this script's folder.
"""
import sys, os, re, json, random, statistics, collections

SP = "<scratchpad>"
OUT = os.path.join(SP, "excerpt", "control")
sys.path.insert(0, os.path.join(SP, "vl"))
import voy  # parse(path) -> (pages, rows); words(text)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glosses import GLOSS  # RECALLED glosses

P = 257
ZL = os.path.join(SP, "vl", "ZL3b-n.txt")
PLATE = os.path.join(SP, "vl", "plate_latin.txt")
TAB = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/emerald_tablet.json"

K = {0,1,2,3,8,15,16,17,23,44,46,62,72,73,86,92,111,117,119,120,128,129,136,137,138,140,142,153,225,240,241,255,256}
CLEAN = re.compile(r"^[a-z]+$")

# ---------------------------------------------------------------- word arithmetic
def letters(w):
    return [ord(c) - 96 for c in w.lower() if "a" <= c <= "z"]

def ksb(w):
    v = letters(w)
    return (len(v), sum(v), sum(i * x for i, x in enumerate(v, 1)))

def cell(w):
    return ksb(w)[1] % P

# ---------------------------------------------------------------- tablet
T = json.load(open(TAB))
W = {int(k): v["words"] for k, v in T.items()}
def nlet(s):
    return sum(1 for c in s if c.isalpha())
def r1(w):
    return W[cell(w)][0]
def r2(w):
    ws = W[cell(w)]
    m = min(nlet(x) for x in ws)
    return next(x for x in ws if nlet(x) == m)   # shortest by letter count, ties first listed

# ---------------------------------------------------------------- plate Latin
LAT = []          # distinct lowercase forms, first-occurrence order
LAT_SEC = {}      # form -> section of first occurrence
UNCERTAIN = set()
TABULA_TEXT = None
sec = None
for line in open(PLATE, encoding="utf-8"):
    line = line.rstrip("\n")
    if not line or line.startswith("#"):
        continue
    m = re.match(r"^\[(TITLE|TABULA|PIMANDER|CAPTION)\]$", line)
    if m:
        sec = m.group(1); continue
    if sec == "TABULA" and TABULA_TEXT is None:
        TABULA_TEXT = line
    for u in re.findall(r"\[([A-Za-z]+)\]", line):
        UNCERTAIN.add(u.lower())
    for x in re.findall(r"[A-Za-z]+", line):
        x = x.lower()
        if x not in LAT_SEC:
            LAT_SEC[x] = sec; LAT.append(x)
BY_KSB = collections.defaultdict(list)
BY_KS = collections.defaultdict(list)
for x in LAT:
    k, s, b = ksb(x)
    BY_KSB[(k, s, b)].append(x)
    BY_KS[(k, s)].append(x)

def r3(w):
    k, s, b = ksb(w)
    if BY_KSB.get((k, s, b)):
        return ("ksb", list(BY_KSB[(k, s, b)]))
    if BY_KS.get((k, s)):
        return ("ks", list(BY_KS[(k, s)][:3]))
    return ("none", [])

def r3_str(res):
    kind, forms = res
    if kind == "none":
        return "—"
    j = "/".join(forms)
    return j if kind == "ksb" else "(" + j + ")"

# ---------------------------------------------------------------- manuscript
pages, rows = voy.parse(ZL)

def clean_tokens(txt):
    toks = voy.words(txt)            # commas join (comma_breaks=False), first alternative already taken
    return [t for t in toks if CLEAN.match(t)], [t for t in toks if not CLEAN.match(t)]

# excerpt: f1r lines from .1 until the line whose locus contains 'Pt' (or before the next paragraph start)
f1r = [r for r in rows if r[0] == "f1r"]
EXC = []
for i, (pg, ln, loc, txt) in enumerate(f1r):
    if i > 0 and (loc.startswith("*") or loc.startswith("@")):
        break
    EXC.append((pg, ln, loc, txt))
    if "Pt" in loc:
        break
EXC_LINES = []
EXC_DROPPED = []
for pg, ln, loc, txt in EXC:
    c, d = clean_tokens(txt)
    EXC_LINES.append(c)
    EXC_DROPPED += [(ln, t) for t in d]
COUNTS = [len(x) for x in EXC_LINES]
EXC_IDS = {(pg, ln) for pg, ln, _, _ in EXC}

# ---------------------------------------------------------------- controls
def c1(seed=101):
    ws = [w for l in EXC_LINES for w in l]
    random.Random(seed).shuffle(ws)
    out, i = [], 0
    for n in COUNTS:
        out.append(ws[i:i + n]); i += n
    return out

def c2(seed=102, rng=None):
    rng = rng or random.Random(seed)
    lets = [c for l in EXC_LINES for w in l for c in w]
    rng.shuffle(lets)
    out, i = [], 0
    for l in EXC_LINES:
        nl = []
        for w in l:
            nl.append("".join(lets[i:i + len(w)])); i += len(w)
        out.append(nl)
    return out

# C3 pool: paragraph-text lines (locus type starting with 'P') outside the excerpt, every token clean
POOL = collections.defaultdict(list)
for pg, ln, loc, txt in rows:
    if (pg, ln) in EXC_IDS:
        continue
    if not loc[1:].startswith("P"):
        continue
    c, d = clean_tokens(txt)
    if d or not c:
        continue
    POOL[len(c)].append((pg, ln, loc, c))

def c3(seed=103):
    rng = random.Random(seed)
    out, ids = [], []
    for n in COUNTS:
        pg, ln, loc, c = rng.choice(POOL[n])
        out.append(c); ids.append(f"{pg}.{ln} ({loc})")
    return out, ids

def c4_latin():
    sents = [s.strip() for s in re.split(r"\.", TABULA_TEXT) if s.strip()][:6]
    return [[x.lower() for x in re.findall(r"[A-Za-z]+", s)] for s in sents], sents

def c4_english():
    import tabula  # SENT = [(latin, english gloss), ...] in vl/tabula.py
    sents = [en for _, en in tabula.SENT[:6]]
    return [[x.lower() for x in re.findall(r"[A-Za-z]+", s)] for s in sents], sents

# ---------------------------------------------------------------- scoring / rendering
def score(lines):
    ws = [w for l in lines for w in l]
    n = len(ws)
    inK = sum(1 for w in ws if cell(w) in K)
    kinds = collections.Counter(r3(w)[0] for w in ws)
    return dict(n_words=n, in_K=inK, share_in_K=inK / n,
                r3_ksb=kinds["ksb"], r3_ks=kinds["ks"], r3_none=kinds["none"],
                share_r3_ksb=kinds["ksb"] / n, share_r3_ks=kinds["ks"] / n)

def render(lines):
    out = []
    for l in lines:
        s = sum(ksb(w)[1] for w in l)
        out.append(dict(
            words=l,
            cells=[cell(w) for w in l],
            ksb=[ksb(w) for w in l],
            R1=[r1(w) for w in l],
            R2=[r2(w) for w in l],
            R3=[r3(w) for w in l],
            line_sum=s, line_cell=s % P))
    return out

def fmt_block(name, lines, extra=None):
    o = [f"=== {name} ==="]
    if extra:
        o += [f"  {e}" for e in extra]
    for i, r in enumerate(render(lines), 1):
        o.append(f"  L{i}  sum {r['line_sum']} ≡ {r['line_cell']}{'  [K]' if r['line_cell'] in K else ''}")
        o.append("    EVA: " + " ".join(r["words"]))
        o.append("    cell: " + " ".join(str(c) + ("*" if c in K else "") for c in r["cells"]))
        o.append("    R1:  " + " | ".join(r["R1"]))
        o.append("    R2:  " + " | ".join(r["R2"]))
        o.append("    R3:  " + " | ".join(r3_str(x) for x in r["R3"]))
        o.append("    R3 gloss (RECALLED): " + " | ".join(
            "—" if k_ == "none" else ("" if k_ == "ksb" else "(") + " / ".join(GLOSS.get(f, "??" + f) for f in fs) + ("" if k_ == "ksb" else ")")
            for k_, fs in r["R3"]))
    sc = score(lines)
    o.append(f"  words {sc['n_words']} · cell in K {sc['in_K']} ({sc['share_in_K']:.3f}) · "
             f"R3 (k,s,b) {sc['r3_ksb']} ({sc['share_r3_ksb']:.3f}) · R3 (k,s) only {sc['r3_ks']} ({sc['share_r3_ks']:.3f}) · R3 none {sc['r3_none']}")
    return "\n".join(o), sc

if __name__ == "__main__":
    report = []
    js = {"K_size": len(K), "K_baseline_share": len(K) / P, "rng": "Python random.Random(seed), Mersenne Twister",
          "latin_vocab_size": len(LAT), "latin_uncertain": sorted(UNCERTAIN)}
    report.append(f"K has {len(K)} cells; uniform-cell baseline share {len(K)}/{P} = {len(K)/P:.4f}")
    report.append(f"plate-Latin vocabulary: {len(LAT)} distinct lowercase forms from TITLE+TABULA+PIMANDER+CAPTION; "
                  f"uncertain (bracketed): {sorted(UNCERTAIN)}")
    report.append(f"distinct (k,s,b) keys {len(BY_KSB)} · distinct (k,s) keys {len(BY_KS)}")
    report.append("excerpt rows used:")
    for pg, ln, loc, txt in EXC:
        report.append(f"  {pg}.{ln} [{loc}] {txt}")
    report.append(f"non-clean tokens dropped: {EXC_DROPPED}")
    report.append(f"line word counts {COUNTS}, total {sum(COUNTS)}")
    report.append("every token (line: tokens):")
    for i, l in enumerate(EXC_LINES, 1):
        report.append(f"  L{i}: " + ", ".join(l))
    report.append("")

    blocks = {}
    t, sc = fmt_block("REAL excerpt f1r.1–f1r.6", EXC_LINES); report.append(t); blocks["REAL"] = dict(lines=EXC_LINES, score=sc)
    L = c1(); t, sc = fmt_block("C1 words shuffled across the six lines (seed 101)", L); report.append(t); blocks["C1"] = dict(lines=L, score=sc)
    L = c2(); t, sc = fmt_block("C2 letters shuffled across all words, lengths kept (seed 102)", L); report.append(t); blocks["C2"] = dict(lines=L, score=sc)
    L, ids = c3(); t, sc = fmt_block("C3 six manuscript lines with the excerpt's word counts (seed 103)", L,
                                     ["source lines: " + "; ".join(ids),
                                      "pool sizes by word count: " + ", ".join(f"{n}:{len(POOL[n])}" for n in COUNTS)])
    report.append(t); blocks["C3"] = dict(lines=L, ids=ids, score=sc)
    L, sents = c4_latin(); t, sc = fmt_block("C4 TABULA first 6 sentences (Latin) read as if EVA", L,
                                             ["the TABULA section is one physical line in plate_latin.txt; its first six '.'-sentences are used as the six lines",
                                              "note: every word of C4 is itself in the plate-Latin vocabulary, so R3 (k,s,b) matches itself"])
    report.append(t); blocks["C4_latin"] = dict(lines=L, sentences=sents, score=sc)
    L, sents = c4_english(); t, sc = fmt_block("C4-EN English glosses of the same 6 sentences (vl/tabula.py SENT) read as if EVA", L,
                                               ["supplementary: the task labels C4 'English' but names the Latin TABULA; both are given"])
    report.append(t); blocks["C4_english"] = dict(lines=L, sentences=sents, score=sc)

    # C2 distribution, seeds 1000..1999
    shares, ksbs, kss = [], [], []
    for seed in range(1000, 2000):
        sc = score(c2(seed=seed))
        shares.append(sc["share_in_K"]); ksbs.append(sc["r3_ksb"]); kss.append(sc["r3_ks"])
    real = blocks["REAL"]["score"]
    def place(vals, x):
        lo = sum(1 for v in vals if v < x); eq = sum(1 for v in vals if v == x); hi = sum(1 for v in vals if v > x)
        return lo, eq, hi
    dist = {}
    for name, vals, x in [("share_in_K", shares, real["share_in_K"]), ("r3_ksb_count", ksbs, real["r3_ksb"]), ("r3_ks_count", kss, real["r3_ks"])]:
        lo, eq, hi = place(vals, x)
        hist = collections.Counter(round(v, 6) for v in vals)
        dist[name] = dict(mean=statistics.mean(vals), sd=statistics.pstdev(vals), min=min(vals), max=max(vals),
                          median=statistics.median(vals), real=x, draws_below=lo, draws_equal=eq, draws_above=hi,
                          hist=sorted(hist.items()))
    report.append("=== C2 distribution over 1000 draws (seeds 1000–1999) ===")
    n = real["n_words"]
    for name in dist:
        d = dist[name]
        report.append(f"  {name}: mean {d['mean']:.4f} sd {d['sd']:.4f} median {d['median']} min {d['min']} max {d['max']} · "
                      f"real {d['real']} · draws below {d['draws_below']}, equal {d['draws_equal']}, above {d['draws_above']}")
        if name == "share_in_K":
            report.append("    histogram (count in K of " + str(n) + " : draws): " +
                          ", ".join(f"{round(v*n)}:{c}" for v, c in d["hist"]))
        else:
            report.append("    histogram (value : draws): " + ", ".join(f"{int(v)}:{c}" for v, c in d["hist"]))
    js["blocks"] = {k: dict(v, rendered=render(v["lines"])) for k, v in blocks.items()}
    js["c2_distribution"] = dist
    # Latin forms used in any R3 rendering (for glossing)
    used = collections.OrderedDict()
    for k_, v in blocks.items():
        for l in v["lines"]:
            for w in l:
                kind, forms = r3(w)
                for f in forms:
                    used.setdefault(f, set()).add(k_)
    js["latin_forms_used"] = {f: sorted(s) for f, s in used.items()}
    report.append("")
    report.append(f"Latin forms used in R3 renderings ({len(used)}), section of first occurrence, gloss RECALLED:")
    for f in used:
        report.append(f"  {f:<14} {str(ksb(f)):<16} [{LAT_SEC[f]}]{' (uncertain reading)' if f in UNCERTAIN else ''}  {GLOSS.get(f, 'MISSING GLOSS')}")
    missing = [f for f in used if f not in GLOSS]
    report.append(f"missing glosses: {missing}")
    # R2 tie-break check: shortest by letter count vs by raw string length
    diff = [c for c in range(P) if min(W[c], key=nlet) != min(W[c], key=len)]
    report.append(f"cells where 'shortest' by letter count differs from shortest by string length: {diff}")
    open(os.path.join(OUT, "controls_report.txt"), "w").write("\n".join(report) + "\n")
    json.dump(js, open(os.path.join(OUT, "controls.json"), "w"), ensure_ascii=False, indent=1, default=list)
    print("\n".join(report))
