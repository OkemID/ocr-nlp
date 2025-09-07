FROM python:3.10-slim

# System dependencies for pdf2image and rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils libgl1 curl \
 && rm -rf /var/lib/apt/lists/*

# Create a volume directory for EasyOCR models
ENV EASYOCR_MODEL_DIR=/models
RUN mkdir -p $EASYOCR_MODEL_DIR && chmod -R 777 $EASYOCR_MODEL_DIR

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu .

# Pre-download EasyOCR models to avoid runtime crashes
RUN python - <<'EOF'
import os, time, easyocr

MODEL_DIR = os.getenv("EASYOCR_MODEL_DIR", "/models")

for attempt in range(5):
    try:
        easyocr.Reader(['en'], gpu=False, model_storage_directory=MODEL_DIR, verbose=False)
        print("✅ EasyOCR model downloaded to", MODEL_DIR)
        break
    except Exception as e:
        print(f"❌ Download attempt {attempt+1} failed: {e}")
        time.sleep(5)
else:
    raise SystemExit("❌ EasyOCR model download failed after multiple attempts.")
EOF

# Copy source code
COPY src ./src

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
