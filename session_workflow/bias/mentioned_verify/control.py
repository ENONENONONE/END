# Extra variants and controls beyond the investigator's (d) test.
# Seed for the shuffle control: 20260919 (random.Random).
import re, random, json
exec(open('<scratchpad>/bias/mentioned_verify/verify.py').read().split("res = {}")[0])

out = {}
rt = html_text(RAW_HTML)
pl = open(VL + 'plate_latin.txt', encoding='utf-8').read()
def section(name):
    s = re.search(r'\[' + name + r'\]\n(.*?)(?:\n\[|\Z)', pl, re.S).group(1)
    return '\n'.join(l for l in s.split('\n') if not l.startswith('#'))
ls = lambda s: sum(ord(c) - 64 for c in s.upper() if 'A' <= c <= 'Z')
tab = section('TABULA')
sents = [s.strip() for s in tab.split('.') if s.strip()]
sums = [ls(s) for s in sents] + [ls(s) + s.upper().count('U') for s in sents]

# --- cuts
i_tbl = RAW_HTML.index('Verum, sine mendacio'); d0 = RAW_HTML.rindex('<div class="tbl">', 0, i_tbl); d1 = RAW_HTML.index('</div>', i_tbl) + 6
i_p = RAW_HTML.index('The whole, in this transcription'); p0 = RAW_HTML.rindex('<p>', 0, i_p); p1 = RAW_HTML.index('</p>', i_p) + 4
X1_html = RAW_HTML[:d0] + RAW_HTML[d1:p0] + RAW_HTML[p1:]
x0 = RAW_HTML.rindex('<p>', 0, RAW_HTML.index("The Emerald Tablet's plate and the rongorongo"))
x1 = RAW_HTML.rindex('<p>', 0, RAW_HTML.index('Readings brought to the review'))
X2_html = RAW_HTML[:x0] + RAW_HTML[x1:]
# X3: X2 minus the verification-table row that records the Tabula sums
i_v = X2_html.index('the fifteen sentence sums in both spellings')
r0 = X2_html.rindex('<tr', 0, i_v); r1 = X2_html.index('</tr>', i_v) + 5
X3_html = X2_html[:r0] + X2_html[r1:]
out['X3_row_removed_chars_html'] = r1 - r0
K_set = set(extract(KEY))
M_full = set(extract(rt)) | K_set
M_X1 = set(extract(html_text(X1_html))) | K_set
M_X2 = set(extract(html_text(X2_html))) | K_set
M_X3 = set(extract(html_text(X3_html))) | K_set
out['sizes'] = dict(full=len(M_full), X1=len(M_X1), X2=len(M_X2), X3=len(M_X3))
out['X3_whole_tabula_in'] = [x in M_X3 for x in (sum(sums[:15]), sum(sums[15:]))]


