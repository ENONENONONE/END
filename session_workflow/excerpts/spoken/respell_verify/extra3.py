import re, numpy as np, collections
src = open('verify.py').read().split("# ---------- per-word arrays ----------")[0]
exec(src)
members5=["heye","hi","high","hy","jai"]; members4=["heye","hi","high","hy"]
for sch_name,sch,rl in (("P",SCHEME_P,3),("M",SCHEME_M,2)):
    bc=triple(respell(["HH","AY1"],sch))[1]%P
    for excl,lab in ((set(members5)|{"hye"},"excl hye"),(set(members5),"incl hye")):
        for mem in (members5,members4):
            ex={m:[] for m in ["m1","m2","m3","m4","m5"]}
            for w in mem:
                a=triple(w)[1]%P
                pool=[triple(respell(first[v],sch))[1]%P for v in words if len(v)==len(w) and len(respell(first[v],sch))==rl and v not in excl]
                pool=np.array(pool)
                nz=pool!=0
                ex["m1"].append(np.mean(CHAR[pool[nz]]==CHAR[a])); ex["m2"].append(np.mean(RING[pool[nz]]==RING[a]))
                ex["m3"].append(np.mean(LINK[a,pool])); ex["m4"].append(np.mean(INK[pool])); ex["m5"].append(np.mean(pool==a))
            print(sch_name,lab,len(mem),"exact expected control:",{k:round(float(np.mean(v)),5) for k,v in ex.items()})
