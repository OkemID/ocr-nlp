# Installation & Run

## Prerequisites
- Docker Desktop (or Docker Engine + docker compose v2)
- Node.js 20.x + npm
- (Optional for local dev) Python 3.10 if running OCR locally outside Docker
- Android/iOS tooling for React Native if building on device

## 1) One‑shot with Docker
```bash
docker compose up --build
# node-api → http://localhost:4000/health
# ocr-nlp  → http://localhost:8000/health
```

## 2) Run services locally (without Docker)

### OCR/NLP (Python FastAPI)
```bash
cd services/ocr-nlp
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install --upgrade pip
pip install -r requirements.txt  # or: pip install -e .
uvicorn src.main:app --reload --port 8000
```

### Node API
```bash
cd services/node-api
npm i
npm run dev
```

### Mobile (Expo)
```bash
cd apps/mobile
npm i
# set your Node API base (LAN IP for device) in .env:
echo "EXPO_PUBLIC_NODE_API_BASE=http://<your-host-ip>:4000" > .env
npm run start
```

## 3) Health & Smoke Tests
```bash
# health
curl -s http://localhost:4000/health
curl -s http://localhost:8000/health

# OCR test (direct and via gateway)
curl -s -F "file=@/path/to/sample.jpg" http://localhost:8000/ocr/extract | jq .
curl -s -F "file=@/path/to/sample.jpg" http://localhost:4000/ocr/extract | jq .
```

## Notes
- EasyOCR is CPU by default; GPU requires different base image & torch build.
- PDF support relies on `poppler-utils` (already packaged in Dockerfile).
