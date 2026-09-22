# 💬 SalesFlow AI: Autonomous WhatsApp Sales & CRM Agent

SalesFlow AI is a **real-time, multi-step AI agent** that lives on a business's WhatsApp number. It receives customer messages, understands intent and mood, scores the lead, drafts and sends a grounded reply, schedules a follow-up, syncs everything to a CRM, and alerts the business owner — all within seconds, with zero manual intervention.

---

## 🧠 Project Architecture & Workflow

Every inbound WhatsApp message is acknowledged instantly, then processed through a five-step pipeline that runs quietly in the background:

![SalesFlow AI Workflow](https://raw.githubusercontent.com/Abdul-Hamidd/salesFlow_ai/main/salesflow_ai_workflow.png)

1. **Contact** — finds or creates the contact, syncs it to the CRM, reads message sentiment
2. **Lead** — scores the message (hot / warm / cold) and updates the CRM lead instead of duplicating it
3. **Response** — drafts a grounded, on-brand reply from the live product catalog and sends it back
4. **Follow-up** — schedules a time-delayed nudge, skipped automatically if one is already pending
5. **Notification** — alerts the business owner for hot/warm leads

A background scheduler independently checks for due follow-ups every minute and sends them the same way.

---

## 🚀 Key Technical Features

* **Instant-ack, background-processed webhook:** the WhatsApp webhook returns `200 OK` in milliseconds and hands the actual AI pipeline to a background task — this stops Meta's webhook retry mechanism from re-delivering (and duplicating) the same message.
* **Idempotent CRM sync:** every contact and lead is searched by phone number before writing, so repeated messages from the same customer update one CRM record instead of creating duplicates.
* **Single merged pipeline, not a microservice sprawl:** the five agent steps run as plain function calls inside one process rather than five separately-hosted services calling each other over HTTP — simpler to deploy, no inter-service network hops, no partial-failure risk.
* **Voice message support:** customer voice notes are downloaded from WhatsApp and transcribed through a hosted API — no local ML model to load, keeping the deployment lightweight.
* **Lead-aware follow-ups:** hot leads get a 2-hour nudge, warm leads 24 hours, cold leads 3 days — each with a distinct message.
* **Live owner dashboard:** a separate frontend shows contacts, leads, conversations and orders in real time, reading from the same database the agent writes to.

---

## ⚙️ Technologies & Core Stack

* **Frontend:** React (Vite), deployed on **Vercel**
* **Backend:** FastAPI, deployed on **FastAPI Cloud** (GitHub-connected, auto-deploys on push)
* **Messaging:** Meta WhatsApp Business Cloud API (permanent System User access token)
* **Database:** Supabase (Postgres) — contacts, leads, conversations, follow-ups, products, notifications
* **CRM:** Zoho CRM (Contacts + Leads modules, synced live)
* **LLM Inference & Voice:** Groq API
* **Scheduling:** APScheduler (in-process, 1-minute interval)

---

## 🧩 Model & Pipeline Specifics

### 🔹 1. Sentiment & Lead Scoring
`openai/gpt-oss-120b` (via Groq) analyzes each inbound message twice: once for sentiment (positive/neutral/negative/urgent) during the Contact step, and once for a 0–100 lead score (cold/warm/hot) during the Lead step.

### 🔹 2. Reply Generation
The same Groq model generates the customer-facing reply, grounded in the live product catalog pulled from Supabase, kept to 3–4 lines, and matched to the customer's own language.

### 🔹 3. Voice Transcription
`whisper-large-v3-turbo` (via Groq) transcribes voice notes.

> **Note:** This originally ran on local `openai-whisper` (PyTorch + CUDA dependencies). It was moved to Groq's hosted Whisper endpoint after the local model's memory footprint caused an out-of-memory crash on deployment.

### 🔹 4. Webhook Reliability
The webhook handler validates Meta's payload, immediately returns `200 OK`, then hands off to `core/pipeline.py` via FastAPI's `BackgroundTasks` — decoupling Meta's delivery guarantee from the pipeline's actual runtime.

---

## ⚙️ Installation & Workspace Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Abdul-Hamidd/salesFlow_ai.git
cd salesFlow_ai
```

### 2. Backend Setup
```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Environment Configuration
Create a `.env` file in the repo root (backend):

SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
WEBHOOK_VERIFY_TOKEN=your_own_secret_string
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_whatsapp_business_account_id
WHATSAPP_TOKEN=your_permanent_whatsapp_access_token
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
ZOHO_CLIENT_ID=your_zoho_client_id
ZOHO_CLIENT_SECRET=your_zoho_client_secret
ZOHO_ACCESS_TOKEN=your_zoho_access_token
ZOHO_REFRESH_TOKEN=your_zoho_refresh_token
ZOHO_API_DOMAIN=https://www.zohoapis.com


Get a free Groq API key from [console.groq.com](https://console.groq.com), Supabase credentials from your Supabase project dashboard, and WhatsApp/Zoho credentials from their respective developer consoles.

---

## ▶️ Operational Execution

**Run the backend:**
```bash
uvicorn main:app --reload
```

**Run the frontend:**
```bash
cd frontend
npm run dev
```

**Production:** the backend is deployed on FastAPI Cloud and the frontend on Vercel, both auto-deploying from this repository on every push to `main`.

---

## ⚠️ Repository Notes

The WhatsApp webhook only starts receiving real (non-test) traffic after the "customer-initiated conversation" step is completed once in Meta's App Dashboard — a manual, one-time setup requirement on Meta's side, not something the code controls.

---

## 🌟 Strategic Roadmap

* [ ] Guard the reply-generation prompt against inventing payment details or other unverified facts
* [ ] Move the follow-up scheduler off in-process APScheduler to survive cold starts on serverless-style hosting
* [ ] Multi-number / multi-business support
* [ ] Analytics dashboard for lead conversion trends over time

---

## 👨‍💻 Author

**ABDUL HAMID**
GenAI & AI/ML Engineer
linkedin.com/in/abdul-hamid786 | kaggle.com/hamidai | upwork.com/freelancers/~011475c781d6b91385

Give it a star ⭐ on GitHub if you find this project 
