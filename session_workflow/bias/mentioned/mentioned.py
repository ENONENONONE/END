#!/usr/bin/env python3
"""Density of the corpus's own vocabulary of integers (exercise a-e).
No randomness is used anywhere in this script (no seed needed).
Output: stdout and results.json in this folder. Never prints lines of the closure key."""
import re, json, html, os, collections
from math import comb

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = '~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ'
REVIEW = BASE + '/cascade_corpus_review.html'
KEY = BASE + '/.closure_key'
TABLET = BASE + '/emerald_tablet.json'
PLATE = '<scratchpad>/vl/plate_latin.txt'
P = 257
R = {}

# ---------------- integer extraction ----------------
DATE = re.compile(r'(?<![0-9])([0-9]{4})-([0-9]{2})-([0-9]{2})(?![0-9])')

def ints_from_text(txt, glue='ascii', drop_decimal_frac=False, drop_whole_date=False):
    """Maximal ASCII digit runs. A run touching a letter on either side is ignored
    (glue='ascii': [A-Za-z]; glue='unicode': any str.isalpha char, e.g. phi, psi).
    Year of a YYYY-MM-DD date is ignored (month/day kept unless drop_whole_date)."""
    skip = set()  # start offsets of runs to skip
    for m in DATE.finditer(txt):
        skip.add(m.start(1))
        if drop_whole_date:
            skip.add(m.start(2)); skip.add(m.start(3))
    out = []
    for m in re.finditer(r'[0-9]+', txt):
        a, b = m.start(), m.end()
        if a in skip:
            continue
        L = txt[a-1] if a > 0 else ''
        Rc = txt[b] if b < len(txt) else ''
        def isl(c):
            if not c: return False
            return (c.isascii() and c.isalpha()) if glue == 'ascii' else c.isalpha()
        if isl(L) or isl(Rc):
            continue
        if drop_decimal_frac and a >= 2 and txt[a-1] == '.' and txt[a-2].isdigit():
            continue
        out.append(int(m.group()))
    return out

def review_text(keep_code=False):
    h = open(REVIEW, encoding='utf-8').read()
    if not keep_code:
        h = re.sub(r'<script\b.*?</script>', ' ', h, flags=re.S | re.I)
        h = re.sub(r'<style\b.*?</style>', ' ', h, flags=re.S | re.I)
    h = re.sub(r'<!--.*?-->', ' ', h, flags=re.S)
    h = re.sub(r'<[A-Za-z/!][^>]*>', ' ', h)   # tags -> space (keeps table cells apart)
    return html.unescape(h)

key_txt = open(KEY, encoding='utf-8').read()
rev_txt = review_text()

rev_list = ints_from_text(rev_txt)
key_list = ints_from_text(key_txt)
S_rev, S_key = set(rev_list), set(key_list)
M = S_rev | S_key
R['a'] = dict(review_distinct=len(S_rev), review_tokens=len(rev_list),
              key_distinct=len(S_key), key_tokens=len(key_list),
              union_M=len(M), intersection=len(S_rev & S_key),
              review_only=len(S_rev - S_key), key_only=len(S_key - S_rev),
              max_review=max(S_rev), max_key=max(S_key))

# variants (sensitivity of the extraction rule)
var = {}
for name, kw, keep in [('unicode_glue', dict(glue='unicode'), False),
                       ('drop_decimal_fraction_runs', dict(drop_decimal_frac=True), False),
                       ('drop_whole_dates', dict(drop_whole_date=True), False),
                       ('keep_script_style', {}, True)]:
    rt = review_text(keep_code=keep)
    Mv = set(ints_from_text(rt, **kw)) | set(ints_from_text(key_txt, **kw))
    var[name] = Mv
R['a']['variants_union_size'] = {k: len(v) for k, v in var.items()}

