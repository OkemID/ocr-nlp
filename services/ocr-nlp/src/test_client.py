import json
import time
import requests
from pathlib import Path

# Point to your test image relative to this file
img_path = Path(__file__).parent / "file-uploads" / "test.png"

if not img_path.exists():
    raise FileNotFoundError(f"Image not found: {img_path}")

url = "http://ocr-nlp:8000/ocr/extract"
  

# Retry loop to wait for ocr-nlp to be ready
for i in range(10):
    try:
        with img_path.open("rb") as f:
            resp = requests.post(url, files={"file": ("test.png", f, "image/png")})
        resp.raise_for_status()
        break  # success
    except requests.exceptions.ConnectionError as e:
        print(f"[Retry {i+1}/10] OCR service not ready. Waiting...")
        time.sleep(2)
else:
    raise RuntimeError("OCR service failed to start in time.")

with img_path.open("rb") as f:
    resp = requests.post(url, files={"file": ("test.png", f, "image/png")})

# Raise if server returned an error
resp.raise_for_status()

# Pretty print JSON
data = resp.json()
print(json.dumps(data, indent=2))

# Optional: print just the detected texts
print("\nDetected text:")
for b in data.get("blocks", []):
    print("-", b.get("text"))
