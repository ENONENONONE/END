#!/usr/bin/env python3
"""Forking-paths exercise: count spelling / span / subset choices in the Tabula and how often one lands on K.
Read-only on all inputs. Writes only to this folder. No random generator is used (all counts are exhaustive)."""
import json, re, itertools, os
from math import comb
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
VL = os.path.join(HERE, '..', '..', 'vl')
TABLET = '~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/emerald_tablet.json'
P = 257
K = {0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120, 128, 129, 136, 137, 138,
     140, 142, 153, 225, 240, 241, 255, 256}
assert len(K) == 33

T = json.load(open(TABLET))
ALLW = {x: int(k) for k, v in T.items() for x in v['words']}
OUT = {}

def ls(s):
    return sum(ord(c) - 96 for c in s.lower() if 'a' <= c <= 'z')

def nletters(s):
    return sum(1 for c in s.lower() if 'a' <= c <= 'z')

# ---------- field readings ----------
DLOG = {}
x = 1
for e in range(256):
    DLOG[x] = e; x = x * 3 % P
assert len(DLOG) == 256
INV = lambda n: pow(n, P - 2, P)
QR = {n * n % P for n in range(1, P)}

def readings(n, atbash=None):
    """Dict name -> list of values (mod 257) for the corpus readings of cell n. inf omitted."""
    n %= P
    r = {'self': [n], 'fold': [(P - n) % P], 'square': [n * n % P], 'double': [2 * n % P],
         'half': [129 * n % P], 'x17': [17 * n % P], 'x5': [5 * n % P], 'x3': [3 * n % P]}
    if n:
        r['inverse'] = [INV(n)]
        r['dlog'] = [DLOG[n]]
    if n == 0:
        r['sqrt'] = [0]
    elif n in QR:
        r['sqrt'] = sorted(y for y in range(1, P) if y * y % P == n)
    if n != 137:
        r['gamma'] = [(n - 120) * INV((n + 120) % P) % P]
    if atbash is not None:
        r['atbash'] = [atbash % P]
    return r

def hits(n, atbash=None):
    return sorted({(k, v) for k, vs in readings(n, atbash).items() for v in vs if v in K})

# baseline: fraction of the 257 cells for which some (non-Atbash) reading lands on K
base_cells = [n for n in range(P) if hits(n)]
OUT['baseline_cells_with_some_reading_in_K'] = len(base_cells)
n_readings_per_cell = [len({(k, v) for k, vs in readings(n).items() for v in vs}) for n in range(P)]
OUT['readings_per_cell_min_max'] = (min(n_readings_per_cell), max(n_readings_per_cell))
distinct_vals = [len({v for vs in readings(n).values() for v in vs}) for n in range(P)]
OUT['distinct_reading_values_per_cell_mean'] = round(sum(distinct_vals) / P, 4)

# ---------- Tabula text ----------
txt = open(os.path.join(VL, 'plate_latin.txt'), encoding='utf-8').read()
tab = txt.split('[TABULA]')[1].split('[PIMANDER]')[0]
tab = '\n'.join(l for l in tab.splitlines() if not l.startswith('#')).strip()
SENTS = [s.strip() + '.' for s in tab.split('.') if s.strip()]
assert len(SENTS) == 15, len(SENTS)
# cross-check against tabula.py SENT
import importlib.util
spec = importlib.util.spec_from_file_location('tabula', os.path.join(VL, 'tabula.py'))
tb = importlib.util.module_from_spec(spec); spec.loader.exec_module(tb)
assert [s for s, _ in tb.SENT] == SENTS, 'plate_latin TABULA split != tabula.SENT'

def toks(s):
    return re.findall(r'[a-z]+', s.lower())

VOW = set('aeiou')
def v_for_u(ws): return [w.replace('u', 'v') for w in ws]
def drop_et(ws): return [w for w in ws if w != 'et']
def que_split(ws):
    out = []
    for w in ws:
        if w.endswith('que') and len(w) > 3:
            out += [w[:-3], 'que']
        else:
            out.append(w)
    return out
