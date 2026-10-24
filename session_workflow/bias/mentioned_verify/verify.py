# Independent recomputation of the "mentioned integers" density exercise.
# Written from the task's definitions; does not reuse the other agent's code.
# No random generator in this file (controls with randomness live in control.py, seeded).
import re, json, html, sys
from collections import Counter

BASE = '~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/'
VL = '<scratchpad>/vl/'
OUT = '<scratchpad>/bias/mentioned_verify/'
P = 257

RAW_HTML = open(BASE + 'cascade_corpus_review.html', encoding='utf-8').read()
KEY = open(BASE + '.closure_key', encoding='utf-8').read()


def html_text(h, drop_script_style=True):
    if drop_script_style:
        h = re.sub(r'<script\b.*?</script>', ' ', h, flags=re.S | re.I)
        h = re.sub(r'<style\b.*?</style>', ' ', h, flags=re.S | re.I)
    h = re.sub(r'<[^>]*>', ' ', h)
    return html.unescape(h)


DATE = re.compile(r'(?<![0-9])(\d{4})-(\d{2})-(\d{2})(?![0-9])')


def extract(t, unicode_letters=False, drop_frac=False, drop_whole_date=False):
    """Return list of kept integer tokens."""
    # spans of years to drop
    drop = set()
    for m in DATE.finditer(t):
        if drop_whole_date:
            drop.update([m.span(1), m.span(2), m.span(3)])
        else:
            drop.add(m.span(1))
    out = []
    for m in re.finditer(r'[0-9]+', t):
        a, b = m.span()
        L = t[a - 1] if a > 0 else ''
        R = t[b] if b < len(t) else ''
        def isletter(c):
            if not c:
                return False
            if unicode_letters:
                return c.isalpha()
            return ('A' <= c <= 'Z') or ('a' <= c <= 'z')
        if isletter(L) or isletter(R):
            continue
        if (a, b) in drop:
            continue
        if drop_frac and a >= 2 and t[a - 1] == '.' and t[a - 2].isdigit():
            continue
        out.append(int(m.group()))
    return out


def ranges(S):
    r = [(0, 256), (257, 999), (1000, 9999), (10000, 100000)]
    res = []
    for lo, hi in r:
        c = sum(1 for x in S if lo <= x <= hi)
        res.append((lo, hi, c, hi - lo + 1, c / (hi - lo + 1)))
    return res


def dens_of(x, R):
    for lo, hi, c, n, d in R:
        if lo <= x <= hi:
            return d
    return None


def pb(ps):
    dist = [1.0]
    for p in ps:
        nd = [0.0] * (len(dist) + 1)
        for i, q in enumerate(dist):
            nd[i] += q * (1 - p)
            nd[i + 1] += q * p
        dist = nd
    return dist


res = {}
rt = html_text(RAW_HTML)
rev_tok = extract(rt)
key_tok = extract(KEY)
R_set, K_set = set(rev_tok), set(key_tok)
M = R_set | K_set
res['a1'] = (len(R_set), len(rev_tok))
res['a2'] = (len(K_set), len(key_tok))
res['a3'] = dict(M=len(M), both=len(R_set & K_set), only_rev=len(R_set - K_set), only_key=len(K_set - R_set),
                 max_rev=max(R_set), max_key=max(K_set), max_rev_digits=len(str(max(R_set))))
# a4 variants
def Mvar(**kw):
    return set(extract(html_text(RAW_HTML, kw.pop('dss', True)), **kw)) | set(extract(KEY, **kw))
res['a4'] = dict(unicode=len(Mvar(unicode_letters=True)), dropfrac=len(Mvar(drop_frac=True)),
                 wholedate=len(Mvar(drop_whole_date=True)), keep_script_style=len(set(extract(html_text(RAW_HTML, False))) | K_set))
RM = ranges(M)
res['b'] = RM
res['b5_rev'] = [c for *_, c, n, d in [(lo, hi, c, n, d) for lo, hi, c, n, d in ranges(R_set)]]
res['b5_key'] = [c for lo, hi, c, n, d in ranges(K_set)]
res['b4_above'] = sum(1 for x in M if x > 100000)
res['b6'] = {f'{h}': sum(1 for x in M if h <= x < h + 100) / 100 for h in range(200, 2000, 100)}
res['b7'] = ranges(Mvar(drop_frac=True))

