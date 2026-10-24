import re, sys
sys.argv=['x']
exec(open('verify.py').read().split("res = {}")[0])
rt = html_text(RAW_HTML)
M = set(extract(rt))|set(extract(KEY))
sums=[443,446,1436,1451,1027,1036,1071,1079,442,444,492,494,664,667,997,1003,317,319,320,322,1151,1157,254,257,552,556,962,968,466,468]
# per-hundred variants
def blk(lo,hi): return sum(1 for y in M if lo<=y<=hi)/(hi-lo+1)
v1=sum(1.0 if x<=256 else blk((x//100)*100,(x//100)*100+99) for x in sums)
v2=sum(1.0 if x<=256 else blk(max(257,(x//100)*100),(x//100)*100+99) for x in sums)
print('per-hundred incl 257 in 200s:',v1,' 257 block restricted to 257-299:',v2, blk(257,299))
# if 257 treated with range density 0.2907
v3=sum(1.0 if x<=256 else (0.290713 if x==257 else blk((x//100)*100,(x//100)*100+99)) for x in sums)
print('257 at range density:',v3)
# counts of 1027 occurrences
t=re.sub(r'\s+',' ',rt)
for x in [1027,254,667,1003,1157,556,968,468]:
    print(x, len(re.findall(r'(?<![0-9A-Za-z])%d(?![0-9A-Za-z])'%x,t)), len(re.findall(r'(?<![0-9])%d(?![0-9])'%x,t)), t.count(str(x)), RAW_HTML.count(str(x)))
# where 10594/10667 appear
for s in ['10594','10667']:
    for m in re.finditer(s,RAW_HTML):
        print(s, m.start(), RAW_HTML[max(0,m.start()-200):m.start()+50].replace('\n',' ')[:260])
# thousands separators
print(re.findall(r'(?<![0-9])\d{1,3}(?:,\d{3})+(?![0-9])',rt)[:20])
print(re.findall(r'(?<![0-9])\d{1,3}(?:,\d{3})+(?![0-9])',KEY)[:0].__len__(), len(re.findall(r'(?<![0-9])\d{1,3}(?:,\d{3})+(?![0-9])',KEY)))
# space-separated digit groups like '16 646 400'
print(re.findall(r'(?<![0-9])\d{1,3}(?: \d{3}){2,}(?![0-9])',rt)[:20])