def j_rule(ws):  # initial i before a vowel -> j
    return ['j' + w[1:] if len(w) > 1 and w[0] == 'i' and w[1] in VOW else w for w in ws]
# extras outside the specified rule set (labelled as extras)
def ejus(ws): return ['ejus' if w == 'eius' else w for w in ws]
def caelum(ws): return ['caelum' if w == 'coelum' else w for w in ws]

wsum = lambda ws: sum(ls(w) for w in ws)
wlen = lambda ws: sum(len(w) for w in ws)

# (a)
a_rows = []
j_changed = sorted({w for s in SENTS for w in toks(s) if j_rule([w])[0] != w})
que_words = sorted({w for s in SENTS for w in toks(s) if w.endswith('que') and len(w) > 3})
tot_single_cells = tot_combo_cells = tot_ext_cells = 0
sent_any_K_single = sent_any_K_combo = sent_any_K_ext = 0
exp_single = exp_combo = exp_ext = Fraction(0)
reading_rows = []
for i, s in enumerate(SENTS, 1):
    ws = toks(s)
    variants = {
        'modern': ws,
        'V_for_U': v_for_u(ws),
        'et_dropped': drop_et(ws),
        'que_split': que_split(ws),
        'J_rule': j_rule(ws),
    }
    sums = {k: wsum(v) for k, v in variants.items()}
    assert sums['que_split'] == sums['modern']
    single_cells = sorted({v % P for v in sums.values()})
    # full combinations of the three binary spec choices (U/V, et/&, J rule); que split has no effect
    combo = {}
    for uv, et, jj in itertools.product([0, 1], repeat=3):
        w2 = ws
        if jj: w2 = j_rule(w2)
        if et: w2 = drop_et(w2)
        if uv: w2 = v_for_u(w2)
        combo[(uv, et, jj)] = (wsum(w2), wlen(w2))
    combo_cells = sorted({v[0] % P for v in combo.values()})
    # extended: add eius->ejus and coelum->caelum (extras, not in the specified rule)
    ext = {}
    for uv, et, ej, ca in itertools.product([0, 1], repeat=4):
        w2 = ws
        if ej: w2 = ejus(w2)
        if ca: w2 = caelum(w2)
        if et: w2 = drop_et(w2)
        if uv: w2 = v_for_u(w2)
        ext[(uv, et, ej, ca)] = (wsum(w2), wlen(w2))
    ext_cells = sorted({v[0] % P for v in ext.values()})
    exact = sorted({v for v in [*sums.values(), *[c[0] for c in combo.values()]] if v in (257, 1027)})
    exact_ext = sorted({c[0] for c in ext.values() if c[0] in (257, 514, 771, 1027, 1028)})
    kin_single = [c for c in single_cells if c in K]
    kin_combo = [c for c in combo_cells if c in K]
    kin_ext = [c for c in ext_cells if c in K]
    tot_single_cells += len(single_cells); tot_combo_cells += len(combo_cells); tot_ext_cells += len(ext_cells)
    sent_any_K_single += bool(kin_single); sent_any_K_combo += bool(kin_combo); sent_any_K_ext += bool(kin_ext)
    pk = lambda m: 1 - Fraction(comb(P - 33, m), comb(P, m))
    exp_single += pk(len(single_cells)); exp_combo += pk(len(combo_cells)); exp_ext += pk(len(ext_cells))
    # readings on each combo cell (Atbash with that variant's letter count)
    rd = []
    for key, (sm, kk) in combo.items():
        h = hits(sm, atbash=27 * kk - sm)
        rd.append((key, sm, sm % P, 27 * kk - sm, h))
    any_reading_K = sum(1 for r in rd if r[4])
    reading_rows.append((i, len(rd), any_reading_K))
    a_rows.append(dict(sentence=i, text=s, sums=sums, single_cells=single_cells, single_K=kin_single,
                       combo={f'uv{k[0]}_et{k[1]}_j{k[2]}': v[0] for k, v in combo.items()},
                       combo_cells=combo_cells, combo_K=kin_combo, exact_257_or_1027=exact,
                       ext_cells=ext_cells, ext_K=kin_ext, ext_exact_multiples_or_1027=exact_ext,
                       n_et=ws.count('et'), n_u=sum(w.count('u') for w in ws),
                       n_eius=ws.count('eius'), has_coelum='coelum' in ws))

