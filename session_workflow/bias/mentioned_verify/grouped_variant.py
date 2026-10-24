# Variant: integers that exist in M only as pieces of digit-grouped numbers (thousands separators, comma or space),
# classified by reading their contexts (probe4.py output); six table-row list entries (308 471 698 711 714 974) are kept.
import re
exec(open('verify.py').read().split("res = {}")[0])
exec(open('control.py').read().split("# --- other Latin")[0].split("exec(open(")[0])
FRAG=[274,296,311,424,458,557,558,586,597,604,635,652,666,674,693,755,777,792,800,801,810,834,870,920,930]
rt=html_text(RAW_HTML)
K=set(extract(KEY))
M=set(extract(rt))|K
i_tbl = RAW_HTML.index('Verum, sine mendacio'); d0 = RAW_HTML.rindex('<div class="tbl">', 0, i_tbl); d1 = RAW_HTML.index('</div>', i_tbl) + 6
i_p = RAW_HTML.index('The whole, in this transcription'); p0 = RAW_HTML.rindex('<p>', 0, i_p); p1 = RAW_HTML.index('</p>', i_p) + 4
X1=set(extract(html_text(RAW_HTML[:d0] + RAW_HTML[d1:p0] + RAW_HTML[p1:])))|K
pl = open(VL + 'plate_latin.txt', encoding='utf-8').read()
tab = re.search(r'\[TABULA\]\n(.*?)\n\[', pl, re.S).group(1)
sents=[s.strip() for s in tab.split('.') if s.strip()]
ls = lambda s: sum(ord(c) - 64 for c in s.upper() if 'A' <= c <= 'Z')
sums=[ls(s) for s in sents]+[ls(s)+s.upper().count('U') for s in sents]
def test(Mx,mode):
    ps=[]
    for x in sums:
        if x<=256: ps.append(1.0); continue
        if mode=='range':
            lo,hi=(257,999) if x<=999 else (1000,9999)
        else:
            lo=max((x//100)*100,257); hi=(x//100)*100+99
        ps.append(sum(1 for y in Mx if lo<=y<=hi)/(hi-lo+1))
    obs=sum(1 for x in sums if x in Mx); d=pb(ps)
    return obs, round(sum(ps),4), float('%.4g'%sum(d[obs:]))
for nm,Mx in [('full',M),('X1',X1)]:
    Mg=Mx-set(FRAG)
    print(nm,'|M|',len(Mx),'->',len(Mg),' 257-999:',sum(1 for y in Mx if 257<=y<=999),'->',sum(1 for y in Mg if 257<=y<=999), round(sum(1 for y in Mg if 257<=y<=999)/743,6))
    for mode in ('range','hundred'):
        print('  ',mode,'orig',test(Mx,mode),'frag removed',test(Mg,mode))
print('fragments that are Tabula sums:',[x for x in FRAG if x in sums])
