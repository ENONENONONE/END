import re
exec(open('verify.py').read().split("res = {}")[0])
rt = re.sub(r'\s+',' ',html_text(RAW_HTML))
fo=[274, 296, 308, 311, 424, 458, 471, 557, 558, 586, 597, 604, 635, 652, 666, 674, 693, 698, 711, 714, 755, 777, 792, 800, 801, 810, 834, 870, 920, 930, 974]
for x in fo:
    ms=list(re.finditer(r'(?<![0-9A-Za-z])%d(?![0-9A-Za-z])'%x,rt))
    src='rev'
    if not ms:
        src='key'; ms=list(re.finditer(r'(?<![0-9A-Za-z])%d(?![0-9A-Za-z])'%x,KEY))
        print(x,src,len(ms),'(key context not printed)')
        continue
    m=ms[0]; print(x,src,len(ms),repr(rt[max(0,m.start()-45):m.end()+25]))
