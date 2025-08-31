import io
import os
from typing import List, Tuple

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from pdf2image import convert_from_bytes

import easyocr
import numpy as np

MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "5"))
PDF_DPI = int(os.getenv("PDF_DPI", "220"))

app = FastAPI(title="OkemID OCR/NLP")

# Initialize EasyOCR once (CPU). Add langs as needed: ["en","fr","de"]
reader = easyocr.Reader(["en"], gpu=False)

BBox = List[List[float]]
OCRItem = Tuple[BBox, str, float]

@app.get("/health")
def health():
  return {"ok": True, "service": "ocr-nlp"}

def _ocr_image(pil_im: Image.Image) -> List[OCRItem]:
  if pil_im.mode != "RGB":
    pil_im = pil_im.convert("RGB")
  arr = np.asarray(pil_im)
  result = reader.readtext(arr, detail=1, paragraph=False)
  out: List[OCRItem] = []
  for item in result:
    bbox, text, conf = item[0], item[1], float(item[2])
    out.append((bbox, text, conf))
  return out

@app.post("/ocr/extract")
async def ocr_extract(file: UploadFile = File(...)):
  data = await file.read()
  if len(data) == 0:
    raise HTTPException(status_code=400, detail="empty file")

  content_type = file.content_type or ""
  blocks: List[dict] = []

  def add_block(text: str, bbox: BBox | None = None, conf: float | None = None, page: int | None = None):
    blocks.append({"text": text, "bbox": bbox, "confidence": conf, "page": page})

  try:
    if "pdf" in content_type or (file.filename and file.filename.lower().endswith(".pdf")):
      pages = convert_from_bytes(data, dpi=PDF_DPI, first_page=1, last_page=MAX_PDF_PAGES)
      for i, im in enumerate(pages, start=1):
        for (bbox, text, conf) in _ocr_image(im):
          add_block(text, bbox, conf, i)
    else:
      im = Image.open(io.BytesIO(data))
      for (bbox, text, conf) in _ocr_image(im):
        add_block(text, bbox, conf, 1)
  except Exception as e:
    raise HTTPException(status_code=422, detail=f"OCR failed: {e}")

  return JSONResponse({"blocks": blocks, "count": len(blocks)})