# readings summary over DISTINCT (cell, atbash) pairs of the 8 spec combinations per sentence
rd_distinct_total = rd_distinct_hit = 0; sent_with_reading_hit = 0; exp_reading = Fraction(0)
reading_kind_counts = {}
rd_detail = []
NB = OUT['baseline_cells_with_some_reading_in_K']
for i, s in enumerate(SENTS, 1):
    ws = toks(s); pairs = set()
    for uv, et, jj in itertools.product([0, 1], repeat=3):
        w2 = ws
        if jj: w2 = j_rule(w2)
        if et: w2 = drop_et(w2)
        if uv: w2 = v_for_u(w2)
        sm, kk = wsum(w2), wlen(w2)
        pairs.add((sm % P, (27 * kk - sm) % P))
    cells = {c for c, _ in pairs}
    nh = 0
    for c, at in sorted(pairs):
        h = hits(c, atbash=at)
        rd_detail.append((i, c, at, h))
        if h: nh += 1
        for kind, _ in h:
            reading_kind_counts[kind] = reading_kind_counts.get(kind, 0) + 1
    rd_distinct_total += len(pairs); rd_distinct_hit += nh; sent_with_reading_hit += bool(nh)
    m = len(cells)
    exp_reading += 1 - Fraction(comb(P - NB, m), comb(P, m))
OUT['a_readings'] = dict(distinct_pairs=rd_distinct_total, pairs_with_reading_in_K=rd_distinct_hit,
                         sentences_with_reading_in_K=sent_with_reading_hit,
                         expected_sentences_uniform_no_atbash=float(exp_reading),
                         reading_kind_counts=reading_kind_counts, detail=rd_detail)

OUT['a'] = dict(rows=a_rows, j_rule_words_changed=j_changed, que_words=que_words,
                tot_single_cells=tot_single_cells, tot_combo_cells=tot_combo_cells, tot_ext_cells=tot_ext_cells,
                sent_any_K_single=sent_any_K_single, sent_any_K_combo=sent_any_K_combo, sent_any_K_ext=sent_any_K_ext,
                expected_any_K_single=float(exp_single), expected_any_K_combo=float(exp_combo),
                expected_any_K_ext=float(exp_ext), reading_rows=reading_rows)

# ---------- (b) 4-subsets of distinct Tabula words ----------
ALLTOK = [w for s in SENTS for w in toks(s)]
DIST = sorted(set(ALLTOK))
NOUNS = set('adaptatione adaptationes coelum fortitudinis fortitudo gloriam hermes igne ingenio luna mater meditatione '
            'mendacio miracula modus mundi mundus nutrix obscuritas operatione partes pater philosophiae re rei rem res '
            'sol solis telesmi terra terram trismegistus ventre ventus vim vis'.split())
SUBST_ADJ = set('verum certum verissimum subtile subtilem spisso solidam superius inferius superiorum inferiorum'.split())
assert NOUNS <= set(DIST) and SUBST_ADJ <= set(DIST)