# ---------------- (b) density by range ----------------
RANGES = [(0, 256), (257, 999), (1000, 9999), (10000, 100000)]
def density(S):
    d = {}
    for lo, hi in RANGES:
        n = hi - lo + 1
        c = sum(1 for x in S if lo <= x <= hi)
        d[f'{lo}-{hi}'] = dict(present=c, size=n, fraction=c / n)
    return d
R['b'] = dict(M=density(M), review_only_set=density(S_rev), key_only_set=density(S_key),
              variants={k: {r: v2['fraction'] for r, v2 in density(v).items()} for k, v in var.items()},
              missing_0_256=sorted(set(range(257)) - M),
              above_100000=sum(1 for x in M if x > 100000))
# finer bins inside 257-999 and 1000-9999 (for the Tabula sums)
fine = {}
for lo in range(200, 2000, 100):
    hi = lo + 99
    fine[f'{lo}-{hi}'] = sum(1 for x in M if lo <= x <= hi) / 100
R['b']['per_hundred_200_1999'] = fine

def dens_of(x):
    for lo, hi in RANGES:
        if lo <= x <= hi:
            return R['b']['M'][f'{lo}-{hi}']['fraction'], f'{lo}-{hi}'
    return None, None

# ---------------- (c) tablet cell counts ----------------
T = json.load(open(TABLET, encoding='utf-8'))
cnt = {int(k): len(v['words']) for k, v in T.items()}
dist = collections.Counter(cnt.values())
R['c'] = dict(cells=len(cnt), total_words=sum(cnt.values()), min_words=min(cnt.values()),
              max_words=max(cnt.values()), cells_with_1=sum(1 for v in cnt.values() if v == 1),
              empty_cells=sorted(k for k, v in cnt.items() if v == 0),
              p_random_sum_hits_word=sum(1 for v in cnt.values() if v > 0) / P,
              count_distribution=dict(sorted(dist.items())))

# ---------------- (d) Tabula sentences ----------------
txt = open(PLATE, encoding='utf-8').read()
sec = re.search(r'\[TABULA\](.*?)\[PIMANDER\]', txt, re.S).group(1)
sec = '\n'.join(l for l in sec.splitlines() if not l.strip().startswith('#'))
sents = [s.strip() for s in sec.split('.') if s.strip()]
ls = lambda s: sum(ord(c) - 64 for c in s.upper() if 'A' <= c <= 'Z')
rows = []
for i, s in enumerate(sents, 1):
    m = ls(s); u = s.upper().count('U'); j = s.upper().count('J')
    rows.append(dict(i=i, modern=m, plate=m + u, U=u, J=j, start=s[:40]))
sums = [(r['i'], 'modern', r['modern']) for r in rows] + [(r['i'], 'plate', r['plate']) for r in rows]
hits = []; exp = 0.0; probs = []
for i, kind, s in sums:
    p, rg = dens_of(s)
    probs.append(p); exp += p
    inM = s in M
    hits.append(dict(sentence=i, spelling=kind, sum=s, range=rg, density=p, in_M=inM,
                     in_review=s in S_rev, in_key=s in S_key, cell=s % P, cell_in_M=(s % P) in M))
obs = sum(h['in_M'] for h in hits)
# Poisson-binomial tail P(X >= obs) under independent Bernoulli(density) draws, exact by DP
dp = [1.0]
for p in probs:
    nd = [0.0] * (len(dp) + 1)
    for k, v in enumerate(dp):
        nd[k] += v * (1 - p); nd[k + 1] += v * p
    dp = nd
