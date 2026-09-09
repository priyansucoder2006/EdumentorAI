# Self-Hosted Judge0 Setup Guide for EduMentorAI

EduMentorAI uses a **self-hosted Judge0 instance** for multi-language code compilation and execution. 
**No Judge0 API key, RapidAPI account, or paid Judge0 cloud subscription is required.**

---

## 1. Prerequisites
- [Docker Engine & Docker Compose](https://docs.docker.com/get-docker/) installed on your machine.

---

## 2. Starting Judge0 Stack

To start the isolated Judge0 infrastructure (Server, Worker, Redis, PostgreSQL):

```bash
# From the project root directory
docker compose -f docker-compose.judge0.yml up -d
```

To view logs and ensure workers are ready:
```bash
docker compose -f docker-compose.judge0.yml logs -f
```

---

## 3. Verifying Judge0 is Running

### Health Check via HTTP:
```bash
# Check system info / reachability
curl http://localhost:2358/system_info

# Check available languages
curl http://localhost:2358/languages
```

### Verification via EduMentorAI Backend:
```bash
curl http://localhost:8000/api/code/health
```
Expected output:
```json
{
  "status": "online",
  "judge0_url": "http://localhost:2358",
  "languages_count": 60,
  "version": "1.13.1",
  "message": "Judge0 code execution engine is operational."
}
```

---

## 4. Starting EduMentorAI

### Step 1: Configure Environment
Ensure your `.env` contains:
```env
JUDGE0_API_URL="http://localhost:2358"
YOUTUBE_API_KEY="your_youtube_api_key_here"
GROQ_API_KEY="your_groq_api_key_here"
```

### Step 2: Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Step 3: Start Frontend
```bash
cd frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 5. Stopping the Judge0 Stack

When finished, stop the Judge0 containers:
```bash
docker compose -f docker-compose.judge0.yml down
```

---

## 6. Supported Languages & Security

- **Supported Languages**: Python, C, C++, Java, JavaScript (Node.js), TypeScript, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Bash, SQL, and any additional compilers enabled in your Judge0 deployment.
- **Security & Sandboxing**: User code is executed entirely in isolated Linux containers (isolate sandbox) managed by Judge0. EduMentorAI backend never calls `eval()`, `exec()`, or `subprocess` for arbitrary user code.
