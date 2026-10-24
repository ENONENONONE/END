"""Independent review-text extraction for (c). Writes v_units.json (working input, not a report)."""
import json, os, re
from bs4 import BeautifulSoup, NavigableString
HERE = os.path.dirname(os.path.abspath(__file__))
D = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
html = open(D + "cascade_corpus_review.html", encoding="utf-8").read()
soup = BeautifulSoup(html, "lxml")
for t in soup(["script", "style"]):
    t.decompose()
BLOCK = ["p", "li", "h1", "h2", "h3", "h4", "pre", "tr"]
blocks = soup.find_all(BLOCK)
# keep outermost only (avoid double counting nested blocks e.g. p inside li, tr inside li)
outer = [b for b in blocks if not any(p.name in BLOCK for p in b.parents)]
print("blocks all", len(blocks), "outermost", len(outer))
units = []
for bi, b in enumerate(outer):
    if b.name == "tr":
        txt = " | ".join(c.get_text(" ", strip=True) for c in b.find_all(["td", "th"]))
        units.append({"block": bi, "tag": "tr", "text": re.sub(r"\s+", " ", txt)})
    else:
        txt = re.sub(r"\s+", " ", b.get_text(" ", strip=True))
        parts = re.split(r"(?<=[.;!?])\s+(?=[A-Z0-9ΦΓΣΩ√(\"“'−–·×₀-₉⁰-⁹])", txt)
        for s in parts:
            if s.strip():
                units.append({"block": bi, "tag": b.name, "text": s.strip()})
print("units", len(units))
# text outside any block
body = soup.body or soup
stray = []
for s in body.find_all(string=True):
    if isinstance(s, NavigableString) and s.strip():
        if not any(p.name in BLOCK for p in s.parents):
            stray.append(s.strip())
print("stray text nodes outside blocks:", len(stray))
json.dump({"units": units, "stray": stray}, open(os.path.join(HERE, "v_units.json"), "w"), ensure_ascii=False)
