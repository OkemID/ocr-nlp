
// dotenv.config();

// const app = express();
// app.use(cors());
// app.use(morgan("dev"));
// app.use(express("dev"));
// app.get("/health", (_, res) => res.json({ ok: true, service: "node-api" }));


import express from "express";
import multer from "multer";
import axios from "axios";
import FormData from "form-data";
import { createReadStream, unlink } from "fs";


const app = express();
const upload = multer({ dest: 'uploads/' });

// Optional: CORS for local dev
// const cors = require('cors');
// app.use(cors({ origin: 'http://localhost:3000', credentials: true }));

// Health check
app.get('/api/health', (req, res) => res.json({ ok: true, service: 'node-bff' }));

// Proxy endpoint that the frontend calls
app.post('/ocr/extract', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'file is required' });
    }

    // (Optional) Validate MIME/type/size here

    // Build multipart form to send to Python
    const form = new FormData();
    form.append(
      'file',
      createReadStream(req.file.path),
      { filename: req.file.originalname, contentType: req.file.mimetype }
    );

    // Forward to FastAPI service
    const pyUrl = `${
      process.env.OCR_NLP_BASE || "http://ocr-nlp:8000"
    }/ocr/extract`;
    const pyResp = await axios.post(pyUrl, form, {
      headers: form.getHeaders(), // includes boundary
      maxBodyLength: Infinity,
      maxContentLength: Infinity,
      timeout: 60_000,            // adjust as needed
    });

    // Clean up temp file
    unlink(req.file.path, () => {});

    // Return OCR JSON to frontend
    res.status(pyResp.status).json(pyResp.data);
  } catch (err) {
    // Clean up temp file if exists
    if (req.file) unlink(req.file.path, () => {});
    const status = err.response?.status || 500;
    const detail = err.response?.data || { error: err.message };
    res.status(status).json({ message: 'OCR proxy failed', detail });
  }
});

// Start server
const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`Node BFF running on :${PORT}`));
