import re,json,collections
P=257
ROOT="~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
T=json.load(open(ROOT+'emerald_tablet.json')); W={int(k):v['words'] for k,v in T.items()}; TABLET={x for v in W.values() for x in v}
dl3={pow(3,k,P):k for k in range(256)}; dl5={pow(5,k,P):k for k in range(256)}
ring=lambda n:min(dl5[n]%64,64-dl5[n]%64)
ls=lambda s:sum(ord(c)-96 for c in s)
def parse(path):
    pages={};cur=None;rows=[]
    for line in open(path,encoding='ascii',errors='replace'):
        line=line.rstrip('\n')
        if not line or line.startswith('#'): continue
        m=re.match(r'^<(f\w+)>\s*<!(.*)>',line)
        if m:
            cur=m.group(1); pages[cur]=dict(re.findall(r'\$(\w)=(\w+)',m.group(2))); continue
        m=re.match(r'^<(f\w+)\.(\w+),([^>]*)>\s*(.*)$',line)
        if not m: continue
        page,ln,loc,txt=m.groups()
        txt=re.sub(r'<![^>]*>','',txt)            # inline comments
        txt=re.sub(r'<[^>]*>','.',txt)            # other tags (<%>, <$>, <->) act as breaks
        txt=re.sub(r'\[([^:\]]*):[^\]]*\]',r'\1',txt)   # alternative readings: take the first
        txt=re.sub(r'@\d+;','?',txt)              # special glyph codes → unreadable marker
        txt=txt.replace('{','').replace('}','').replace("'",'')
        rows.append((page,ln,loc,txt))
    return pages,rows
def words(txt,comma_breaks=False):
    if comma_breaks: txt=txt.replace(',','.')
    else: txt=txt.replace(',','')
    return [w for w in txt.split('.') if w]
