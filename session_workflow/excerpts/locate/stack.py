# stack.py OUT maxwidth crop1 crop2 ... : stack saved crops vertically (each scaled to <= maxwidth) with labels. Deterministic.
import sys
from PIL import Image, ImageDraw
out=sys.argv[1]; mw=int(sys.argv[2]); ims=[]
for f in sys.argv[3:]:
    im=Image.open(f).convert("RGB")
    if im.width>mw: im=im.resize((mw,int(im.height*mw/im.width)),Image.LANCZOS)
    ims.append((f.split('/')[-1],im))
H=sum(im.height+18 for _,im in ims); W=max(im.width for _,im in ims)
S=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(S); y=0
for n,im in ims:
    d.text((4,y+3),n,fill="red"); S.paste(im,(0,y+18)); y+=im.height+18
S.save(out); print(out,S.size)
