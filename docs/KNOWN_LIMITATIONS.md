# KNOWN_LIMITATIONS.md — Architectural Boundaries & Roadmap

## 1. Current System Boundaries

1. **OCR Scanning**:
   - For image-only PDFs without embedded fonts, full OCR requires `tesseract-ocr` installed on the host OS or running inside the Docker container. When Tesseract is not present on host, text extraction falls back to direct character layer parsing.
2. **External Cloud Avatars (HeyGen / D-ID)**:
   - Live browser interactions utilize the real-time animated Canvas/SVG Teacher Avatar with synchronized lip-sync and phonemes to ensure zero-latency responses without per-minute cloud API charges. Cloud video job synthesis queues composite scene plans ready for rendering.
3. **Multilingual Speech Synthesis**:
   - In offline/browser mode, Web Speech API speech synthesis voice quality depends on the operating system's installed TTS voice packages (e.g. Windows Natural voices for Hindi/Bengali). EdgeTTS/OpenAI TTS can be activated via `.env` configuration.