def subset_stats(words, spell=lambda w: w):
    vals = [ls(spell(w)) for w in words]
    mx = sum(sorted(vals)[-4:])
    # dp[j][s] = number of j-subsets with sum s
    dp = [[0] * (mx + 1) for _ in range(5)]
    dp[0][0] = 1
    for v in vals:
        for j in range(4, 0, -1):
            row, prev = dp[j], dp[j - 1]
            for s in range(mx, v - 1, -1):
                if prev[s - v]:
                    row[s] += prev[s - v]
    d4 = dp[4]
    total = sum(d4)
    assert total == comb(len(words), 4)
    exact257 = d4[257] if mx >= 257 else 0
    mult = {m: d4[m] for m in range(257, mx + 1, 257)}
    inK = sum(c for s, c in enumerate(d4) if s % P in K)
    exact_other = {t: (d4[t] if t <= mx else 0) for t in (514, 771, 1027)}
    return dict(n_words=len(words), n_subsets=total, exact_257=exact257, multiples_of_257=mult,
                multiples_total=sum(mult.values()), in_K=inK, in_K_frac=inK / total, exact_other=exact_other,
                max_sum=mx)

def list_exact(words, target, spell=lambda w: w):
    return [c for c in itertools.combinations(words, 4) if sum(ls(spell(w)) for w in c) == target]

b = {}
b['modern_all'] = subset_stats(DIST)
b['modern_nouns'] = subset_stats(sorted(NOUNS))
b['modern_nouns_plus_substadj'] = subset_stats(sorted(NOUNS | SUBST_ADJ))
b['V_all'] = subset_stats(DIST, lambda w: w.replace('u', 'v'))
b['V_nouns'] = subset_stats(sorted(NOUNS), lambda w: w.replace('u', 'v'))
noun257 = list_exact(sorted(NOUNS), 257)
b['modern_nouns_257_list'] = [' + '.join(c) for c in noun257]
b['sol_luna_ventus_terra'] = [ls(w) for w in ('sol', 'luna', 'ventus', 'terra')]
b['sol_luna_ventus_terra_V'] = [ls(w.replace('u', 'v')) for w in ('sol', 'luna', 'ventus', 'terra')]
# the four named in the sentence, one form each: nominative singular forms present
b['uniform_expected_in_K_frac'] = 33 / 257
OUT['b'] = b
all257 = list_exact(DIST, 257)
with open(os.path.join(HERE, 'b_all_4subsets_257_modern.txt'), 'w') as f:
    for c in all257:
        f.write(' + '.join(c) + '\n')
assert len(all257) == b['modern_all']['exact_257']

# ---------- (c) contiguous spans ----------
def spans(seq, targets=(257, 514, 771, 1027)):
    vals = [ls(w) for w in seq]
    res = {t: [] for t in targets}
    n = len(vals); cnt = 0; zero_mod = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += vals[j]; cnt += 1
            if s % P == 0: zero_mod += 1
            if s in res: res[s].append(' '.join(seq[i:j + 1]))
    return cnt, res, zero_mod

def sent_spans(sents_ws, targets=(257, 514, 771, 1027)):
    res = {t: [] for t in targets}; cnt = 0
    for ws in sents_ws:
        c, r, _ = spans(ws, targets); cnt += c
        for t in targets: res[t] += r[t]
    return cnt, res

c = {}
for name, fn in [('modern', lambda ws: ws), ('V_for_U', v_for_u),
                 ('V_for_U_et_dropped', lambda ws: v_for_u(drop_et(ws))), ('et_dropped', drop_et)]:
    seq = fn(ALLTOK)
    cnt, res, zm = spans(seq)
    scnt, sres = sent_spans([fn(toks(s)) for s in SENTS])
    c[name] = dict(n_words=len(seq), n_spans=cnt, counts={t: len(v) for t, v in res.items()}, spans=res,
                   zero_mod_257=zm, within_sentence_spans=scnt,
                   within_sentence_counts={t: len(v) for t, v in sres.items()})
OUT['c'] = c

# ---------- (d) spellings ----------
PAIRS = [('EHYEH', 'EHEIEH'), ('IUNONI', 'JUNONI'), ('CAELUM', 'COELUM'), ('ALCHYMIA', 'ALCHIMIA'),
         ('PYRAMIDUM', 'PIRAMIDUM'), ('HENRIC', 'HENRICUS'), ('KHUNRATH', 'KUNRATH')]
