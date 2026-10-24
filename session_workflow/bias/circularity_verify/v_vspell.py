"""Spelling fork: the 32 step-5 additions found verbatim in the plate text, read with U (as added) and with V for U (the plate's cut). Also J for I is not applied."""
import re
P = 257
K = {0, 1, 2, 3, 8, 15, 16, 17, 23, 44, 46, 62, 72, 73, 86, 92, 111, 117, 119, 120,
     128, 129, 136, 137, 138, 140, 142, 153, 225, 240, 241, 255, 256}
ls = lambda w: sum(ord(c) - 64 for c in w.upper() if 'A' <= c <= 'Z') % P
V = ("AMEN SOL LUNA SUM MATER PATER COELUM MAGNESIA ASCENDIT PIMANDER DESCENDIT TELESMI MUNDUS INFERIUS "
     "KHUNRATH VENTUS NUTRIX PYRAMIDUM MERCURIUS FORTITUDO SUPERIUS").split() + [
     "TRES PARTES", "RERUM NATURA", "COMPLETUM EST", "SUBTILE A SPISSO", "VERUM SINE MENDACIO",
     "SEPARABIS TERRAM AB IGNE", "FORTITUDO FORTIS", "MENS DIVINAE POTENTIAE", "DESIGNATIO PYRAMIDUM",
     "CERTUM ET VERISSIMUM", "SIC MUNDUS CREATUS EST"]
assert len(V) == 32
ku = [w for w in V if ls(w) in K]
kv = [w.replace("U", "V") for w in V if ls(w.replace("U", "V")) in K]
print("U spelling in K:", len(ku), ku)
print("V-for-U spelling in K:", len(kv), [(w, ls(w)) for w in kv])
ch = [(w, ls(w), w.replace('U','V'), ls(w.replace('U','V'))) for w in V if 'U' in w]
print("words with U:", len(ch))
for r in ch: print("  ", r)
