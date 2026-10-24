#!/usr/bin/env python3
"""Render ZL f1r paragraph 1 (lines f1r.1-f1r.6) under three fixed rules.

R1 first word   : EVA word -> cell (s mod 257) -> first tablet word at that cell
R2 shortest word: EVA word -> cell -> tablet word with fewest letters (ties: first listed)
R3 Latin        : EVA word -> plate-Latin forms with same (k, s, b) (all), else same (k, s)
                  (up to 3, in order of first appearance in the plate text), else '-'

No random generator is used anywhere in this script (nothing to seed).
Outputs: render_f1r_p1.json and render_f1r_p1.txt next to this file.
"""
import json, re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
VL = os.path.join(HERE, '..', '..', 'vl')
sys.path.insert(0, VL)
import voy  # parse(path) -> (pages, rows); words(text) joins on commas by default

P = 257
ROOT = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
T = json.load(open(ROOT + 'emerald_tablet.json'))
W = {int(k): v['words'] for k, v in T.items()}
K = {0,1,2,3,8,15,16,17,23,44,46,62,72,73,86,92,111,117,119,120,128,129,136,137,138,140,142,153,225,240,241,255,256}

def vals(w):
    return [ord(c) - 64 for c in w.upper() if 'A' <= c <= 'Z']

def ksb(w):
    v = vals(w)
    return len(v), sum(v), sum((i + 1) * x for i, x in enumerate(v))

def nlet(w):
    return len(vals(w))

# ---- plate Latin vocabulary (all four sections, '#' lines skipped, [..] uncertain kept, brackets stripped)
latin_order = []
latin_uncertain = set()
for line in open(os.path.join(VL, 'plate_latin.txt'), encoding='utf-8'):
    line = line.rstrip('\n')
    if not line or line.startswith('#') or re.fullmatch(r'\[[A-Z]+\]', line.strip()):
        continue
    for m in re.finditer(r'(\[)?([A-Za-z]+)(\])?', line):
        w = m.group(2).lower()
        if m.group(1) and m.group(3):
            latin_uncertain.add(w)
        if w not in latin_order:
            latin_order.append(w)
LKSB = {w: ksb(w) for w in latin_order}

# ---- the excerpt
pages, rows = voy.parse(os.path.join(VL, 'ZL3b-n.txt'))
f1r = [r for r in rows if r[0] == 'f1r']
para = []
for r in f1r:
    para.append(r)
    if 'Pt' in r[2]:
        break
raw_lines = {}
for line in open(os.path.join(VL, 'ZL3b-n.txt'), encoding='ascii', errors='replace'):
    m = re.match(r'^<(f1r)\.(\d+),([^>]*)>\s*(.*)$', line.rstrip('\n'))
    if m:
        raw_lines[m.group(2)] = (m.group(3), m.group(4))

out = {'lines': [], 'latin_vocab_size': len(latin_order), 'latin_uncertain': sorted(latin_uncertain)}
txt = []
all_tok = []
for (pg, ln, loc, t) in para:
    toks = voy.words(t)                       # commas join
    clean = [w for w in toks if re.fullmatch(r'[a-z]+', w)]
    dropped = [w for w in toks if w not in clean]
    recs = []
    for w in clean:
        k, s, b = ksb(w)
        c = s % P
        cand = W[c]
        r1 = cand[0]
        r2 = min(cand, key=lambda x: (nlet(x), cand.index(x)))
        exact = [x for x in latin_order if LKSB[x] == (k, s, b)]
        ks = [x for x in latin_order if LKSB[x][:2] == (k, s)]
        exact_mod = [x for x in latin_order if LKSB[x][0] == k and LKSB[x][1] % P == s % P and LKSB[x][2] % P == b % P]
        if exact:
            r3, r3kind = exact, 'ksb'
        elif ks:
            r3, r3kind = ks[:3], 'ks'
        else:
            r3, r3kind = [], 'none'
        recs.append(dict(eva=w, k=k, s=s, b=b, cell=c, inK=c in K, R1=r1, R2=r2, R3=r3, R3kind=r3kind,
                         ks_all=ks, ksb_mod257=exact_mod, tablet_words=cand))
        all_tok.append(recs[-1])
    lsum = sum(r['s'] for r in recs)
    out['lines'].append(dict(line=ln, locus=loc, zl_raw=raw_lines[ln][1], clean_tokens=clean, dropped=dropped,
                             letter_sum=lsum, cell=lsum % P, words=recs))

