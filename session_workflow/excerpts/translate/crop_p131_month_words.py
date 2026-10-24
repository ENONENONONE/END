"""Crops used in the translate step (no random generators are used; no seed needed).

PDF page 131 (0-based index 130) shows two zodiac circles of the f72v fold-out:
left circle a lion (Leo, f72v3), right circle a seated woman (Virgo, f72v2).
This script extracts the page image and saves enlarged crops of the
Roman-alphabet word in the centre of each circle.
"""
import io
import os

from PIL import Image, ImageEnhance
from pypdf import PdfReader

PDF = "~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/Voynich_Manuscript.pdf"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "crops")
os.makedirs(OUT, exist_ok=True)

reader = PdfReader(PDF)
page = Image.open(io.BytesIO(list(reader.pages[130].images)[0].data)).convert("RGB")
print("page 131 size", page.size)  # (1536, 1025)
page.save(os.path.join(OUT, "p131_full.jpg"), quality=92)

BOXES = {
    "p131_leo_region": (250, 480, 470, 640),     # word under the lion: read 'augst'
    "p131_virgo_region": (820, 440, 1060, 600),  # word left of the woman: read '?ep??t' with overbar
}
for name, box in BOXES.items():
    c = page.crop(box)
    c = c.resize((c.width * 3, c.height * 3), Image.LANCZOS)
    c = ImageEnhance.Contrast(c).enhance(1.5)
    c.save(os.path.join(OUT, name + ".png"))
    print(name, box)
