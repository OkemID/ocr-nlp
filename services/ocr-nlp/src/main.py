import io
import os
import logging
from typing import List, Tuple

from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
from pdf2image import convert_from_bytes
import easyocr
import numpy as np

# ----------------- Logging Setup -----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ----------------- Constants & Config -----------------
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "5"))
PDF_DPI = int(os.getenv("PDF_DPI", "220"))
EASYOCR_MODEL_DIR = os.getenv("EASYOCR_MODEL_DIR", "/models")

# ----------------- App Setup -----------------
app = FastAPI(title="OkemID OCR/NLP")

# Initialize EasyOCR Reader with model directory
try:
    reader = easyocr.Reader(["en"], gpu=False, model_storage_directory=EASYOCR_MODEL_DIR)
except Exception as e:
    logging.error(f"Failed to initialize EasyOCR: {e}")
    raise RuntimeError("OCR service startup failed: could not load model.")

# ----------------- Type Aliases -----------------
BBox = List[List[float]]
OCRItem = Tuple[BBox, str, float]

# ----------------- Health Check -----------------
@app.get("/health")
def health():
    return {"ok": True, "service": "ocr-nlp"}

# ----------------- Internal OCR Handler -----------------
def _ocr_image(pil_img: Image.Image) -> List[OCRItem]:
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    np_img = np.asarray(pil_img)

    try:
        results = reader.readtext(np_img, detail=1, paragraph=True)
    except Exception as e:
        logging.error(f"EasyOCR failed on image: {e}")
        raise HTTPException(status_code=500, detail="OCR engine failed to process image.")

    ocr_results: List[OCRItem] = []

    for item in results:
        try:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                bbox = [[float(x) for x in point] for point in item[0]]
                text = str(item[1])
                conf = float(item[2]) if len(item) > 2 else None
                ocr_results.append((bbox, text, conf))
            else:
                logging.warning(f"Skipping unexpected OCR result item: {item}")
        except Exception as parse_err:
            logging.warning(f"Failed to parse OCR item {item}: {parse_err}")

    return ocr_results

# ----------------- OCR API Endpoint -----------------
@app.post("/ocr/extract")
async def ocr_extract(file: UploadFile = File(...)):
    logging.info(f"Incoming OCR request: filename={file.filename}, content_type={file.content_type}")

    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")

        blocks = []

        def add_block(text: str, bbox=None, conf=None, page=None):
            blocks.append({
                "text": text,
                "bbox": bbox,
                "confidence": float(conf) if conf is not None else None,
                "page": int(page) if page else None
            })

        is_pdf = (
            (file.content_type and "pdf" in file.content_type.lower())
            or (file.filename and file.filename.lower().endswith(".pdf"))
        )

        if is_pdf:
            images = convert_from_bytes(content, dpi=PDF_DPI, first_page=1, last_page=MAX_PDF_PAGES)
            for page_num, img in enumerate(images, start=1):
                for bbox, text, conf in _ocr_image(img):
                    add_block(text, bbox, conf, page_num)
        else:
            image = Image.open(io.BytesIO(content))
            for bbox, text, conf in _ocr_image(image):
                add_block(text, bbox, conf, page=1)

        logging.info(f"OCR completed. Extracted {len(blocks)} blocks.")
        return {"count": len(blocks), "blocks": blocks}

    except HTTPException:
        raise  # re-raise FastAPI exceptions as-is
    except Exception as e:
        logging.error(f"OCR processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")
