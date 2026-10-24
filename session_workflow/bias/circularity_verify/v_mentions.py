"""Find uppercase mentions of tablet words in review units, longest-first masking.
Prints every unit that mentions one of the task's listed words, with an id, for manual classification."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
D = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/"
cur = json.load(open(D + "emerald_tablet.json"))
vocab = sorted({w for v in cur.values() for w in v["words"]}, key=len, reverse=True)
U = json.load(open(os.path.join(HERE, "v_units.json")))
units = [u["text"] for u in U["units"]] + ["[STRAY] " + s for s in U["stray"]]
LIST = ["PYRAMIDUM", "ATLANTIS", "TOTH", "THOTH", "SCRIBE", "TRISMEGISTUS", "AIM", "I AM",
        "ROTATION", "QUARTER TURN", "BOUNDARY", "TERMINUS", "HERMES TRISMEGISTUS", "RONGORONGO"]
added = json.load(open(os.path.join(HERE, "v_added.json")))
ADDED = sorted({w for _, _, w in added})
pats = [(w, re.compile(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])")) for w in vocab]


def mentions(t, mask=True):
    found = []
    s = t
    for w, p in pats:
        for m in p.finditer(s):
            found.append((w, m.start()))
        if mask:
            s = p.sub(lambda m: "#" * len(m.group()), s)
    return found


res = []
for i, t in enumerate(units):
    ms = mentions(t)
    res.append(ms)
json.dump({"units": units, "mentions": res}, open(os.path.join(HERE, "v_mentions.json"), "w"), ensure_ascii=False)
# summary counts
from collections import Counter, defaultdict
per = defaultdict(set)
occ = Counter()
for i, ms in enumerate(res):
    for w, _ in ms:
        per[w].add(i)
        occ[w] += 1
stray0 = len(U["units"])
print("units", len(units), "(of which stray", len(U["stray"]), ")")
tot_units = set()
nwords = 0
for w in ADDED:
    if per[w]:
        nwords += 1
        tot_units |= per[w]
print("added words mentioned:", nwords, "of", len(ADDED), "in", len(tot_units), "units; occurrences", sum(occ[w] for w in ADDED))
tu2 = {i for i in tot_units if i < stray0}
n2 = sum(1 for w in ADDED if any(i < stray0 for i in per[w]))
print("  excluding stray:", n2, "words in", len(tu2), "units; occurrences", sum(1 for i, ms in enumerate(res) if i < stray0 for w, _ in ms if w in ADDED))
for w in LIST:
    print(w, "units", len(per[w]), "occ", occ[w], "stray units", sum(1 for i in per[w] if i >= stray0))
# unmasked counts for reference
print("--- unmasked (substring-as-word) unit counts")
for w in LIST:
    p = re.compile(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])")
    print(w, sum(1 for t in units if p.search(t)))
if len(sys.argv) > 1:
    for w in LIST:
        print("=" * 20, w)
        for i in sorted(per[w]):
            print(f"[{i}] {units[i][:600]}")
