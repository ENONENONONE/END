"""Grapheme-to-phoneme aligner for CMU dict (first pronunciation).

DP over (letters consumed, phonemes consumed). Units are graphemes of 1-3 letters,
each with a list of allowed phoneme sequences and a cost. A single letter may map
to nothing (silent) at a cost; a silent 'gh' digraph is its own unit. Letters inside
a multi-letter grapheme share that grapheme's phonemes and are NOT silent.

Conventions (stated, fixed before running):
  * digraphs/trigraphs that share phonemes (not silent): ph sh th ch ng ck gh(->F)
    wh(->W, HH W) qu cq tch dg dj sc(->SH) sch(->SH, S K) tsch(->CH) cch(->K) ch(->HH), doubled consonants (bb cc dd ... zz),
    vowel pairs, vowel+w (aw ew ow), vowel+y (ay ey oy uy), vowel+r (->ER).
  * 'gh' -> nothing is a silent-gh unit (both letters silent, category 'gh').
  * 'gh' -> G is g->G plus silent h (ghost); 'wh' -> HH is silent w plus h->HH (whole).
  * vowel letters may be silent (cost 0.6; final e 0.3); y silent 0.8.
  * consonant silent cost 1.0; silent gh unit 1.5; secondary phoneme of a letter 0.1;
    fallback letter->any phoneme 3.0; phoneme with no letter (insertion) 3.0.
"""

VOWEL_PH = ["AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"]
VOWEL_L = set("aeiou")
CONS_L = set("bcdfghjklmnpqrstvwxz")          # y excluded (semi-vowel)
SILENT_SET = set("bcdghklnpstw")               # the test's silent consonants (+ 'gh' unit)

SIL_CONS = 1.0
SIL_GH = 1.5
SIL_VOW = 0.6
SIL_FINAL_E = 0.3
SIL_Y = 0.8
FALLBACK = 3.0
INSERT = 3.0

OPTS = {}   # grapheme -> list of (seq tuple, cost, tag)


def add(g, seq, cost, tag="map"):
    OPTS.setdefault(g, []).append((tuple(seq.split()) if isinstance(seq, str) else tuple(seq), cost, tag))


# ---- single consonants: primary cost 0, secondary 0.1, silent 1.0
CONS_SINGLE = {
    "b": ["B", ("P", .1)],
    "c": ["K", ("S", .1), ("CH", .1), ("SH", .1), ("K S", .1)],
    "d": ["D", ("T", .1), ("JH", .1)],
    "f": ["F", ("V", .1)],
    "g": ["G", ("JH", .1), ("ZH", .1), ("K", .1)],
    "h": ["HH"],
    "j": ["JH", ("Y", .1), ("HH", .1), ("ZH", .1)],
    "k": ["K"],
    "l": ["L", ("AH L", .1)],
    "m": ["M", ("AH M", .1)],
    "n": ["N", ("NG", .1), ("AH N", .1)],
    "p": ["P"],
    "q": ["K", "K W"],
    "r": ["R", ("ER", .1)],
    "s": ["S", ("Z", .1), ("SH", .1), ("ZH", .1)],
    "t": ["T", ("SH", .1), ("CH", .1), ("D", .1), ("ZH", .1), ("TH", .1)],
    "v": ["V", ("F", .1)],
    "w": ["W", ("V", .1)],
    "x": ["K S", ("G Z", .1), ("Z", .1), ("K SH", .1), ("S", .1), ("G ZH", .1), ("HH", .2)],
    "z": ["Z", ("S", .1), ("ZH", .1), ("T S", .1)],
}
for L, lst in CONS_SINGLE.items():
    for o in lst:
        if isinstance(o, tuple):
            add(L, o[0], o[1])
        else:
            add(L, o, 0.0)
    add(L, (), SIL_CONS, "silent")
    # geminate: doubled letter shares the single letter's phonemes
    for o in lst:
        if isinstance(o, tuple):
            add(L + L, o[0], o[1])
        else:
            add(L + L, o, 0.0)
add("cc", "K S", 0.0)
add("gg", "G JH", 0.0)

# ---- vowels
for v in "aeiou":
    for ph in VOWEL_PH:
        add(v, (ph,), 0.1)
    add(v, (), SIL_VOW, "silentv")
for v in "ueio":
    for ph in VOWEL_PH:
        add(v, ("Y", ph), 0.2)
for v in "ou":
    for ph in VOWEL_PH:
        add(v, ("W", ph), 0.2)
add("u", "W", 0.2)
add("i", "Y", 0.2)
add("e", "Y", 0.2)
# y
add("y", "Y", 0.0)
for ph in VOWEL_PH:
    add("y", (ph,), 0.1)
add("y", (), SIL_Y, "silentv")