# (c)
T = json.load(open(BASE + 'emerald_tablet.json', encoding='utf-8'))
cnt = {int(k): len(v['words']) for k, v in T.items()}
res['c'] = dict(cells=len(cnt), words=sum(cnt.values()), min=min(cnt.values()), max=max(cnt.values()),
                ones=sum(1 for v in cnt.values() if v == 1), empty=sum(1 for v in cnt.values() if v == 0),
                hist=sorted(Counter(cnt.values()).items()), missing_keys=[i for i in range(257) if i not in cnt])

# (d)
pl = open(VL + 'plate_latin.txt', encoding='utf-8').read()
tab = re.search(r'\[TABULA\]\n(.*?)\n\[', pl, re.S).group(1)
tab = '\n'.join(l for l in tab.split('\n') if not l.startswith('#'))
sents = [s.strip() for s in tab.split('.') if s.strip()]
ls = lambda s: sum(ord(c) - 64 for c in s.upper() if 'A' <= c <= 'Z')
mod = [ls(s) for s in sents]
plate = [ls(s) + s.upper().count('U') for s in sents]
res['d1'] = dict(n=len(sents), pairs=list(zip(mod, plate)), whole=(sum(mod), sum(plate)), J=tab.upper().count('J'),
                 distinct=len(set(mod + plate)))
sums = mod + plate


