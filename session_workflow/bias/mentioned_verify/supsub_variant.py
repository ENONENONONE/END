# Variant: superscript/subscript digits read as their own digit runs (separate from adjacent ASCII digits).
import re
exec(open('verify.py').read().split("res = {}")[0])
SUP='⁰¹²³⁴⁵⁶⁷⁸⁹'; SUB='₀₁₂₃₄₅₆₇₈₉'
def supsub(t):
    ints=[]
    for m in re.finditer('['+SUP+']+',t): ints.append(int(''.join(str(SUP.index(c)) for c in m.group())))
    for m in re.finditer('['+SUB+']+',t): ints.append(int(''.join(str(SUB.index(c)) for c in m.group())))
    return set(ints)
rt=html_text(RAW_HTML)
M=set(extract(rt))|set(extract(KEY))
S=supsub(rt)|supsub(KEY)
new=S-M
print('sup/sub integers',len(S),'new to M',len(new),'new by range', [sum(1 for x in new if lo<=x<=hi) for lo,hi in [(0,256),(257,999),(1000,9999),(10000,100000)]], 'above', sum(1 for x in new if x>100000))
sums=[443,446,1436,1451,1027,1036,1071,1079,442,444,492,494,664,667,997,1003,317,319,320,322,1151,1157,254,257,552,556,962,968,466,468]
print('tabula sums among new:',[x for x in sums if x in new])