# ---- vowel digraphs
for a in "aeiou":
    for b in "aeiouwy":
        g = a + b
        for ph in VOWEL_PH:
            add(g, (ph,), 0.1)
        add(g, ("Y", "UW"), 0.15)
    add(a + "r", "ER", 0.1)
add("yr", "ER", 0.1)

# ---- consonant digraphs / trigraphs (shared phonemes, not silent)
add("ph", "F", 0.0); add("ph", "V", 0.1)
add("sh", "SH", 0.0); add("sh", "ZH", 0.1)
add("th", "TH", 0.0); add("th", "DH", 0.0)
add("ch", "CH", 0.0); add("ch", "K", 0.0); add("ch", "SH", 0.0); add("ch", "JH", 0.1)
add("ng", "NG", 0.0); add("ng", "NG G", 0.0); add("ng", "NG K", 0.1)
add("ck", "K", 0.0)
add("gh", "F", 0.0)
add("gh", (), SIL_GH, "silentgh")
add("wh", "W", 0.0); add("wh", "HH W", 0.0)
add("qu", "K W", 0.0); add("qu", "K", 0.0)
add("cq", "K", 0.0)
add("tch", "CH", 0.0)
add("dg", "JH", 0.0)
add("dj", "JH", 0.0)
add("sc", "SH", 0.1)
add("sch", "SH", 0.0); add("sch", "S K", 0.0)
add("tsch", "CH", 0.0)
add("cch", "K", 0.0)
add("ch", "HH", 0.1)

# index options by first phoneme
IDX = {}
for g, lst in OPTS.items():
    d = {"_empty": []}
    for seq, c, tag in lst:
        if len(seq) == 0:
            d["_empty"].append((seq, c, tag))
        else:
            d.setdefault(seq[0], []).append((seq, c, tag))
    IDX[g] = d

INF = float("inf")


def align(word, phones):
    """Return (cost, steps). steps: list of (letter_start, letter_end, phones_tuple, tag)."""
    n, m = len(word), len(phones)
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            c = cost[i][j]
            if c == INF:
                continue
            if j < m:  # insertion (phoneme with no letter)
                nc = c + INSERT
                if nc < cost[i][j + 1] - 1e-12:
                    cost[i][j + 1] = nc
                    back[i][j + 1] = (i, j, i, i, (phones[j],), "ins")
            if i == n:
                continue
            ph0 = phones[j] if j < m else None
            for L in (1, 2, 3, 4):
                if i + L > n:
                    break
                g = word[i:i + L]
                d = IDX.get(g)
                if d is None:
                    continue
                cands = list(d["_empty"])
                if ph0 is not None:
                    cands += d.get(ph0, [])
                for seq, cc, tag in cands:
                    k = len(seq)
                    if k and tuple(phones[j:j + k]) != seq:
                        continue
                    if g == "e" and k == 0 and i == n - 1:
                        cc = SIL_FINAL_E
                    nc = c + cc
                    if nc < cost[i + L][j + k] - 1e-12:
                        cost[i + L][j + k] = nc
                        back[i + L][j + k] = (i, j, i, i + L, seq, tag)
            # fallback: single letter -> any single phoneme
            if ph0 is not None:
                nc = c + FALLBACK
                if nc < cost[i + 1][j + 1] - 1e-12:
                    cost[i + 1][j + 1] = nc
                    back[i + 1][j + 1] = (i, j, i, i + 1, (ph0,), "fallback")
    steps = []
    i, j = n, m
    while (i, j) != (0, 0):
        pi, pj, a, b, seq, tag = back[i][j]
        steps.append((a, b, seq, tag))
        i, j = pi, pj
    steps.reverse()
    return cost[n][m], steps


def silent_letters(word, steps):
    """Return list of (index, letter, category) for silent consonants in SILENT_SET (+gh unit),
    list of other silent consonants (index, letter), and set of silent letter indices overall."""
    sil = []
    other = []
    allsil = set()
    for a, b, seq, tag in steps:
        if tag == "silent":
            allsil.add(a)
            ch = word[a]
            if ch in SILENT_SET:
                sil.append((a, ch, ch))
            else:
                other.append((a, ch))
        elif tag == "silentgh":
            for t in range(a, b):
                allsil.add(t)
                sil.append((t, word[t], "gh"))
        elif tag == "silentv":
            allsil.add(a)
    return sil, other, allsil


def render(word, steps):
    out = []
    for a, b, seq, tag in steps:
        g = word[a:b] if b > a else "_"
        p = " ".join(seq) if seq else "-"
        mark = {"silent": "*", "silentgh": "*", "fallback": "!", "ins": "+", "silentv": ""}.get(tag, "")
        out.append(f"{g}{mark}:{p}")
    return " | ".join(out)