EXTRA_V = ['IVNONI', 'CAELVM', 'COELVM', 'PYRAMIDVM', 'PIRAMIDVM', 'HENRICVS', 'KHVNRATH', 'KVNRATH',
           'HENRIC KHUNRATH', 'HENRICUS KHUNRATH', 'HENRICVS KHVNRATH']
d = []
for x, y in PAIRS:
    sx, sy = ls(x), ls(y)
    d.append(dict(a=x, sa=sx, ca=sx % P, a_inK=sx % P in K, a_tablet=ALLW.get(x),
                  b=y, sb=sy, cb=sy % P, b_inK=sy % P in K, b_tablet=ALLW.get(y), differ=sx % P != sy % P))
dx = [dict(w=w, s=ls(w), c=ls(w) % P, inK=ls(w) % P in K, tablet=ALLW.get(w)) for w in EXTRA_V]
OUT['d'] = dict(pairs=d, extra_v=dx)

json.dump(OUT, open(os.path.join(HERE, 'forking_out.json'), 'w'), indent=1, default=str)

# ---------- print ----------
print('K size', len(K), '| baseline: cells 0..256 with some reading in K:', len(base_cells), '/ 257',
      '| readings/cell (min,max)', OUT['readings_per_cell_min_max'], '| mean distinct reading values/cell',
      OUT['distinct_reading_values_per_cell_mean'])
print('\n(a) J-rule words changed:', j_changed, '| que words:', que_words)
for r in a_rows:
    print(f"S{r['sentence']:>2} sums {r['sums']} | u={r['n_u']} et={r['n_et']} eius={r['n_eius']} coelum={r['has_coelum']}")
    print(f"     single cells {r['single_cells']} K:{r['single_K']} | combo sums {sorted(set(r['combo'].values()))} cells {r['combo_cells']} K:{r['combo_K']} | exact 257/1027: {r['exact_257_or_1027']}")
    print(f"     ext cells ({len(r['ext_cells'])}) {r['ext_cells']} K:{r['ext_K']} | ext exact: {r['ext_exact_multiples_or_1027']}")
A = OUT['a']
print('totals: single cells', A['tot_single_cells'], 'combo cells', A['tot_combo_cells'], 'ext cells', A['tot_ext_cells'])
print('sentences with any K: single', A['sent_any_K_single'], f"(uniform expectation {A['expected_any_K_single']:.4f})",
      '| combo', A['sent_any_K_combo'], f"({A['expected_any_K_combo']:.4f})", '| ext', A['sent_any_K_ext'], f"({A['expected_any_K_ext']:.4f})")
AR = OUT['a_readings']
print('readings over distinct (cell, atbash) pairs:', AR['distinct_pairs'], 'pairs;', AR['pairs_with_reading_in_K'],
      'with some reading in K; sentences with some reading in K:', AR['sentences_with_reading_in_K'],
      f"(uniform expectation without Atbash {AR['expected_sentences_uniform_no_atbash']:.4f})")
print('  reading kinds that hit K (count of pair-hits):', dict(sorted(AR['reading_kind_counts'].items(), key=lambda x: -x[1])))
for r in AR['detail']:
    print('   S', r[0], 'cell', r[1], 'atbash', r[2], 'hits', r[3])
print('\n(b)')
for k, v in b.items():
    print(' ', k, v)
print('\n(c)')
for k, v in c.items():
    print(' ', k, 'words', v['n_words'], 'spans', v['n_spans'], 'counts', v['counts'], 'sum≡0', v['zero_mod_257'],
          '| within-sentence spans', v['within_sentence_spans'], v['within_sentence_counts'])
    for t, lst in v['spans'].items():
        for sp in lst:
            print('     ', t, ':', sp)
print('\n(d)')
for r in d: print(' ', r)
for r in dx: print(' ', r)
