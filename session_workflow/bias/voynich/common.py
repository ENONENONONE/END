import re, sys, collections
VL="<scratchpad>/vl/"
sys.path.insert(0, VL)
import voy
P=257
def load_voynich():
    pages, rows = voy.parse(VL+"ZL3b-n.txt")
    toks=[]
    for page,ln,loc,txt in rows:
        for w in voy.words(txt):
            if re.fullmatch('[a-z]+', w): toks.append(w)
    return toks
def load_plate():
    sec={}; cur=None
    for line in open(VL+"plate_latin.txt", encoding='utf-8'):
        line=line.rstrip('\n')
        if not line or line.startswith('#'): continue
        m=re.fullmatch(r'\[(\w+)\]', line.strip())
        if m: cur=m.group(1); sec[cur]=""; continue
        sec[cur]+=line+" "
    return sec
def forms(text):
    return re.findall('[a-z]+', text.lower())
ID=list(range(1,27))  # value of letter index i (0=a) is ID[i]
def key(w, val=ID):
    k=len(w); s=0; b=0
    for i,c in enumerate(w,1):
        v=val[ord(c)-97]; s+=v; b+=i*v
    return (k, s%P, b%P), s
def keys_all(w, val=ID):
    (k,s,b), sraw = key(w,val)
    rev=(k, s, ((k+1)*s - b)%P)
    atb=(k, (27*k - sraw)%P, (27*k*(k+1)//2 - b)%P)
    return dict(cell=s, ks=(k,s), ksb=(k,s,b), rev=rev, atb=atb)
def latin_sets(lat_forms):
    S=dict(cell=set(), ks=set(), ksb=set())
    for f in lat_forms:
        K=keys_all(f)
        S['cell'].add(K['cell']); S['ks'].add(K['ks']); S['ksb'].add(K['ksb'])
    return S
def count_matches(vtypes, S, val=ID, which=('cell','ks','ksb','rev','atb')):
    c={x:0 for x in which}; hits={x:[] for x in which}
    for w in vtypes:
        K=keys_all(w,val)
        for x in which:
            tgt = 'ksb' if x in ('rev','atb') else x
            if K[x] in S[tgt]: c[x]+=1; hits[x].append(w)
    return c, hits
