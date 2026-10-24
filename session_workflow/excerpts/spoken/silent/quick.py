import re
from aligner import *
P={}
for line in open('../../cmu/cmudict.dict'):
    line=line.split('#')[0].strip()
    if not line: continue
    w,*ph=line.split()
    if w in P: continue
    P[w]=[re.sub(r'\d','',x) for x in ph]
import sys
for w in sys.argv[1:]:
    c,st=align(w,P[w]); s,o,_=silent_letters(w,st)
    print(f"{w:12s} {c:5.2f} {render(w,st)}  SIL={[(i,ch,cat) for i,ch,cat in s]} OTHER={o}")
