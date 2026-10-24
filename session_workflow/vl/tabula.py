import json,re
P=257
T=json.load(open('~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/emerald_tablet.json')); W={int(k):v['words'] for k,v in T.items()}; allw={x:int(k) for k,v in T.items() for x in v['words']}
ls=lambda s:sum(ord(c)-64 for c in s.upper() if c.isalpha())
SENT=[
("Verum, sine mendacio, certum et verissimum.","True, without falsehood, certain and most true."),
("Quod est inferius est sicut quod est superius, et quod est superius est sicut quod est inferius, ad perpetranda miracula rei unius.","What is below is like what is above, and what is above is like what is below, to accomplish the miracles of the one thing."),
("Et sicut omnes res fuerunt ab uno, meditatione unius, sic omnes res natae fuerunt ab hac una re, adaptatione.","And as all things were from one, by the meditation of one, so all things were born from this one thing, by adaptation."),
("Pater eius est Sol, mater eius Luna; portavit illud ventus in ventre suo; nutrix eius terra est.","Its father is the Sun, its mother the Moon; the wind carried it in its belly; its nurse is the earth."),
("Pater omnis telesmi totius mundi est hic.","The father of all the perfection of the whole world is here."),
("Vis eius integra est, si versa fuerit in terram.","Its power is whole if it is turned into earth."),
("Separabis terram ab igne, subtile a spisso, suaviter cum magno ingenio.","You shall separate the earth from the fire, the subtle from the gross, gently, with great skill."),
("Ascendit a terra in coelum, iterumque descendit in terram, et recipit vim superiorum et inferiorum.","It rises from earth to heaven and descends again to earth, and receives the power of things above and things below."),
("Sic habebis gloriam totius mundi.","So you shall have the glory of the whole world."),
("Ideo fugiat a te omnis obscuritas.","Therefore let all darkness flee from you."),
("Hic est totius fortitudinis fortitudo fortis, quia vincet omnem rem subtilem, omnemque solidam penetrabit.","This is the strong strength of all strength, for it will overcome every subtle thing and pierce every solid."),
("Sic mundus creatus est.","Thus the world was made."),
("Hinc erunt adaptationes mirabiles, quarum modus hic est.","From this will come wonderful adaptations, of which this is the way."),
("Itaque vocatus sum Hermes Trismegistus, habens tres partes philosophiae totius mundi.","And so I am called Hermes Trismegistus, having the three parts of the philosophy of the whole world."),
("Completum est quod dixi de operatione Solis.","What I have said of the working of the Sun is complete."),
]
if __name__=="__main__":
    tot=0;totv=0;nw=0;nl=0
    for i,(la,en) in enumerate(SENT,1):
        s=ls(la); u=la.upper().count('U'); tot+=s; totv+=s+u; ws=re.findall(r"[A-Za-z]+",la); nw+=len(ws); nl+=sum(len(x) for x in ws)
        print(f"{i:>2}. {s:>5} ≡ {s%P:>3} {W[s%P][0]:<26} | as cut (V for U, +{u:>2}) {s+u:>5} ≡ {(s+u)%P:>3} {W[(s+u)%P][0]:<24} | {la[:60]}")
    print(f"whole Tabula: {nw} words, {nl} letters, sum {tot} ≡ {tot%P} {W[tot%P][:3]} · as cut {totv} ≡ {totv%P} {W[totv%P][:3]}")
    voc={}
    for la,_ in SENT:
        for x in re.findall(r"[A-Za-z]+",la): voc.setdefault(x.upper(),0); voc[x.upper()]+=1
    print(len(voc),"distinct words")
    for x in sorted(voc,key=lambda x:(-voc[x],x)): print(f"   {x:<14}×{voc[x]:<2}{ls(x):>4} ≡ {ls(x)%P:>3} {', '.join(W[ls(x)%P][:3]):<40}{'  ← itself a tablet word' if x in allw else ''}")
