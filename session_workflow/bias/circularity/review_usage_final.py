#!/usr/bin/env python3
"""(c) final: automatic occurrence classes from review_usage.py's rules, then a
recorded manual decision for every occurrence that the rules could not settle
(each with its reason). Classes:
  LABEL_OP     W names a number produced by an operation, chain, count or date
               (Atbash mirror, inverse, half, fold, Γ, squaring, sum of cells...)
  LABEL_COLOC  W named as the occupant of a cell reached by ANOTHER string's
               letter sum ('X = 173, the cell of QUARTER TURN', 'X = 80 with W')
  OPERAND      W's value used as a term/factor in arithmetic ('g × AIM')
  PROPERTY     a number named as W's φ part ('104 is ZRN's φ part')
  OWN          W's own letter reading (W = n, W n, W at n, W's cell)
  OTHER        lists, bookkeeping, headings, word-level transforms
'Label use' (task c) = LABEL_OP or LABEL_COLOC. For I AM the cell (1 = value
placement, pre-existing; 23 = letter-sum placement, added in the window) is
recorded. Matching is on uppercase tablet words only. No randomness."""
import json, os, re
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
TAB = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/emerald_tablet.json"
S = json.load(open(os.path.join(HERE, "review_sentences.json")))
D = json.load(open(os.path.join(HERE, "diff_report.json")))
cur = json.load(open(TAB))
added = {}
for st in D["steps"]:
    for a in st["added"]:
        added.setdefault(a["word"], []).append(a["cell"])
step_of = {a["word"]: f"{st['from']}->{st['to']}" for st in D["steps"] for a in st["added"]}
EXTRA = {"AIM": [23], "HERMES": [68]}  # named in the task list, pre-existing
targets = dict(added); targets.update(EXTRA)
targets["I AM"] = [1, 23]

vocab = sorted({w for v in cur.values() for w in v["words"] if re.search(r"[A-Z]", w)},
               key=lambda w: (-len(w), w))
pat = re.compile(r"(?<![A-Za-z])(" + "|".join(re.escape(w) for w in vocab) + r")(?![A-Za-z])")
CELLOF = re.compile(r"(?:cells? of|that of|onto|lands? on|landing on|lands? at|shares the cell of)\s+"
                    r"(?:(?:the )?[A-Z][A-Z0-9' -]*?(?:,\s+|\s+and\s+|\s+or\s+))*$")