def ptest(Mx, xs, mode):
    ps = []
    for x in xs:
        if x <= 256:
            ps.append(1.0)  # M covers 0-256 completely in every variant (checked below)
        elif mode == 'range':
            lo, hi = (257, 999) if x <= 999 else (1000, 9999) if x <= 9999 else (10000, 100000)
            ps.append(sum(1 for y in Mx if lo <= y <= hi) / (hi - lo + 1))
        elif mode == 'hundred':
            h = (x // 100) * 100; lo = max(h, 257)
            ps.append(sum(1 for y in Mx if lo <= y <= h + 99) / (h + 99 - lo + 1))
        elif mode == 'window50':  # local density in [x-50, x+50] without x itself
            ps.append(sum(1 for y in Mx if x - 50 <= y <= x + 50 and y != x and y > 256) / sum(1 for y in range(x - 50, x + 51) if y != x and y > 256))
    obs = sum(1 for x in xs if x in Mx)
    dist = pb(ps)
    return dict(obs=obs, n=len(xs), exp=round(sum(ps), 4), P_ge=float('%.4g' % sum(dist[obs:])), P_le=float('%.4g' % sum(dist[:obs + 1])))

for nm, Mx in [('full', M_full), ('X1', M_X1), ('X2', M_X2), ('X3', M_X3)]:
    assert all(i in Mx for i in range(257)), nm
    out['tabula_' + nm] = {m: ptest(Mx, sums, m) for m in ('range', 'hundred', 'window50')}

# --- other Latin on the same plate, same test (split on . : ? ; as sentence ends)
for sec in ('PIMANDER', 'CAPTION'):
    txt = section(sec)
    parts = [s.strip() for s in re.split(r'[.:?;]', txt) if s.strip() and ls(s) > 0]
    xs = [ls(s) for s in parts] + [ls(s) + s.upper().count('U') for s in parts]
    out[sec] = dict(n_parts=len(parts), sums=xs,
                    **{nm: {m: ptest(Mx, xs, m) for m in ('range', 'hundred', 'window50')} for nm, Mx in [('full', M_full), ('X2', M_X2), ('X3', M_X3)]})

# --- shuffle control: Tabula words re-cut into 15 sentences of the original word counts
words = [re.findall(r'[A-Za-z]+', s) for s in sents]
lens = [len(w) for w in words]
flat = [x for w in words for x in w]
rng = random.Random(20260919)
N = 10000
counts = {'full': [], 'X1': [], 'X3': []}
for _ in range(N):
    f = flat[:]; rng.shuffle(f); i = 0; xs = []
    for L in lens:
        chunk = ' '.join(f[i:i + L]); i += L
        xs.append(ls(chunk)); xs.append(ls(chunk) + chunk.upper().count('U'))
    for nm, Mx in [('full', M_full), ('X1', M_X1), ('X3', M_X3)]:
        counts[nm].append(sum(1 for x in xs if x in Mx))
obsd = {'full': sum(1 for x in sums if x in M_full), 'X1': sum(1 for x in sums if x in M_X1), 'X3': sum(1 for x in sums if x in M_X3)}
out['shuffle_seed'] = 20260919
out['shuffle'] = {nm: dict(obs=obsd[nm], mean=round(sum(c) / N, 4), sd=round((sum((v - sum(c) / N) ** 2 for v in c) / (N - 1)) ** 0.5, 4),
                            frac_ge_obs=sum(1 for v in c if v >= obsd[nm]) / N, frac_le_obs=sum(1 for v in c if v <= obsd[nm]) / N, min=min(c), max=max(c))
                  for nm, c in counts.items()}

# --- grouped-number fragments: comma groups joined; fragment-only integers
def extract_grouped(t):
    # join 1-3 digits followed by ,ddd groups into one integer; then drop fragments
    t2 = re.sub(r'(?<![0-9])(\d{1,3}(?:,\d{3})+)(?![0-9])', lambda m: m.group(1).replace(',', ''), t)
    return t2
Mg = set(extract(extract_grouped(rt))) | set(extract(extract_grouped(KEY)))
out['comma_join'] = dict(size=len(Mg), dens=[(lo, hi, c, round(d, 6)) for lo, hi, c, n, d in ranges(Mg)])
Mg_X1 = set(extract(extract_grouped(html_text(X1_html)))) | set(extract(extract_grouped(KEY)))
out['comma_join_X1'] = {m: ptest(Mg_X1, sums, m) for m in ('range', 'hundred', 'window50')}
# fragment-only: integers whose every occurrence (in review+key) sits inside a comma- or space-grouped run
GRP = re.compile(r'(?<![0-9])\d{1,3}(?:[, ]\d{3})+(?![0-9])')
def spans_grouped(t):
    return [m.span() for m in GRP.finditer(t)]
def occ(t):
    sp = spans_grouped(t); res = {}
    for m in re.finditer(r'[0-9]+', t):
        a, b = m.span()
        L = t[a - 1] if a else ''; R = t[b] if b < len(t) else ''
        if re.match('[A-Za-z]', L or ' ') or re.match('[A-Za-z]', R or ' '): continue
        ing = any(s <= a and b <= e for s, e in sp)
        res.setdefault(int(m.group()), []).append(ing)
    return res
o1 = occ(rt); o2 = occ(KEY)
frag_only = sorted(x for x in M_full if all((o1.get(x, []) + o2.get(x, [])) or [False]) and x > 256)
out['fragment_only_above256'] = dict(n=len(frag_only), in_257_999=[x for x in frag_only if x <= 999], n_1000_9999=sum(1 for x in frag_only if 1000 <= x <= 9999))

json.dump(out, open(OUT + 'control_out.json', 'w'), indent=1, ensure_ascii=False)
for k, v in out.items():
    print(k, '=>', v)