def dtest(Mx, per_hundred=False):
    Rx = ranges(Mx)
    if per_hundred:
        ps = []
        for x in sums:
            if x <= 256:
                ps.append(1.0 if x in Mx else sum(1 for y in Mx if 0 <= y <= 256) / 257)
            else:
                h = (x // 100) * 100
                ps.append(sum(1 for y in Mx if h <= y < h + 100) / 100)
    else:
        ps = [dens_of(x, Rx) for x in sums]
    obs = sum(1 for x in sums if x in Mx)
    dist = pb(ps)
    return dict(obs=obs, exp=sum(ps), var=sum(p * (1 - p) for p in ps), P_ge=sum(dist[obs:]), P_le=sum(dist[:obs + 1]),
                present=[x for x in sums if x in Mx], dens=[(lo, hi, c, round(d, 6)) for lo, hi, c, n, d in Rx], sizeM=len(Mx))


res['d2'] = dtest(M)
res['d2_perhundred'] = dtest(M, True)
res['d2_inrev'] = sum(1 for x in sums if x in R_set)
res['d2_inkey'] = [x for x in sums if x in K_set]
res['d2_mod_inM'] = sum(1 for x in sums if x % P in M)
res['d2_ranges'] = Counter('0-256' if x <= 256 else '257-999' if x <= 999 else '1000-9999' for x in sums)

# X1: remove the Tabula table div and the summary paragraph
i_tbl = RAW_HTML.index('Verum, sine mendacio')
d0 = RAW_HTML.rindex('<div class="tbl">', 0, i_tbl)
d1 = RAW_HTML.index('</div>', i_tbl) + len('</div>')
i_p = RAW_HTML.index('The whole, in this transcription')
p0 = RAW_HTML.rindex('<p>', 0, i_p)
p1 = RAW_HTML.index('</p>', i_p) + len('</p>')
assert d1 <= p0
removed_html = RAW_HTML[d0:d1] + RAW_HTML[p0:p1]
X1_html = RAW_HTML[:d0] + RAW_HTML[d1:p0] + RAW_HTML[p1:]
removed_text_len = len(html_text(RAW_HTML[d0:d1])) + len(html_text(RAW_HTML[p0:p1]))
removed_text_len_ws = len(re.sub(r'\s+', ' ', html_text(RAW_HTML[d0:d1])).strip()) + len(re.sub(r'\s+', ' ', html_text(RAW_HTML[p0:p1])).strip())
res['X1_removed_chars'] = dict(html=len(removed_html), text=removed_text_len, text_ws_collapsed=removed_text_len_ws)
X1_rev = set(extract(html_text(X1_html)))
M_X1 = X1_rev | K_set
res['d4'] = dtest(M_X1)
res['d4_perhundred'] = dtest(M_X1, True)
# d3: sums in removed parts but nowhere else
rem_ints = set(extract(html_text(removed_html)))
res['d3'] = sorted(x for x in set(sums) if x in rem_ints and x not in X1_rev and x not in K_set)
res['d3_n'] = len(res['d3'])

# X2: whole plate passage
x0 = RAW_HTML.rindex('<p>', 0, RAW_HTML.index("The Emerald Tablet's plate and the rongorongo"))
x1 = RAW_HTML.rindex('<p>', 0, RAW_HTML.index('Readings brought to the review'))
X2_html = RAW_HTML[:x0] + RAW_HTML[x1:]
res['X2_removed_chars'] = dict(html=x1 - x0, text=len(html_text(RAW_HTML[x0:x1])))
M_X2 = set(extract(html_text(X2_html))) | K_set
res['d6'] = dtest(M_X2)

# d7: X1 + drop fractional runs
M_X1f = set(extract(html_text(X1_html), drop_frac=True)) | set(extract(KEY, drop_frac=True))
res['d7'] = dtest(M_X1f)

# d8
res['d8'] = dict(in_MX1=[x in M_X1 for x in (sum(mod), sum(plate))], in_key=[x in K_set for x in (sum(mod), sum(plate))])

# X3: X2 plus the change-log <li> entries mentioning the plate / Tabula sums
lis = [(m.start(), m.end()) for m in re.finditer(r'<li\b.*?</li>', X2_html, re.S)]
cut = [(a, b) for a, b in lis if any(str(s) in X2_html[a:b] for s in sums + [sum(mod), sum(plate)]) and ('plate' in X2_html[a:b] or 'Tabula' in X2_html[a:b])]
X3_html = X2_html
for a, b in reversed(cut):
    X3_html = X3_html[:a] + X3_html[b:]
M_X3 = set(extract(html_text(X3_html))) | K_set
res['X3_cut_li'] = len(cut)
res['d_X3'] = dtest(M_X3)
res['d_X3_perhundred'] = dtest(M_X3, True)
res['d_X3_whole'] = [x in M_X3 for x in (sum(mod), sum(plate))]

# d5 contexts in X1 text
x1t = re.sub(r'\s+', ' ', html_text(X1_html))
ctx = {}
for x in res['d4']['present']:
    m = re.search(r'(?<![0-9A-Za-z])' + str(x) + r'(?![0-9A-Za-z])', x1t)
    occ = len(re.findall(r'(?<![0-9A-Za-z])' + str(x) + r'(?![0-9A-Za-z])', x1t))
    ctx[x] = (occ, x1t[max(0, m.start() - 60):m.end() + 40] if m else None)
res['d5'] = ctx

# (e)
def placed(path):
    Tj = json.load(open(path, encoding='utf-8'))
    ls_n = vp = 0
    cells_vp = set(); cells_ls = set(); digitwords = []; nolet = 0
    for k, v in Tj.items():
        c = int(k)
        for w in v['words']:
            s = ls(w)
            if not re.search('[A-Za-z]', w):
                nolet += 1
            if re.search('[0-9]', w):
                digitwords.append((c, w, s % P == c))
            if s % P == c:
                ls_n += 1; cells_ls.add(c)
            else:
                vp += 1; cells_vp.add(c)
    return dict(total=ls_n + vp, ls=ls_n, vp=vp, cells_vp=len(cells_vp),
                no_ls_cells=sorted(set(range(257)) - cells_ls), digitwords=digitwords, nolet=nolet)

res['e'] = {}
for f in ['emerald_tablet.json', 'emerald_tablet.pre-terminus-20260918.json', 'emerald_tablet.pre-aim-20260918.json',
          'emerald_tablet.pre-rotate-20260918.json', 'emerald_tablet.pre-toth-20260918.json',
          'emerald_tablet.pre-rongorongo-20260919.json', 'emerald_tablet.pre-plate-20260919.json']:
    r = placed(BASE + f)
    res['e'][f] = {k: v for k, v in r.items() if k != 'digitwords'}
    res['e'][f]['digit_words_meeting_rule'] = [(c, w) for c, w, ok in r['digitwords'] if ok]
    res['e'][f]['n_digit_words'] = len(r['digitwords'])

json.dump(res, open(OUT + 'verify_out.json', 'w'), indent=1, default=str, ensure_ascii=False)
for k, v in res.items():
    print(k, '=>', v)
