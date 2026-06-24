# EVOSGPT — Part of the EVOS Business Hub

An evolving AI assistant that remembers each user, built with FastAPI + React + Supabase + OpenAI.

## 📁 Structure

```
evosgpt/
├── backend/          ← FastAPI API
│   ├── main.py
│   ├── requirements.txt
│   ├── schema.sql    ← run this in EVOSDATA Supabase SQL Editor
│   ├── render.yaml
│   └── .env.example
└── frontend/         ← React (Vite)
    ├── src/
    │   ├── pages/    ← Home, Login, Register, Chat, Dashboard, Upgrade
    │   ├── api/      ← API client
    │   ├── App.jsx
    │   └── main.jsx
    ├── package.json
    ├── netlify.toml
    └── .env.example
```

## 🗄️ Step 1 — Database Setup

This project **shares the same `users` table as EvosData** — one login for the whole EVOS ecosystem.

1. Go to your **EVOSDATA Supabase project → SQL Editor**
2. Open `backend/schema.sql`
3. Run it — this adds an `evosgpt_tier` column to your existing `users` table and creates:
   - `evosgpt_memory` — short-term chat memory
   - `evosgpt_long_memory` — AI-generated evolving summary per user
   - `evosgpt_daily_chats` — daily chat counter (for Basic tier limits)
   - `evosgpt_purchases` — Paystack purchase records
   - `evosgpt_coupons` — coupon codes

## 🔧 Step 2 — Backend Setup (FastAPI)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:
```
SUPABASE_URL=https://your-evosdata-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_KEY=your-service-role-key
OPENAI_API_KEY=your-openai-key
PAYSTACK_SECRET_KEY=your-paystack-secret
```

Run locally:
```bash
uvicorn main:app --reload
```

### Deploy to Render
1. Push `backend/` to a GitHub repo
2. Create a new **Web Service** on Render, connect the repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add the env vars above in Render's dashboard
6. Deploy

Your API will be live at `https://your-service.onrender.com`

## 🎨 Step 3 — Frontend Setup (React)

```bash
cd frontend
npm install
cp .env.example .env
```

Fill in `.env`:
```
VITE_API_URL=https://your-evosgpt-api.onrender.com
```

Run locally:
```bash
npm run dev
```

### Deploy to Netlify
1. Push `frontend/` to a GitHub repo
2. Connect repo to Netlify
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Add env var: `VITE_API_URL`
6. Deploy

## 🔗 Step 4 — Paystack Webhook

In your Paystack dashboard, add this webhook URL:
```
https://your-evosgpt-api.onrender.com/webhook/paystack
```

## 🎯 Tiers

| Tier | Price | Model | Daily Limit | Memory |
|------|-------|-------|--------------|--------|
| Basic | Free | gpt-4o-mini | 10 chats/day | 20 messages |
| Pro | GH₵75/mo | gpt-4o | Unlimited | 100 messages |
| Core | GH₵135/mo | gpt-4o | Unlimited | 300 messages |
| Founder (hidden) | — | gpt-4o | Unlimited | 1000 messages |

To manually upgrade a user to Founder, run in Supabase:
```sql
UPDATE users SET evosgpt_tier = 'Founder' WHERE username = 'your_username';
```

## 🧠 How the Evolving Memory Works

1. **Short-term memory** — last N messages (per tier limit) stored in `evosgpt_memory`, fed into every AI call for context
2. **Long-term memory** — every 10 messages, the AI summarizes the conversation and merges it into `evosgpt_long_memory.summary`. This summary is injected into the system prompt on every chat, so EVOSGPT "remembers" the user across sessions even after short-term memory is trimmed.

## 📋 Smart Output Formatting

The system prompt instructs the AI to always format:
- Code → fenced code blocks with language tags (rendered with a "Copy" button in the UI)
- Letters → clean, copy-paste-ready structure
- Lists/tables → proper markdown

## 💬 Upgrade Nudges

Basic tier users get a friendly upgrade nudge popup after their 5th and 8th chat of the day, and a clear limit-reached message after their 10th — both also mention EvosData for buying data bundles.

## 🎟️ Coupons

Seeded coupons (edit/remove in `schema.sql`):
- `EVOSPRO2026` → Pro
- `EVOSCORE2026` → Core
- `EVOSFOUND` → Founder

Redeem via the Upgrade page in-app.