# manual decisions: (sentence, word) -> class for all occurrences, or list per occurrence
# each entry: (classes, reason, cell_for_I_AM)
M = {
 (100, "I AM"): ("LABEL_OP", "one-letter Atbash 26 -> 1 named I AM", 1),
 (109, "I AM"): ("LABEL_OP", "table row: mirror of Z lands on 1, cell's words listed", 1),
 (155, "I AM"): ("LABEL_OP", "Γ(∞) = 1 read as I AM", 1),
 (162, "I AM"): ("LABEL_OP", "Γ orbit holds cell 1, named I AM", 1),
 (526, "I AM"): ("LABEL_OP", "squaring tower ends on 1, 'the cell where I AM sits'", 1),
 (841, "I AM"): ("LABEL_OP", "table: a power evaluates to 1, named I AM", 1),
 (1183, "I AM"): ("LABEL_OP", "table: 2^16 ≡ 1, named I AM", 1),
 (1122, "I AM"): ("LABEL_OP", "day number 1 -> position 1, named", 1),
 (1234, "I AM"): ("OWN", "I AM at 1 stated as placement", 1),
 (1591, "I AM"): (["LABEL_OP", "OTHER"], "opcode 1 named I AM; second is a quoted phrase", 1),
 (2133, "I AM"): ("LABEL_OP", "Γ(∞) = 1 = I AM", 1),
 (2270, "I AM"): ("LABEL_OP", "Γ(∞) = 1 = I AM", 1),
 (2299, "I AM"): ("LABEL_OP", "Γ(∞) = 1 = I AM", 1),
 (520, "I AM"): ("OWN", "AIM is I AM by the same letters", 23),
 (506, "AIM"): ("LABEL_OP", "Atbash shortest-word chain lands on 23, named AIM", None),
 (520, "AIM"): (["LABEL_OP", "OWN", "LABEL_OP"], "chain lands on 23 AIM; AIM = I AM by letters; closes on TWO <-> AIM", None),
 (523, "AIM"): ("OTHER", "listing of cell 23's words in AIM's own subsection", None),
 (526, "AIM"): ("LABEL_OP", "58^2 ≡ 23 named AIM", None),
 (535, "AIM"): ("OPERAND", "69 = g × AIM", None),
 (546, "AIM"): (["PROPERTY", "OTHER"], "ZRN's cell named AIM's φ part; word-level Atbash mirror", None),
 (547, "AIM"): (["OTHER", "PROPERTY"], "×Q image of the point; AIM's φ part", None),
 (554, "AIM"): ("OPERAND", "79 ≡ 104 × 23, '... times AIM'", None),
 (569, "AIM"): ("LABEL_OP", "Γ(56) = 23 reflects SCRIBE onto AIM", None),
 (595, "AIM"): ("OTHER", "ring co-membership", None),
 (618, "AIM"): ("OWN", "fibre over AIM's own value", None),
 (622, "AIM"): ("OWN", "AIM's own store point", None),
 (547, "ZRN"): (["OTHER", "OWN"], "×Q image; ZRN's cell", None),
 (554, "ZRN"): ("PROPERTY", "104 named ZRN's φ part", None),
 (569, "ZRN"): ("PROPERTY", "63 × 71 ≡ 104 named ZRN's φ part", None),
 (578, "ZRN"): ("PROPERTY", "63 × 71 ≡ 104 named ZRN's φ part", None),
 (1448, "ZRN"): ("PROPERTY", "a word ×4 = 104 named ZRN's φ part", None),
 (545, "ASHER"): ("OWN", "ASHER's own norm", None),
 (556, "ASHER"): ("PROPERTY", "173 named ASHER's φ part", None),
 (579, "TOTH"): ("PROPERTY", "142 = 2 × 71 named TOTH's φ part", None),
 (585, "TOTH"): ("OWN", "TOTH's own cell", None),
 (1412, "TOTH"): ("LABEL_COLOC", "ANTIS = 63, the cell of TOTH", None),
 (569, "THOTH"): (["OWN", "OPERAND"], "THOTH's own cell; 'THOTH times Q'", None),
 (569, "TARGET"): ("LABEL_COLOC", "THOTH (71) shares the cell of TARGET", None),
 (574, "TARGET"): ("LABEL_COLOC", "THOTH = 71, the cell of ... TARGET", None),
 (569, "TRISMEGISTUS"): (["OWN", "OPERAND"], "own sum as THOTH×Q; inverse relation with SCRIBE", None),
 (1376, "TRISMEGISTUS"): ("OPERAND", "93 = HERMES × TRISMEGISTUS", None),
 (1380, "TRISMEGISTUS"): ("LABEL_OP", "Atbash mirror of BOUSTROPHEDON = 179 named TRISMEGISTUS", None),
 (569, "SCRIBE"): ("OPERAND", "inverse of 179; input of Γ", None),
 (569, "ROTATION"): ("LABEL_OP", "four cells sum to 369 ≡ 112, the cell of ROTATION", None),
 (1376, "HERMES"): ("OPERAND", "93 = HERMES × TRISMEGISTUS", None),
 (1417, "HERMES"): ("LABEL_COLOC", "stem ATLANT- = 68, the cell of HERMES", None),
 (1442, "HERMES"): ("LABEL_OP", "letter count 839 ≡ 68, the cell of HERMES", None),
 (1375, "SUPERIUS"): ("OPERAND", "SUPERIUS + INFERIUS = 229", None),
 (1375, "INFERIUS"): ("OPERAND", "SUPERIUS + INFERIUS = 229", None),
 (1390, "SUPERIUS"): ("OWN", "SUPERIUS at 128", None),
 (1390, "INFERIUS"): ("OWN", "its own sum as fold of 156", None),
 (1378, "INFERIUS"): ("LABEL_COLOC", "VENTUS 101 with INFERIUS", None),
 (1378, "KHUNRATH"): ("LABEL_COLOC", "VENTUS 101 with ... KHUNRATH", None),
 (1380, "RONGO"): ("OPERAND", "149 = RONGO⁻¹", None),
 (1393, "RONGORONGO"): ("OPERAND", "product of EMERALD TABLET and RONGORONGO", None),
 (1379, "QUARTER TURN"): ("LABEL_COLOC", "OPERATIO SOLIS = 173, the cell of QUARTER TURN", None),
 (1395, "QUARTER TURN"): ("LABEL_COLOC", "three phrases share 173, the cell of QUARTER TURN", None),
 (1379, "TABULA SMARAGDINA"): ("OWN", "TABULA SMARAGDINA = 144", None),
 (1396, "TABULA SMARAGDINA"): ("LABEL_COLOC", "a phrase ≡ 144, with TABULA SMARAGDINA", None),
 (1396, "HERMES TRISMEGISTUS"): (["LABEL_COLOC", "OTHER"], "a German phrase = 247, the cell of H.T.; component of a longer phrase", None),
 (1396, "SUM"): ("OTHER", "component of a longer phrase", None),
 (1400, "SUM"): ("OTHER", "component of a longer phrase", None),
 (1405, "SUM"): ("LABEL_OP", "year 1595 ≡ 53 with SUM", None),
 (1405, "SONNE"): ("LABEL_OP", "year 1609 ≡ 67 with SONNE", None),
 (1400, "PIMANDER"): (["LABEL_COLOC", "OTHER"], "EGO SUM = 80 with PIMANDER; component of a longer phrase", None),
 (1400, "RAPA NUI"): ("LABEL_COLOC", "EGO SUM = 80 with ... RAPA NUI", None),
 (1400, "ATLANTIC"): ("LABEL_COLOC", "EGO SUM = 80 with ... ATLANTIC", None),
 (1399, "TELESMI"): ("LABEL_COLOC", "DESCENDIT (83) with TELESMI", None),
 (1416, "TELESMI"): ("LABEL_OP", "inverse of ATLANTIS, 83, the cell of TELESMI", None),
 (1416, "SAIS"): ("LABEL_OP", "half of ATLANTIS, 48, that of SAIS", None),
 (1414, "PYRAMIDUM"): ("LABEL_OP", "Atbash mirror of ATLANTIS is 120, the cell of PYRAMIDUM", None),
 (1414, "ATLANTIS"): ("OPERAND", "input of the Atbash mirror", None),
 (1416, "ATLANTIS"): ("OWN", "ATLANTIS's own readings", None),
 (1415, "CONFLAGRATION"): ("LABEL_OP", "fold of PYRANTIS, 135, the letter sum of CONFLAGRATION", None),
 (2153, "CONFLAGRATION"): ("LABEL_OP", "257 − 122 = 135 = CONFLAGRATION", None),
 (1415, "HENRIC KHUNRATH"): ("LABEL_OP", "inverse 158 is HENRIC KHUNRATH", None),
 (560, "BOUNDARY"): ("LABEL_COLOC", "HALF TURN = 100, the cell of BOUNDARY", None),
 (567, "WHO"): (["OTHER", "LABEL_OP"], "'with WHO at 46'; chain step 46 WHO", None),
 (1374, "SO BELOW"): ("OWN", "phrase split into its own parts' sums", None),
 (1397, "SOL"): ("OWN", "SOL is 46", None),
 (1404, "NEPTUNE"): ("OPERAND", "sum of four names", None),
 (1404, "JUNO"): ("OPERAND", "sum of four names", None),
 (1404, "VULCAN"): ("OPERAND", "sum of four names", None),
 (1413, "PYRANTIS"): (["OPERAND", "OWN"], "ATLANTIS = 5 × PYRANTIS; own ring", None),
 (2340, "PYRANTIS"): ("OPERAND", "ATLANTIS = 5 × PYRANTIS", None),
 (2153, "PYRANTIS"): ("OWN", "PYRANTIS 122", None),
}


