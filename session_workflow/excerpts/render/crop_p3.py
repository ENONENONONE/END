#!/usr/bin/env python3
"""Extract PDF page 3 (1-based) of Voynich_Manuscript.pdf, the f1r side, and write the crops viewed for the excerpt.
No random generator used."""
import io, os
from pypdf import PdfReader
from PIL import Image, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
PDF = '~/Documents/Φ≡c≡g≡∂ₜΦ≡Oc≡∂ₜΦ≡g≡c≡Φ/Voynich_Manuscript.pdf'
r = PdfReader(PDF)
for i in range(6):  # thumbnails of PDF pages 1-6 used to locate f1r
    im = Image.open(io.BytesIO(list(r.pages[i].images)[0].data)).convert('RGB')
    im.resize((im.size[0] // 3, im.size[1] // 3)).save(os.path.join(HERE, f'thumb_p{i+1}.jpg'))
im = Image.open(io.BytesIO(list(r.pages[2].images)[0].data)).convert('RGB')  # PDF page 3
im.save(os.path.join(HERE, 'pdf_p3_full.png'))
ImageEnhance.Contrast(im.crop((0, 100, 1116, 420))).enhance(1.8).save(os.path.join(HERE, 'p3_para1_overview.png'))
L = [(160, 222), (212, 262), (250, 300), (285, 335), (320, 370)]  # the five written lines of paragraph 1
for n, (y0, y1) in enumerate(L, 1):
    for h, (x0, x1) in enumerate([(100, 530), (500, 960)]):
        c = im.crop((x0, y0, x1, y1))
        c = ImageEnhance.Contrast(c.resize((c.size[0] * 3, c.size[1] * 3), Image.LANCZOS)).enhance(2.0)
        c.save(os.path.join(HERE, f'p3_L{n}_{"ab"[h]}.png'))
for name, box, sc, ct in [('p3_topright', (780, 20, 1060, 160), 3, 2.2), ('p3_bottom', (60, 1200, 1060, 1480), 1, 2.5),
                          ('p3_rightmargin', (860, 150, 1000, 380), 3, 2.2)]:
    c = im.crop(box)
    c = ImageEnhance.Contrast(c.resize((c.size[0] * sc, c.size[1] * sc), Image.LANCZOS)).enhance(ct)
    c.save(os.path.join(HERE, name + '.png'))
