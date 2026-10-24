# Independent recomputation of the f1r paragraph-1 renderings (R1, R2, R3).
# No random generator is used anywhere in this script.
import re, json, collections, sys

SP = "<scratchpad>/"
ZL = SP + "vl/ZL3b-n.txt"
LAT = SP + "vl/plate_latin.txt"
TAB = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/emerald_tablet.json"
P = 257
K = {0,1,2,3,8,15,16,17,23,44,46,62,72,73,86,92,111,117,119,120,128,129,136,137,138,140,142,153,225,240,241,255,256}

def ksb(w):
    vals = [ord(c) - 64 for c in w.upper() if 'A' <= c <= 'Z']
    return len(vals), sum(vals), sum((i + 1) * v for i, v in enumerate(vals))

def nletters(w):
    return sum(1 for c in w.upper() if 'A' <= c <= 'Z')

# ---- ZL: raw lines of folio f1r ----
raw = []
for line in open(ZL, encoding='utf-8', errors='replace'):
    m = re.match(r'^<(f1r)\.(\d+),([^>]*)>\s*(.*)$', line.rstrip('\n'))
    if m:
        raw.append((int(m.group(2)), m.group(3), m.group(4)))

# paragraph 1: from line 1 up to and including first line whose locus contains 'Pt',
# or stop before the next line whose locus starts a paragraph ('*P' or '@P')
para = []
for i, (ln, loc, txt) in enumerate(raw):
    if i > 0 and (loc.startswith('*P') or loc.startswith('@P')):
        break
    para.append((ln, loc, txt))
    if 'Pt' in loc:
        break

def clean(txt, comma='join', alt=0):
    t = re.sub(r'<![^>]*>', '', txt)          # inline comments
    t = re.sub(r'<[^>]*>', '.', t)            # <%> <$> etc. as breaks
    t = re.sub(r'\[([^\]]*)\]', lambda m: m.group(1).split(':')[alt], t)
    t = re.sub(r'@\d+;', '?', t)
    t = t.replace('{', '').replace('}', '').replace("'", '')
    t = t.replace(',', '' if comma == 'join' else '.')
    toks = [w for w in t.split('.') if w]
    return toks

T = json.load(open(TAB, encoding='utf-8'))
W = {int(k): v['words'] for k, v in T.items()}

# ---- Latin forms ----
lat_text = []
for line in open(LAT, encoding='utf-8'):
    if line.startswith('#'): continue
    s = line.strip()
    if re.fullmatch(r'\[[A-Z]+\]', s): continue   # section headers
    lat_text.append(s)
lat_all = ' '.join(lat_text)
forms_raw = re.findall(r"[A-Za-z]+", lat_all.replace('[', '').replace(']', ''))
seen = []
for f in forms_raw:
    fl = f.lower()
    if fl not in seen: seen.append(fl)
LATIN = seen
lat_ksb = collections.defaultdict(list); lat_ks = collections.defaultdict(list)
for f in LATIN:
    k, s, b = ksb(f)
    lat_ksb[(k, s, b)].append(f); lat_ks[(k, s)].append(f)

if __name__ == '__main__':
    out = {}
    print("PARAGRAPH LINES:")
    for ln, loc, txt in para: print(f"  f1r.{ln} locus={loc!r} raw={txt}")
    print("next line:", raw[len(para)][:2])
    print("Latin distinct forms (case-folded):", len(LATIN),
          "| case-sensitive distinct:", len(set(re.findall(r"[A-Za-z]+", lat_all.replace('[','').replace(']','')))))
    total_s = 0; allrows = []
    for ln, loc, txt in para:
        toks = clean(txt)
        bad = [t for t in toks if not re.fullmatch(r'[a-z]+', t)]
        rows = []
        for t in toks:
            k, s, b = ksb(t); c = s % P
            words = W[c]
            r1 = words[0]
            r2 = min(words, key=lambda w: (nletters(w), words.index(w)))
            r2c = min(words, key=lambda w: (len(w), words.index(w)))
            ex = lat_ksb.get((k, s, b), [])
            ks = lat_ks.get((k, s), [])
            if ex: r3 = ('ksb', ex)
            elif ks: r3 = ('ks', ks[:3])
            else: r3 = ('none', [])
            rows.append(dict(t=t, k=k, s=s, b=b, c=c, r1=r1, r2=r2, r2c=r2c, r3=r3, ks_all=ks, inK=c in K))
        ls = sum(r['s'] for r in rows); total_s += ls
        allrows += rows
        print(f"\nL{ln} EVA: {' '.join(toks)} | bad={bad} | n={len(toks)} | sum {ls} -> cell {ls%P} ({W[ls%P][0]})")
        print("  R1:", ' / '.join(r['r1'] for r in rows))
        print("  R2:", ' / '.join(r['r2'] for r in rows))
        d = [(r['t'], r['r2'], r['r2c']) for r in rows if r['r2'] != r['r2c']]
        if d: print("  R2 by chars differs:", d)
        print("  R3:", ' / '.join(('|'.join(r['r3'][1]) + f"({r['r3'][0]})") if r['r3'][1] else '—' for r in rows))
        for r in rows:
            print(f"     {r['t']:12s} k={r['k']:2d} s={r['s']:3d} b={r['b']:4d} cell={r['c']:3d} inK={r['inK']} ks_all={r['ks_all']}")
    n = len(allrows)
    print(f"\nTOTAL tokens {n}; paragraph sum {total_s} -> cell {total_s%P} ({W[total_s%P][0]})")
    inK = [(r['t'], r['c']) for r in allrows if r['inK']]
    print(f"in K: {len(inK)}/{n} = {len(inK)/n:.4f}  {inK}; |K|={len(K)} |K|/257={len(K)/257:.4f}")
    print("R3 ksb:", sum(r['r3'][0]=='ksb' for r in allrows), [(r['t'], r['r3'][1]) for r in allrows if r['r3'][0]=='ksb'])
    print("R3 ks only:", sum(r['r3'][0]=='ks' for r in allrows))
    print("R3 none:", sum(r['r3'][0]=='none' for r in allrows))
    print("R1!=R2:", sum(r['r1']!=r['r2'] for r in allrows))
    # mod-257 variant
    lat_mod = collections.defaultdict(list)
    for f in LATIN:
        k, s, b = ksb(f); lat_mod[(k, s % P, b % P)].append(f)
    print("R3 mod257 ksb:", [(r['t'], lat_mod[(r['k'], r['s'] % P, r['b'] % P)]) for r in allrows if lat_mod.get((r['k'], r['s'] % P, r['b'] % P))])
    # alternatives / comma split
    for ln, loc, txt in para:
        a1 = clean(txt, alt=1); a0 = clean(txt)
        if a1 != a0:
            print("alt reading line", ln, [(x, ksb(x)) for x in a1 if x not in a0])
        cs = clean(txt, comma='split')
        if cs != a0:
            print("comma split line", ln, [(x, ksb(x)[1]) for x in cs if x not in a0])
    json.dump([{k: v for k, v in r.items()} for r in allrows], open(SP + "excerpt/render_verify/rows.json", 'w'), indent=1)
