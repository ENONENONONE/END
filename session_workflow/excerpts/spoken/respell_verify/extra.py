# extra checks; imports verify.py's definitions by exec (no re-run of controls)
import re, numpy as np, collections
src = open('verify.py').read().split("# ---------- per-word arrays ----------")[0]
exec(src)
N=len(words)
A=np.array([triple(w)[1]%P for w in words]); LA=np.array([triple(w)[0] for w in words])
out={}
for sch_name,sch in (("P",SCHEME_P),("M",SCHEME_M)):
    strs=[respell(first[w],sch) for w in words]
    B=np.array([triple(s)[1]%P for s in strs]); LB=np.array([len(s) for s in strs])
    ident=np.array([s==w.upper() for s,w in zip(strs,words)])
    anag=np.array([sorted(s)==sorted(w.upper()) for s,w in zip(strs,words)])
    for lab,mask,seeds in (("all",np.ones(N,bool),[7401,7402,7403,7404,7405]),("nonid",~ident,[7411,7412,7413,7414,7415])):
        idx=np.where(mask)[0]
        strata=collections.defaultdict(list)
        for i in idx: strata[(LA[i],LB[i])].append(i)
        meds=[];shares=[]
        for sd in seeds:
            rng=np.random.default_rng(sd); ds=[]
            for key,mem in strata.items():
                mem=np.array(mem); n=len(mem)
                if n<2: continue
                u=rng.integers(0,n-1,size=n); u=np.where(u>=np.arange(n),u+1,u)
                a=A[mem]; b=B[mem[u]]
                ds.append(np.minimum((a-b)%P,(b-a)%P))
            d=np.concatenate(ds); meds.append(float(np.median(d))); shares.append(float(np.mean(d<=10)))
        print(sch_name,lab,"ctl folded distance medians",meds,"mean",np.mean(meds),"share<=10 mean",round(np.mean(shares),5))
    na=np.where(anag&~ident)[0]
    print(sch_name,"non-identical anagram respellings",len(na),"examples",[(words[i],strs[i]) for i in na[:25]])
    # the phone -> letters that produce anagrams: most common
    if sch_name=="P":
        SP_=strs
print()
# example relation checks
def rels(a,b):
    return [r for r in REL_NAMES if REL[r][a,b]] + (["equal"] if a==b else [])
for w in ["knight","write","gnome","hour","debt","listen","colonel","wednesday","psalm","island","ghost","kaboom","schmaltz","rechargeable","jaskulski","selley","reissman"]:
    a=triple(w)[1]%P; bp=triple(respell(first[w],SCHEME_P))[1]%P; bm=triple(respell(first[w],SCHEME_M))[1]%P
    print(w,a,bp,bm,"A-P",rels(a,bp),"A-M",rels(a,bm))
for w in ["ab","abdel","a","abash","abet","abide","absent","abduct","add","admire","aber","abner","accursed","abe","absolute","abraham"]:
    sa=triple(w)[1]; p=respell(first[w],SCHEME_P); m=respell(first[w],SCHEME_M)
    print(w,first[w],p,sa-triple(p)[1],m,sa-triple(m)[1])
# HH AY1 inside longer pronunciations
cont=[];endw=[]
for w in words:
    for v,ph in entries[w].items():
        if len(ph)>2 and any(ph[i:i+2]==["HH","AY1"] for i in range(len(ph)-1)): cont.append((w,v))
        if len(ph)>2 and ph[-2:]==["HH","AY1"]: endw.append((w,v))
print("entries containing contiguous HH AY1 in a longer pron:",len(cont),"ending in HH AY1:",len(endw),endw[:30])
