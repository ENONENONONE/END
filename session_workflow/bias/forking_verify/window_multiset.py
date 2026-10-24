# distinct word-multiset counts per integer target in a +-30 window (V spelling), deduplicating repeated-phrase rotations
import re
from collections import Counter
BASE='<scratchpad>/'
txt=open(BASE+'vl/plate_latin.txt',encoding='utf-8').read()
tab=txt.split('[TABULA]')[1].split('[PIMANDER]')[0]
tab='\n'.join(l for l in tab.splitlines() if not l.startswith('#'))
sents=[s for s in tab.split('.') if s.strip()]
toks=[re.findall('[a-z]+',s.lower()) for s in sents]
ls=lambda w:sum(ord(c)-96 for c in w)
for spell in ('modern','V'):
  seq=[(w.replace('u','v') if spell=='V' else w) for t in toks for w in t]; bd=[i for i,t in enumerate(toks) for w in t]
  for scope in ('whole','within'):
    ms={}
    n=len(seq)
    for i in range(n):
      s=0
      for j in range(i,n):
        if scope=='within' and bd[j]!=bd[i]: break
        s+=ls(seq[j]); ms.setdefault(s,set()).add(tuple(sorted(seq[i:j+1])))
    for t in (257,1027):
      win=[len(ms.get(x,())) for x in range(t-30,t+31) if x!=t]
      print(spell,scope,t,'multisets',len(ms.get(t,())),'window mean %.4f max %d n>=: %d'%(sum(win)/len(win),max(win),sum(1 for w in win if w>=len(ms.get(t,())))))
