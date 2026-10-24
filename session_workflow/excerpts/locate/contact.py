# Contact sheets of PDF pages (thumbnails with 1-based page numbers). Deterministic.
from PIL import Image, ImageDraw
import sys
a,b=int(sys.argv[1]),int(sys.argv[2]); cols=int(sys.argv[3]) if len(sys.argv)>3 else 6
tw,th=220,300
n=b-a+1; rows=(n+cols-1)//cols
sheet=Image.new("RGB",(cols*tw,rows*(th+20)),"white"); d=ImageDraw.Draw(sheet)
for j,p in enumerate(range(a,b+1)):
    im=Image.open(f"pages/p{p:03d}.jpg"); im.thumbnail((tw,th))
    x=(j%cols)*tw; y=(j//cols)*(th+20)
    sheet.paste(im,(x,y+20)); d.text((x+5,y+3),f"PDF {p}",fill="red")
sheet.save(f"contact_{a:03d}_{b:03d}.jpg",quality=85)
