"""(c4) 'the cell(s) of X' / 'that of X' constructions over review units (blocks + stray)."""
import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "v_mentions.json")))
U = d["units"]
D = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
cur = json.load(open(D + "emerald_tablet.json"))
vocab = sorted({w for v in cur.values() for w in v["words"]}, key=len, reverse=True)
added = {w for _, _, w in json.load(open(os.path.join(HERE, "v_added.json")))}
pat = re.compile(r"(the cells? of|that of) ")
rows = []
anyof = 0
for i, t in enumerate(U):
    for m in pat.finditer(t):
        anyof += 1
        rest = t[m.end():]
        hit = None
        for w in vocab:
            if re.match(re.escape(w) + r"(?![A-Za-z])", rest):
                hit = w; break
        if hit is None:
            mm = re.match(r"[0-9A-Z][^\s,;.]*", rest)
            hit = ("NONWORD:" + mm.group()) if mm else None
        if hit:
            rows.append((i, m.group(1), hit, hit in added))
print("all 'the cell(s) of '/'that of ' matches:", anyof)
print("followed by a tablet word or a number/uppercase token:", len(rows))
for r in rows: print(r)
tw = [r for r in rows if not r[2].startswith("NONWORD")]
print("tablet words:", len(tw), "window words:", sum(r[3] for r in tw), sorted({r[2] for r in tw if r[3]}))
print("unit range", min(r[0] for r in rows), max(r[0] for r in rows))
