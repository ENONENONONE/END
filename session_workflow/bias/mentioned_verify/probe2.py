import re, sys
exec(open('verify.py').read().split("res = {}")[0])
rt = html_text(RAW_HTML)
for sep,name in [(' ','thin'),(' ','nnbsp'),(' ','nbsp'),(',','comma'),(' ','space')]:
    pat=r'(?<![0-9])\d{1,3}(?:'+re.escape(sep)+r'\d{3})+(?![0-9])'
    print(name, len(re.findall(pat,rt)), len(re.findall(pat,KEY)))
# find the change log mention
i=RAW_HTML.index('the fifteen sentence sums in both spellings')
print(RAW_HTML[RAW_HTML.rfind('<',0,i-3000):i][:200].replace('\n',' '))
j=RAW_HTML.rfind('<li',0,i); k=RAW_HTML.rfind('<p',0,i); print('li at',j,'p at',k,'i',i)
print(RAW_HTML[max(j,k):max(j,k)+300].replace('\n',' '))
