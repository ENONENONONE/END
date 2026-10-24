# enhance.py PAGE x0 y0 x1 y1 SCALE NAME [channel]
# Local-contrast enhancement: channel (R,G,B or L) -> subtract heavy Gaussian blur (high-pass) -> equalize -> enlarge.
# Deterministic (no randomness).
import sys, numpy as np
from PIL import Image, ImageFilter, ImageOps
p,x0,y0,x1,y1=map(int,sys.argv[1:6]); s=float(sys.argv[6]); name=sys.argv[7]; ch=sys.argv[8] if len(sys.argv)>8 else "B"
im=Image.open(f"pages/p{p:03d}.jpg").crop((x0,y0,x1,y1))
g=im.convert("L") if ch=="L" else im.getchannel(ch)
a=np.asarray(g,dtype=float); bl=np.asarray(g.filter(ImageFilter.GaussianBlur(25)),dtype=float)
hp=a-bl; lo,hi=np.percentile(hp,[1,99.5]); hp=np.clip((hp-lo)/(hi-lo),0,1)*255
out=Image.fromarray(hp.astype("uint8")).filter(ImageFilter.GaussianBlur(0.6))
out=out.resize((int((x1-x0)*s),int((y1-y0)*s)),Image.LANCZOS)
fn=f"crops/{name}.png"; out.save(fn); print(fn,out.size)
