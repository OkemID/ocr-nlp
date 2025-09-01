import io
import os
import logging
from typing import List, Tuple

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from pdf2image import convert_from_bytes
import easyocr
import numpy as np
import json

# ---------- Logging Setup ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------- Constants ----------
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "5"))
PDF_DPI = int(os.getenv("PDF_DPI", "220"))

# ---------- App & Reader ----------
app = FastAPI(title="OkemID OCR/NLP")
reader = easyocr.Reader(["en"], gpu=False)

# ---------- Type Aliases ----------
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
        bbox = [[float(x) for x in point] for point in item[0]]
        text = str(item[1])
        conf = float(item[2])
        out.append((bbox, text, conf))
    return out


@app.post("/ocr/extract")
async def ocr_extract(file: UploadFile = File(...)):
    logging.info(f"Incoming OCR request: filename={file.filename}, content_type={file.content_type}")

    try:
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")

        blocks = []

        def add_block(text, bbox=None, conf=None, page=None):
            blocks.append({
                "text": str(text),
                "bbox": bbox,
                "confidence": float(conf) if conf else None,
                "page": int(page) if page else None
            })

        # Detect if PDF
        content_type = file.content_type or ""
        if "pdf" in content_type or (file.filename and file.filename.lower().endswith(".pdf")):
            pages = convert_from_bytes(data, dpi=PDF_DPI, first_page=1, last_page=MAX_PDF_PAGES)
            for page_num, img in enumerate(pages, 1):
                for bbox, text, conf in _ocr_image(img):
                    add_block(text, bbox, conf, page_num)
        else:
            image = Image.open(io.BytesIO(data))
            for bbox, text, conf in _ocr_image(image):
                add_block(text, bbox, conf, 1)

        logging.info(f"OCR completed. Extracted {len(blocks)} blocks.")
        return {"blocks": blocks, "count": len(blocks)}

    except Exception as e:
        logging.error(f"OCR processing failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")
