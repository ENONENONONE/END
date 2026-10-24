import re, sys
exec(open('verify.py').read().split("res = {}")[0])
rt = re.sub(r'\s+',' ',html_text(RAW_HTML))
for m in re.finditer(r'(?<![0-9])\d{1,3}(?:,\d{3})+(?![0-9])',rt):
    print(repr(rt[max(0,m.start()-40):m.end()+20]))
