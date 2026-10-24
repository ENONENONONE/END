# Print '#' comment lines and inline <!...> comments for selected folios from ZL3b-n.txt. Deterministic.
import re,sys
F="<scratchpad>/vl/ZL3b-n.txt"
want=sys.argv[1:]
cur=None
for i,line in enumerate(open(F,encoding='ascii',errors='replace'),1):
    line=line.rstrip('\n')
    m=re.match(r'^<(f\w+)>',line)
    if m: cur=m.group(1)
    if cur not in want: continue
    if line.startswith('#') and line.strip('#').strip():
        print(f"{i}:{cur}:COMMENT {line}")
    elif m: print(f"{i}:{cur}:HEADER {line}")
    else:
        for c in re.findall(r'<![^>]*>',line):
            if not re.match(r'<!@\d+;>',c): print(f"{i}:{cur}:INLINE {c}  | {line[:60]}")
