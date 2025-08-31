FROM python:3.10-slim

# System dependencies for pdf2image and rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils libgl1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (EasyOCR, FastAPI, etc.)
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu .

# Copy the app code
COPY src ./src

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
