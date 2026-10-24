import re, numpy as np, collections
src = open('verify.py').read().split("# ---------- per-word arrays ----------")[0]
exec(src)
N=len(words)
A=np.array([triple(w)[1]%P for w in words]); LA=np.array([triple(w)[0] for w in words])
firststr={w:" ".join(re.sub(r"\d","",p) for p in first[w]) for w in words}
for sch_name,sch in (("P",SCHEME_P),("M",SCHEME_M)):
    strs=[respell(first[w],sch) for w in words]
    B=np.array([triple(s)[1]%P for s in strs]); LB=np.array([len(s) for s in strs])
    ident=np.array([s==w.upper() for s,w in zip(strs,words)])
    for lab,mask,seeds in (("all",np.ones(N,bool),[7501,7502,7503,7504,7505]),("nonid",~ident,[7511,7512,7513,7514,7515])):
        idx=np.where(mask)[0]
        # observed among unequal pairs
        a=A[idx]; b=B[idx]; ne=(a!=b)&(a!=0)&(b!=0)
        o1=np.mean(CHAR[a[ne]]==CHAR[b[ne]]); o2=np.mean(RING[a[ne]]==RING[b[ne]])
        strata=collections.defaultdict(list)
        for i in idx: strata[(LA[i],LB[i])].append(i)
        c1=[];c2=[];leak=[]
        for sd in seeds:
            rng=np.random.default_rng(sd); S=[];Pp=[]
            for key,mem in strata.items():
                mem=np.array(mem); n=len(mem)
                if n<2: continue
                u=rng.integers(0,n-1,size=n); u=np.where(u>=np.arange(n),u+1,u)
                S.append(mem); Pp.append(mem[u])
            S=np.concatenate(S); Pp=np.concatenate(Pp)
            ca=A[S]; cb=B[Pp]; cne=(ca!=cb)&(ca!=0)&(cb!=0)
            c1.append(np.mean(CHAR[ca[cne]]==CHAR[cb[cne]])); c2.append(np.mean(RING[ca[cne]]==RING[cb[cne]]))
            leak.append(np.mean([strs[i]==strs[j] for i,j in zip(S,Pp)]))
        print(sch_name,lab,f"unequal pairs n={ne.sum()} m1 obs {o1:.5f} ctl {np.mean(c1):.5f} [{min(c1):.5f},{max(c1):.5f}] | m2 obs {o2:.5f} ctl {np.mean(c2):.5f} [{min(c2):.5f},{max(c2):.5f}] | control partner with identical respelling share {np.mean(leak):.5f}")
print("exact unequal-pair baselines over the field: same char", 128*127*2/(256*255), "same ring", (2*4*3+31*8*7)/(256*255))
