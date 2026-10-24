# crop.py PAGE x0 y0 x1 y1 SCALE NAME [contrast] [gray]
# Crops a region of a PDF page image (pixel coords of the original extracted JPEG), enlarges with LANCZOS,
# optionally boosts contrast, saves to crops/NAME.png. Deterministic, no randomness.
import sys, os
from PIL import Image, ImageEnhance, ImageOps
p,x0,y0,x1,y1=map(int,sys.argv[1:6]); s=float(sys.argv[6]); name=sys.argv[7]
c=float(sys.argv[8]) if len(sys.argv)>8 else 1.6
gray=len(sys.argv)>9 and sys.argv[9]=="gray"
os.makedirs("crops",exist_ok=True)
im=Image.open(f"pages/p{p:03d}.jpg").crop((x0,y0,x1,y1))
if gray: im=ImageOps.autocontrast(im.convert("L"),cutoff=1)
im=im.resize((int((x1-x0)*s),int((y1-y0)*s)),Image.LANCZOS)
im=ImageEnhance.Contrast(im).enhance(c)
fn=f"crops/{name}.png"; im.save(fn); print(fn, im.size)
