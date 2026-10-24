"""My manual label-use decisions for window words (and I AM / AIM / TERMINUS for reference).
Rule: LABEL = the word names a number that the sentence reaches by another route (operation, chain,
another string's letter sum, count, date, machine position). Unit ids are from v_mentions.json."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
U = json.load(open(os.path.join(HERE, "v_mentions.json")))["units"]
M = [  # (unit, word, class, reason)
 (554, "BOUNDARY", "COLOC", "HALF TURN = 100, the cell of BOUNDARY"),
 (561, "WHO", "OP", "Atbash chain from RITO lands on 46 WHO"),
 (563, "TARGET", "COLOC", "THOTH shares the cell of TARGET"),
 (563, "ROTATION", "OP", "four cells sum to 112, the cell of ROTATION"),
 (563, "TRISMEGISTUS", "OP*", "71 x 17 = 179 puts TRISMEGISTUS at THOTH times Q (investigator: OWN)"),
 (563, "SCRIBE", "OP?", "179 x 56 = 1 makes SCRIBE the inverse (investigator: OPERAND); borderline"),
 (568, "TARGET", "COLOC", "THOTH = 71, the cell of ... TARGET"),
 (1373, "INFERIUS", "COLOC", "VENTUS 101 with INFERIUS"),
 (1373, "KHUNRATH", "COLOC", "VENTUS 101 with KHUNRATH"),
 (1374, "QUARTER TURN", "COLOC", "OPERATIO SOLIS = 173, the cell of QUARTER TURN"),
 (1375, "TRISMEGISTUS", "OP", "Atbash mirror of BOUSTROPHEDON 179"),
 (1390, "QUARTER TURN", "COLOC", "three phrases share 173"),
 (1391, "HERMES TRISMEGISTUS", "COLOC", "German phrase = 247"),
 (1391, "TABULA SMARAGDINA", "COLOC", "VOCATUS SUM HERMES TRISMEGISTUS = 144"),
 (1394, "TELESMI", "COLOC", "DESCENDIT 83 with TELESMI"),
 (1395, "PIMANDER", "COLOC", "EGO SUM = 80 with"),
 (1395, "RAPA NUI", "COLOC", "EGO SUM = 80 with"),
 (1395, "ATLANTIC", "COLOC", "EGO SUM = 80 with"),
 (1400, "SUM", "OP", "year 1595 = 53"),
 (1400, "SONNE", "OP", "year 1609 = 67"),
 (1407, "TOTH", "COLOC", "ANTIS = 63, the cell of TOTH"),
 (1409, "PYRAMIDUM", "OP", "Atbash mirror of ATLANTIS is 120"),
 (1410, "CONFLAGRATION", "OP", "fold of PYRANTIS 135"),
 (1410, "HENRIC KHUNRATH", "OP", "inverse of PYRANTIS 158"),
 (1411, "TELESMI", "OP", "inverse of ATLANTIS 83"),
 (1411, "SAIS", "OP", "half of ATLANTIS 48"),
 (2148, "CONFLAGRATION", "OP", "257 - 122 = 135"),
]
with open(os.path.join(HERE, "v_labels.tsv"), "w") as f:
    f.write("unit\tword\tclass\treason\tsnippet<=12words\n")
    for u, w, c, r in M:
        t = U[u]; p = t.find(w); s = " ".join(t[max(0, p-60):p+len(w)+20].split()[-12:])
        f.write(f"{u}\t{w}\t{c}\t{r}\t{s}\n")
base = [m for m in M if m[2] in ("OP", "COLOC")]
print("investigator-consistent pairs", len(base), "words", len({m[1] for m in base}), "units", len({m[0] for m in base}))
cons = [m for m in M if m[2] in ("OP", "COLOC", "OP*")]
print("with TRISMEGISTUS@563 coded like AIM@563:", len(cons), "pairs", len({m[1] for m in cons}), "words", len({m[0] for m in cons}), "units")
allm = M
print("also SCRIBE@563:", len(allm), "pairs", len({m[1] for m in allm}), "words")
