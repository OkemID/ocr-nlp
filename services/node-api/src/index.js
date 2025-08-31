import express from "express";
import cors from "cors";
import morgan from "morgan";
import multer from "multer";
import axios from "axios";
import dotenv from "dotenv";
import FormData from "form-data";

dotenv.config();

const app = express();
app.use(cors());
app.use(morgan("dev"));
app.get("/health", (_, res) => res.json({ ok: true, service: "node-api" }));

const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 20 * 1024 * 1024 } });

const OCR_NLP_BASE = process.env.OCR_NLP_BASE || "http://ocr-nlp:8000";

app.post("/ocr/extract", upload.single("file"), async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: "file required" });

    // forward to FastAPI
    const form = new FormData();
    form.append("file", req.file.buffer, { filename: req.file.originalname, contentType: req.file.mimetype });

    const r = await axios.post(`${OCR_NLP_BASE}/ocr/extract`, form, {
      headers: form.getHeaders(),
      maxBodyLength: Infinity
    });

    res.status(r.status).json(r.data);
  } catch (e) {
    const status = e.response?.status || 500;
    res.status(status).json({ error: e.message, detail: e.response?.data });
  }
});

const port = process.env.PORT || 4000;
app.listen(port, () => console.log(`node-api listening on :${port}`));