tail = sum(dp[obs:])
var_ = sum(p * (1 - p) for p in probs)
# same with per-hundred local density
exp_local = sum(fine.get(f'{(s//100)*100}-{(s//100)*100+99}', dens_of(s)[0]) for _, _, s in sums)
R['d'] = dict(n_sentences=len(sents), rows=rows, hits=hits, observed_in_M=obs, expected=exp,
              variance=var_, p_tail_ge_obs=tail, expected_local_per_hundred=exp_local,
              observed_modern=sum(h['in_M'] for h in hits if h['spelling'] == 'modern'),
              observed_plate=sum(h['in_M'] for h in hits if h['spelling'] == 'plate'),
              distinct_sums=len(set(s for _, _, s in sums)),
              observed_in_review=sum(h['in_review'] for h in hits),
              observed_in_key=sum(h['in_key'] for h in hits),
              cells_in_M=sum(h['cell_in_M'] for h in hits),
              whole_modern=sum(r['modern'] for r in rows), whole_plate=sum(r['plate'] for r in rows))
R['d']['whole_modern_in_M'] = R['d']['whole_modern'] in M
R['d']['whole_plate_in_M'] = R['d']['whole_plate'] in M
# variant densities applied to the same sums
R['d']['variants'] = {}
for k, Mv in var.items():
    R['d']['variants'][k] = sum(1 for _, _, s in sums if s in Mv)

# ---------------- (d') the same test with the review's own Tabula write-up removed ----------------
# The review holds a table listing every Tabula sentence with its sums (div.tbl containing
# "Verum, sine mendacio") and a following paragraph ("The whole, in this transcription").
# X1 removes those two blocks; X2 removes the whole plate passage, from the paragraph
# "The Emerald Tablet's plate and the rongorongo" up to the paragraph "Readings brought to the review".
raw = open(REVIEW, encoding='utf-8').read()
raw = re.sub(r'<script\b.*?</script>', ' ', raw, flags=re.S | re.I)
raw = re.sub(r'<style\b.*?</style>', ' ', raw, flags=re.S | re.I)
i_tab = raw.find('Verum, sine mendacio')
t0 = raw.rfind('<div class="tbl">', 0, i_tab)
t1 = raw.find('</div>', raw.find('</table>', i_tab)) + len('</div>')
p0 = raw.find('<p', raw.find('The whole, in this transcription') - 40)
p0 = raw.rfind('<p', 0, raw.find('The whole, in this transcription'))
p1 = raw.find('</p>', p0) + 4
x2a = raw.rfind('<p', 0, raw.find("The Emerald Tablet's plate and the rongorongo"))
x2b = raw.rfind('<p', 0, raw.find('Readings brought to the review'))
def strip(hh):
    hh = re.sub(r'<!--.*?-->', ' ', hh, flags=re.S)
    return html.unescape(re.sub(r'<[A-Za-z/!][^>]*>', ' ', hh))
X1 = strip(raw[:t0] + ' ' + raw[t1:p0] + ' ' + raw[p1:])
X2 = strip(raw[:x2a] + ' ' + raw[x2b:])
removed_X1 = strip(raw[t0:t1] + ' ' + raw[p0:p1])
excl = {}
for nm, tx in [('X1_table_and_summary_removed', X1), ('X2_plate_passage_removed', X2)]:
    Mx = set(ints_from_text(tx)) | S_key
    dx = density(Mx)
    ex = 0.0; ob = 0; pr = []; kept = []
    for i, kind, s in sums:
        for lo, hi in RANGES:
            if lo <= s <= hi:
                p = dx[f'{lo}-{hi}']['fraction']
        pr.append(p); ex += p
        if s in Mx:
            ob += 1; kept.append((i, kind, s))
    dp = [1.0]
    for p in pr:
        nd = [0.0] * (len(dp) + 1)
        for k, v in enumerate(dp):
            nd[k] += v * (1 - p); nd[k + 1] += v * p
        dp = nd
    excl[nm] = dict(chars_removed=len(rev_txt) - len(tx), union_size=len(Mx),
                    density={r: v['fraction'] for r, v in dx.items()},
                    present={r: v['present'] for r, v in dx.items()},
                    observed=ob, expected=ex, p_tail_ge_obs=sum(dp[ob:]),
                    p_le_obs=sum(dp[:ob + 1]), still_present=kept)
    # context of each surviving sum (first occurrence) for inspection
    ctx = {}
    for i, kind, s in kept:
        m = re.search(r'(?<![0-9A-Za-z])%d(?![0-9A-Za-z])' % s, tx)
        ctx[f'{i}{kind[0]}:{s}'] = re.sub(r'\s+', ' ', tx[max(0, m.start() - 50):m.start() + 25]) if m else 'key file'
    excl[nm]['contexts'] = ctx
