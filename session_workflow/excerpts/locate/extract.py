# Extract every page image of the Voynich PDF to pages/pNNN.jpg (1-based numbering). No randomness used.
from pypdf import PdfReader
from PIL import Image
import io, os
PDF="~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/Voynich_Manuscript.pdf"
os.makedirs("pages",exist_ok=True)
r=PdfReader(PDF)
print("pages",len(r.pages))
for i,pg in enumerate(r.pages):
    imgs=list(pg.images)
    im=Image.open(io.BytesIO(imgs[0].data))
    fn=f"pages/p{i+1:03d}.jpg"
    if not os.path.exists(fn): im.convert("RGB").save(fn,quality=95)
    print(i+1,len(imgs),im.size,im.mode, pg.mediabox.width, pg.mediabox.height)
