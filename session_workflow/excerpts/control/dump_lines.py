# Compact one-string-per-line dump of controls.json (R3 forms with RECALLED glosses inline).
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glosses import GLOSS
d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "controls.json")))
K = {0,1,2,3,8,15,16,17,23,44,46,62,72,73,86,92,111,117,119,120,128,129,136,137,138,140,142,153,225,240,241,255,256}
out = []
for name, b in d["blocks"].items():
    for i, r in enumerate(b["rendered"], 1):
        def r3s(x):
            k, fs = x
            if k == "none": return "—"
            s = " / ".join(f"{f} '{GLOSS[f]}'" for f in fs)
            return s if k == "ksb" else "(" + s + ")"
        out.append(f"{name} L{i} [sum {r['line_sum']} ≡ {r['line_cell']}] EVA: {' '.join(r['words'])} || cells: {' '.join(str(c)+('*' if c in K else '') for c in r['cells'])} || R1: {' | '.join(r['R1'])} || R2: {' | '.join(r['R2'])} || R3: {' | '.join(r3s(x) for x in r['R3'])}")
open("rendered_lines.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out))