def auto(t, m, cells):
    pre, post = t[:m.start()], t[m.end():]
    clause = re.split(r"[;·|]", pre)[-1]
    if CELLOF.search(clause):
        return "LABEL_COLOC?"
    if any(re.search(r"(?<![\d.])" + str(c) + r"\s*(?:\(|→)?\s*$", pre) for c in cells) and not re.search(r",\s*$", pre):
        return "NUM_LABEL?"
    if re.match(r"['’]s\s+\S", post):
        return "PROPERTY?"
    if re.match(r"\s*(?:=|≡|\(|\d)", post):
        return "OWN"
    return "OTHER"


def snippet(text, start, end, maxw=12):
    wb, wa, mid = text[:start].split(), text[end:].split(), text[start:end].split()
    room = max(0, maxw - len(mid)); nb = min(len(wb), room // 2); na = min(len(wa), room - nb)
    nb = min(len(wb), room - na)
    return " ".join((wb[len(wb) - nb:] + mid + wa[:na])[:maxw])


rows = []
unresolved = []
for s in S:
    t = s["text"]
    seen = Counter()
    for m in pat.finditer(t):
        w = m.group(1)
        if w not in targets:
            continue
        k = seen[w]; seen[w] += 1
        a = auto(t, m, targets[w])
        key = (s["i"], w)
        cell = None
        if key in M:
            cls, why, cell = M[key]
            if isinstance(cls, list):
                cls = cls[k] if k < len(cls) else cls[-1]
            src = "manual"
        else:
            cls, why, src = a, "rule", "rule"
            if cls.endswith("?"):
                unresolved.append((s["i"], w, a, snippet(t, m.start(), m.end())))
        if w == "I AM" and cell is None:
            cell = 23 if re.search(r"23", t[max(0, m.start() - 30):m.end() + 30]) else None
        rows.append({"sentence": s["i"], "tag": s["tag"], "word": w, "occ": k, "auto": a, "class": cls,
                     "source": src, "reason": why, "i_am_cell": cell,
                     "snippet": snippet(t, m.start(), m.end())})

per = defaultdict(lambda: defaultdict(set))
for r in rows:
    w = r["word"]
    per[w]["mention"].add(r["sentence"])
    per[w][r["class"]].add(r["sentence"])
    if r["class"] in ("LABEL_OP", "LABEL_COLOC"):
        per[w]["label"].add(r["sentence"])
        if w == "I AM":
            per[w][f"label_at_{r['i_am_cell']}"].add(r["sentence"])

res = {}
for w in sorted(targets, key=lambda w: (targets[w][0], w)):
    p = per.get(w, {})
    res[w] = {"cells": targets[w], "added_in": step_of.get(w, "pre-existing (in pre-terminus)"),
              "sentences_mentioning": len(p.get("mention", ())),
              "label_sentences": len(p.get("label", ())),
              "label_op_sentences": len(p.get("LABEL_OP", ())),
              "label_coloc_sentences": len(p.get("LABEL_COLOC", ())),
              "operand_sentences": len(p.get("OPERAND", ())),
              "property_sentences": len(p.get("PROPERTY", ())),
              "own_sentences": len(p.get("OWN", ())),
              "other_sentences": len(p.get("OTHER", ()))}
    if w == "I AM":
        res[w]["label_sentences_at_1"] = len(p.get("label_at_1", ()))
        res[w]["label_sentences_at_23"] = len(p.get("label_at_23", ()))

add_only = [w for w in added]
lab_sents = set().union(*[per[w]["label"] for w in add_only if w in per and "label" in per[w]])
# I AM labels at 1 are the pre-existing placement: exclude them from window totals
lab_sents_window = set()
pairs_window = 0
for w in add_only:
    if w not in per:
        continue
    if w == "I AM":
        ss = per[w].get("label_at_23", set())
    else:
        ss = per[w].get("label", set())
    lab_sents_window |= ss
    pairs_window += len(ss)
tot = {
    "sentences_total": len(S),
    "added_words_total": len(added),
    "added_words_mentioned_uppercase": sum(1 for w in add_only if res[w]["sentences_mentioning"] > 0),
    "added_words_with_label_use_window": sum(1 for w in add_only if (res[w].get("label_sentences_at_23", res[w]["label_sentences"]) if w == "I AM" else res[w]["label_sentences"]) > 0),
    "label_word_sentence_pairs_window": pairs_window,
    "distinct_sentences_with_label_use_window": len(lab_sents_window),
    "distinct_sentences_mentioning_any_added": len(set().union(*[per[w]["mention"] for w in add_only if w in per])),
    "occurrence_classes_added_words": dict(Counter(r["class"] for r in rows if r["word"] in added)),
    "unresolved_rule_flags": len(unresolved),
}
listed = ["PYRAMIDUM", "ATLANTIS", "TOTH", "THOTH", "SCRIBE", "TRISMEGISTUS", "AIM", "I AM", "ROTATION",
          "QUARTER TURN", "BOUNDARY", "TERMINUS", "HERMES TRISMEGISTUS", "RONGORONGO"]
json.dump({"per_word": res, "totals": tot, "listed": {w: res[w] for w in listed},
           "unresolved": unresolved}, open(os.path.join(HERE, "review_usage_final.json"), "w"),
          ensure_ascii=False, indent=1)
with open(os.path.join(HERE, "review_usage_final.tsv"), "w") as f:
    f.write("sentence\ttag\tword\tocc\tauto\tclass\tsource\treason\ti_am_cell\tsnippet(<=12 words)\n")
    for r in rows:
        f.write("\t".join(str(r[k]) for k in ("sentence", "tag", "word", "occ", "auto", "class", "source",
                                               "reason", "i_am_cell", "snippet")) + "\n")
print(json.dumps(tot, ensure_ascii=False, indent=1))
print("unresolved:", unresolved)
print("\nlisted words:")
for w in listed:
    print(f"  {w:20s}", res[w])
print("\nall added words with label use:")
for w in add_only:
    if res[w]["label_sentences"]:
        print(f"  {w:22s} cells={added[w]} label={res[w]['label_sentences']} (op {res[w]['label_op_sentences']}, coloc {res[w]['label_coloc_sentences']})")
