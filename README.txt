END/solved — the pages for end.rito.one
Built by ../build.py. Ten files, static HTML, no scripts, no external requests, no fonts to fetch.
Dark throughout, on the START palette.

  index.html       the landing page: the finding, and the cards to the rest
  corpus.html      the Cascade Corpus Review — the parent document this is carried forward from
  conclusion.html  the whole argument, START to the Voynich
  reading.html     the procedure, stated so it can be followed or broken
  bereshit.html    Genesis 1:1 through the reading — what it reaches and what it does not
  figures.html     the 299 zodiac figures, by sign, the five starless and the four crowned
  sky.html         910 eclipses, what Prague saw, the Pleiades, the two dating tests
  field.html       GF(257): the generator, the fold, Γ, the ladder, precession through the rays
  evidence.html    everything measured, positive and negative at the same size

Every number is read from a file at build time. To change the pages, change the data and run:
  python3 build.py

Reads: ../../emerald_tablet.json · ../../cascade_corpus_review.html
       ~/Documents/artifacts/voynich_2026-09-19/{beinecke,eclipses,charts,stars,language}
Deploy: copy the contents of this folder to the end.rito.one document root. Nothing else is required.
