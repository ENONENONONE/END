# (d) on each tablet version, plus sensitivity of (e)(ii) to a half-circle azimuth range. No RNG.
import json, math
P=257; ROOT="~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
K33={0,1,2,3,8,15,16,17,23,44,46,62,72,73,86,92,111,117,119,120,128,129,136,137,138,140,142,153,225,240,241,255,256}
DL={pow(3,k,P):k for k in range(256)}; inv=lambda n:pow(n,P-2,P)
roots={n:[m for m in range(1,P) if m*m%P==n] for n in range(P)}
def R(n):
    r=[(P-n)%P,n*n%P,2*n%P,129*n%P,17*n%P,5*n%P,3*n%P]
    if n: r+= [inv(n),DL[n]]+roots[n]
    else: r+=[0]
    if (n+120)%P: r.append((n-120)*inv((n+120)%P)%P)
    return r
hit={c:(c in K33 or any(v in K33 for v in R(c))) for c in range(P)}
for f in ["pre-terminus-20260918","pre-aim-20260918","pre-rotate-20260918","pre-toth-20260918","pre-rongorongo-20260919","pre-plate-20260919",None]:
    T=json.load(open(ROOT+("emerald_tablet.json" if f is None else f"emerald_tablet.{f}.json"),encoding="utf-8"))
    E=[]
    for p in T:
        for w in T[p]["words"]:
            v=[ord(c)-64 for c in w.upper() if "A"<=c<="Z"]; E.append((len(v),sum(v)))
    n=sum(1 for k,s in E if hit[s%P] or (27*k-s)%P in K33)
    atK=sum(1 for k,s in E if s%P in K33)
    print(f"{f or 'current':<26} entries {len(E):>5}  K33 word-test {n}/{len(E)} = {n/len(E):.4f}  words whose cell is in K33 {atK} ({atK/len(E):.4f})")
# new words added between pre-plate and current
A=json.load(open(ROOT+"emerald_tablet.pre-plate-20260919.json",encoding="utf-8")); B=json.load(open(ROOT+"emerald_tablet.json",encoding="utf-8"))
old={(p,w) for p in A for w in A[p]["words"]}; new=[(p,w) for p in B for w in B[p]["words"] if (p,w) not in old]
def ks(w):
    v=[ord(c)-64 for c in w.upper() if "A"<=c<="Z"]; return len(v),sum(v)
nn=sum(1 for p,w in new if hit[ks(w)[1]%P] or (27*ks(w)[0]-ks(w)[1])%P in K33)
print("added since pre-plate:",len(new),"word-test hits",nn, round(nn/len(new),4))
def btail(n,p,k): return sum(math.comb(n,j)*p**j*(1-p)**(n-j) for j in range(k,n+1))
for lab,cov,arc in (("full circle",88,360),("half circle 0-180 (n=0..21 windows)",None,180)):
    if cov is None:
        cen=[2.5*(55*n%144) for n in range(22)]
        # coverage of [0,180) by windows [c-2,c+2] (mod 360)
        step=0.001; cnt=0; x=0.0
        cov=sum(1 for i in range(180000) if any(min(abs(i*step-c)%360,360-abs(i*step-c)%360)<=2 for c in cen))*step
    p=cov/arc
    print(f"{lab}: covered {cov:.1f} of {arc}, p={p:.4f}, expected of 21 {21*p:.3f}, P(>=7)={btail(21,p,7):.4f}")