# English glosses of the Latin forms used by R3: RECALLED (the author's own knowledge of Latin, not checked here)
GLOSS = {
 'dignis': 'worthy (dat./abl. pl.)', 'ipse': 'himself, he himself', 'eius': 'his, its, of him',
 'vincet': 'will conquer', 'itaque': 'and so, therefore', 'lubens': 'willingly, gladly',
 'est': 'is', 'vim': 'force, power (acc.)', 'cuivis': 'to anyone at all',
 'natae': 'born (fem. pl.)', 'mihi': 'to me', 'divinae': 'divine, of the divine (fem.)',
 'fidelis': 'faithful', 'dixi': 'I have said', 'hunc': 'this (acc. masc.)',
 'magno': 'great (abl./dat.)', 'aliis': 'others (dat./abl. pl.)', 'magnesia': 'magnesia (the alchemists\' matter)',
 'instar': 'likeness, the equal of', 'cupis': 'you desire', 'coelum': 'heaven, sky',
 'grati': 'grateful, pleasing (gen.)', 'omnes': 'all (pl.)', 'modum': 'manner, way (acc.)',
 'omnis': 'all, every', 'logou': 'of the Word (Greek logou)', 'sicut': 'just as, like',
 'modus': 'manner, way', 'animi': 'of the mind, of the soul', 'terraeque': 'and of the earth',
 'mementote': 'remember! (pl. imperative)',
}
missing = sorted({x for r in all_tok for x in r['R3'] if x not in GLOSS})
if missing:
    raise SystemExit(f'gloss missing for {missing}')
out['glosses_RECALLED'] = {x: GLOSS[x] for x in sorted({x for r in all_tok for x in r['R3']})}

n = len(all_tok)
nK = sum(r['inK'] for r in all_tok)
n_ksb = sum(r['R3kind'] == 'ksb' for r in all_tok)
n_ks = sum(r['R3kind'] == 'ks' for r in all_tok)
n_mod = sum(bool(r['ksb_mod257']) for r in all_tok)
tot = sum(r['s'] for r in all_tok)
out.update(n_tokens=n, n_inK=nK, share_inK=nK / n, K_size=len(K), K_over_257=len(K) / P,
           n_R3_ksb=n_ksb, n_R3_ks=n_ks, n_R3_none=n - n_ksb - n_ks, n_ksb_mod257=n_mod,
           paragraph_letter_sum=tot, paragraph_cell=tot % P,
           r1_r2_differ=sum(r['R1'] != r['R2'] for r in all_tok))

for i, L in enumerate(out['lines'], 1):
    txt.append(f"L{i} (f1r.{L['line']}, {L['locus']}) ZL raw: {L['zl_raw']}")
    txt.append(f"L{i} EVA: {' '.join(L['clean_tokens'])}   | letter sum {L['letter_sum']} -> cell {L['cell']} ({W[L['cell']][0]})")
    txt.append(f"L{i} R1: " + ' / '.join(r['R1'] for r in L['words']))
    txt.append(f"L{i} R2: " + ' / '.join(r['R2'] for r in L['words']))
    txt.append(f"L{i} R3: " + ' / '.join(('|'.join(r['R3']) + ('' if r['R3kind'] != 'ks' else '(ks)')) if r['R3'] else '—' for r in L['words']))
    txt.append(f"L{i} R3 gloss (RECALLED): " + ' / '.join(('|'.join(f"{x} '{GLOSS[x]}'" for x in r['R3'])) if r['R3'] else '—' for r in L['words']))
    for r in L['words']:
        txt.append(f"     {r['eva']:<13} k={r['k']:<2} s={r['s']:<3} b={r['b']:<4} cell={r['cell']:<3} {'K' if r['inK'] else ' '} "
                   f"R1={r['R1']:<24} R2={r['R2']:<14} R3[{r['R3kind']}]={','.join(r['R3']) or '—'}"
                   f"{'  ks_all=' + ','.join(r['ks_all']) if len(r['ks_all']) > 3 else ''}"
                   f"{'  ksb_mod257=' + ','.join(r['ksb_mod257']) if r['ksb_mod257'] and r['ksb_mod257'] != r['R3'] else ''}")
txt.append(f"tokens {n} · in K {nK} ({nK/n:.4f}) · |K| {len(K)}, |K|/257 {len(K)/P:.4f}")
txt.append(f"R3: (k,s,b) {n_ksb} · (k,s) only {n_ks} · none {n-n_ksb-n_ks} · (k, s mod 257, b mod 257) matches {n_mod}")
txt.append(f"paragraph letter sum {tot} -> cell {tot%P} · R1 != R2 on {out['r1_r2_differ']} tokens · Latin vocabulary {len(latin_order)} forms")
open(os.path.join(HERE, 'render_f1r_p1.json'), 'w').write(json.dumps(out, indent=1, ensure_ascii=False))
open(os.path.join(HERE, 'render_f1r_p1.txt'), 'w').write('\n'.join(txt) + '\n')
print('\n'.join(txt))
