#!/usr/bin/env python3
"""(c) In the review's sentences, find uses of words added to the tablet in the
window pre-terminus -> current, and classify each occurrence.

Tokenisation: every current tablet word (uppercase phrase) is matched case-
sensitively, longest phrase first, with no uppercase letter on either side, and
matched spans are masked so that e.g. EVENT HORIZON is not counted as HORIZON
and QUARTER TURN is not counted as TURN.

Occurrence classes for an added word W at cell c:
  CELL_OF   the text just before W (same clause) ends in 'cell of', 'cells of',
            'that of', 'onto', 'lands on', 'landing on', 'lands at', 'shares the
            cell of', possibly with earlier list items 'X, ' / 'X and ' between.
            W names a number reached by another route.
  NUM_LABEL W is immediately preceded by its own cell number c (whitespace only,
            optionally with ( or '→ '), e.g. '173 QUARTER TURN': a computed
            number carrying W as its label.
  POSSESSIVE W's / W’s followed by a noun (φ part, cell, inverse...): a number
            named as a property of W.
  OWN       W followed by '=', '≡', '(', or a number: W's own letter reading.
  OTHER     none of the above (mentions, lists, bookkeeping).
A sentence counts as a 'label use' of W if it holds at least one CELL_OF or
NUM_LABEL occurrence of W; 'label_or_possessive' adds POSSESSIVE.
No randomness."""
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
added_step = {a["word"]: f"{st['from']}->{st['to']}" for st in D["steps"] for a in st["added"]}
# reference words named in the task list that were NOT added in the window
EXTRA = {"AIM": [23], "HERMES": [68]}

vocab = sorted({w for v in cur.values() for w in v["words"] if re.search(r"[A-Z]", w)},
               key=lambda w: (-len(w), w))
where = defaultdict(list)
for c, v in cur.items():
    for w in v["words"]:
        where[w].append(int(c))

targets = dict(added)
targets.update(EXTRA)

# one big alternation, longest first
pat = re.compile(r"(?<![A-Za-z])(" + "|".join(re.escape(w) for w in vocab) + r")(?![A-Za-z])")

CELLOF = re.compile(r"(?:cells? of|that of|onto|lands? on|landing on|lands? at|shares the cell of)\s+"
                    r"(?:(?:the )?[A-Z][A-Z0-9' -]*?(?:,\s+|\s+and\s+|\s+or\s+))*$")


def snippet(text, start, end, maxw=12):
    words_before = text[:start].split()
    words_after = text[end:].split()
    mid = text[start:end].split()
    room = max(0, maxw - len(mid))
    nb = min(len(words_before), room // 2)
    na = min(len(words_after), room - nb)
    if na < room - nb:
        nb = min(len(words_before), room - na)
    parts = words_before[len(words_before) - nb:] + mid + words_after[:na]
    return " ".join(parts[:maxw])


rows = []
per = defaultdict(lambda: {"sentences_mentioning": set(), "label": set(), "label_or_poss": set(),
                           "own": set(), "occ": Counter()})
for s in S:
    t = s["text"]
    for m in pat.finditer(t):
        w = m.group(1)
        if w not in targets:
            continue
        cells = targets[w]
        pre = t[:m.start()]
        post = t[m.end():]
        # clause before: since last ; · or | (keep commas for list handling)
        clause = re.split(r"[;·|]", pre)[-1]
        cls = "OTHER"
        if CELLOF.search(clause):
            cls = "CELL_OF"
        elif any(re.search(r"(?<![\d.])" + str(c) + r"\s*(?:\(|→)?\s*$", pre) for c in cells) \
                and not re.search(r",\s*$", pre):
            cls = "NUM_LABEL"
        elif re.match(r"['’]s\s+\S", post):
            cls = "POSSESSIVE"
        elif re.match(r"\s*(?:=|≡|\(|\d)", post):
            cls = "OWN"
        p = per[w]
        p["sentences_mentioning"].add(s["i"])
        p["occ"][cls] += 1
        if cls in ("CELL_OF", "NUM_LABEL"):
            p["label"].add(s["i"])
        if cls in ("CELL_OF", "NUM_LABEL", "POSSESSIVE"):
            p["label_or_poss"].add(s["i"])
        if cls == "OWN":
            p["own"].add(s["i"])
        rows.append({"word": w, "cells": cells, "sentence": s["i"], "tag": s["tag"],
                     "section": s["section"][:60], "class": cls,
                     "snippet": snippet(t, m.start(), m.end())})

out = {}
for w in sorted(targets, key=lambda w: (targets[w][0], w)):
    p = per.get(w)
    if p is None:
        out[w] = {"cells": targets[w], "step": added_step.get(w, "pre-existing"),
                  "sentences_mentioning": 0, "label_sentences": 0,
                  "label_or_possessive_sentences": 0, "own_sentences": 0, "occurrences": {}}
        continue
    out[w] = {"cells": targets[w], "step": added_step.get(w, "pre-existing"),
              "sentences_mentioning": len(p["sentences_mentioning"]),
              "label_sentences": len(p["label"]),
              "label_or_possessive_sentences": len(p["label_or_poss"]),
              "own_sentences": len(p["own"]),
              "occurrences": dict(p["occ"])}
tot = {"sentences_total": len(S),
       "added_words_mentioned": sum(1 for w in added if out[w]["sentences_mentioning"] > 0),
       "added_words_with_label_use": sum(1 for w in added if out[w]["label_sentences"] > 0),
       "label_sentence_word_pairs": sum(out[w]["label_sentences"] for w in added),
       "distinct_sentences_with_any_label_use": len(set().union(*[per[w]["label"] for w in added if w in per])),
       "distinct_sentences_mentioning_any_added": len(set().union(*[per[w]["sentences_mentioning"] for w in added if w in per])),
       "occurrence_classes_added": dict(sum((Counter(per[w]["occ"]) for w in added if w in per), Counter()))}
json.dump({"per_word": out, "totals": tot}, open(os.path.join(HERE, "review_usage.json"), "w"),
          ensure_ascii=False, indent=1)
with open(os.path.join(HERE, "review_usage_occurrences.tsv"), "w") as f:
    f.write("word\tcells\tsentence\ttag\tclass\tsnippet(<=12 words)\n")
    for r in rows:
        f.write(f"{r['word']}\t{r['cells']}\t{r['sentence']}\t{r['tag']}\t{r['class']}\t{r['snippet']}\n")
print(json.dumps(tot, ensure_ascii=False, indent=1))
for w, v in out.items():
    if v["sentences_mentioning"]:
        print(f"{w:28s} {str(v['cells']):9s} ment={v['sentences_mentioning']:3d} label={v['label_sentences']:3d} "
              f"lab+poss={v['label_or_possessive_sentences']:3d} own={v['own_sentences']:3d} {v['occurrences']}")