R['d_excluding_writeup'] = excl
R['d']['ints_only_in_removed_X1_block'] = sorted((set(ints_from_text(removed_X1)) - set(ints_from_text(X1))) - S_key)

# ---------------- (e) value-placed vs letter-sum ----------------
lsum = 0; vplace = 0; noletters = 0; per_cell_v = collections.Counter()
for k, v in T.items():
    for w in v['words']:
        s = ls(w)
        if not any('A' <= c <= 'Z' for c in w.upper()):
            noletters += 1
        if s % P == int(k):
            lsum += 1
        else:
            vplace += 1; per_cell_v[int(k)] += 1
cells_only_value = sorted(c for c in range(P)
                          if all(ls(w) % P != c for w in T[str(c)]['words']))
digit_rule_hits = [(k, w) for k, v in T.items() for w in v['words']
                   if re.search(r'[0-9]', w) and ls(w) % P == int(k)]
versions = {}
for f in ['pre-terminus-20260918', 'pre-aim-20260918', 'pre-rotate-20260918', 'pre-toth-20260918',
          'pre-rongorongo-20260919', 'pre-plate-20260919']:
    U = json.load(open(BASE + f'/emerald_tablet.{f}.json', encoding='utf-8'))
    n = sum(len(v['words']) for v in U.values())
    l = sum(1 for k, v in U.items() for w in v['words'] if ls(w) % P == int(k))
    versions[f] = dict(words=n, letter_sum=l, value=n - l)
R['e'] = dict(letter_sum_placed=lsum, value_placed=vplace, words_without_letters=noletters,
              words_with_digit_meeting_rule=digit_rule_hits, earlier_versions=versions,
              value_placed_words={k: [w for w in v['words'] if ls(w) % P != int(k)]
                                  for k, v in T.items() if any(ls(w) % P != int(k) for w in v['words'])},
              cells_with_a_value_placed_word=len(per_cell_v),
              cells_with_no_letter_sum_word=cells_only_value)

json.dump(R, open(os.path.join(OUT, 'results.json'), 'w'), indent=1, ensure_ascii=False, default=str)

# ---------------- print ----------------
print('(a)', {k: v for k, v in R['a'].items()})
print('(b) M density:')
for k, v in R['b']['M'].items(): print('   ', k, v)
print('    missing 0-256:', R['b']['missing_0_256'], ' >100000:', R['b']['above_100000'])
print('    review-only-set density:', {k: round(v['fraction'], 5) for k, v in R['b']['review_only_set'].items()})
print('    key-only-set density:', {k: round(v['fraction'], 5) for k, v in R['b']['key_only_set'].items()})
print('    variants:', {k: {r: round(f, 5) for r, f in v.items()} for k, v in R['b']['variants'].items()})
print('    per hundred:', R['b']['per_hundred_200_1999'])
print('(c)', R['c'])
print('(d) sentences', len(sents))
for r in rows: print('   ', r)
for h in hits: print('   ', h)
print('   ', {k: v for k, v in R['d'].items() if k not in ('rows', 'hits')})
print('    ints only in removed X1 block:', R['d']['ints_only_in_removed_X1_block'])
for k, v in R['d_excluding_writeup'].items():
    print("(d')", k, {kk: vv for kk, vv in v.items() if kk != 'contexts'})
    for kk, vv in v['contexts'].items(): print('        ', kk, '|', vv)
print('(e)', {k: v for k, v in R['e'].items() if k != 'value_placed_words'})
