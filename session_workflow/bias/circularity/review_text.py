#!/usr/bin/env python3
"""Extract block-level text from the review HTML and split into sentences.
Block = p, li, h1-h4, pre, tr (cells joined by ' | '), td/th handled inside tr.
Sentence split: after . ; ! ? followed by whitespace and an uppercase/digit/symbol start.
Writes review_sentences.json (list of {i, section, block, text})."""
import json, os, re
from html.parser import HTMLParser

SRC = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/cascade_corpus_review.html"
OUT = os.path.dirname(os.path.abspath(__file__))

BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "pre", "tr", "figcaption", "caption", "dt", "dd", "blockquote"}
SKIP = {"style", "script", "nav"}


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []  # (section, tag, text)
        self.stack = []
        self.buf = None
        self.btag = None
        self.skip = 0
        self.section = ""
        self.in_h2 = False
        self.h2buf = ""

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        if tag == "h2":
            self.in_h2 = True
            self.h2buf = ""
        if tag in BLOCK and self.buf is None:
            self.buf = []
            self.btag = tag
        elif tag in ("td", "th") and self.buf is not None:
            self.buf.append(" | ")
        elif tag == "br" and self.buf is not None:
            self.buf.append(" ")

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip -= 1
            return
        if self.skip:
            return
        if tag == "h2":
            self.in_h2 = False
            self.section = re.sub(r"\s+", " ", self.h2buf).strip()
        if tag == self.btag and self.buf is not None:
            txt = re.sub(r"\s+", " ", "".join(self.buf)).strip(" |")
            if txt:
                self.blocks.append((self.section, tag, txt))
            self.buf = None
            self.btag = None

    def handle_data(self, data):
        if self.skip:
            return
        if self.in_h2:
            self.h2buf += data
        if self.buf is not None:
            self.buf.append(data)


p = P()
p.feed(open(SRC, encoding="utf-8").read())
SPLIT = re.compile(r"(?<=[.;!?])\s+(?=[A-Z0-9√Γ(ΦφΔχΠε∂ψ±−\-“\"'])")
sents = []
for bi, (sec, tag, txt) in enumerate(p.blocks):
    if tag == "tr":
        parts = [txt]  # a table row is one unit
    else:
        parts = [s.strip() for s in SPLIT.split(txt) if s.strip()]
    for s in parts:
        sents.append({"i": len(sents), "section": sec, "block": bi, "tag": tag, "text": s})
json.dump(sents, open(os.path.join(OUT, "review_sentences.json"), "w"), ensure_ascii=False, indent=0)
print("blocks", len(p.blocks), "sentences", len(sents))
from collections import Counter
print(Counter(s["tag"] for s in sents))
