from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from supabase import create_client, Client
from passlib.context import CryptContext
from datetime import datetime, timezone
import os
import uuid
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# =========================
# CORS
# =========================
ALLOWED_ORIGINS = [
    "https://evosgpt.xyz",
    "https://www.evosgpt.xyz",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ENV
# =========================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")

# =========================
# SUPABASE
# =========================
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# PASSWORD HASHING
# =========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# =========================
# TIER CONFIG
# =========================
TIER_MODELS = {
    "Basic": "gpt-4o-mini",
    "Core": "gpt-4o-mini",
    "Pro": "gpt-4o",
    "King": "gpt-4o",
    "Founder": "gpt-4o",
}

TIER_MEMORY_LIMIT = {
    "Basic": 20,
    "Core": 50,
    "Pro": 100,
    "King": 200,
    "Founder": 500,
}

TIER_PRICES_GHS = {
    "Core": 15,
    "Pro": 75,
    "King": 135,
}

VALID_UPGRADE_TIERS = set(TIER_PRICES_GHS.keys())

# =========================
# MODELS
# =========================
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    referred_by: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    user_id: str
    message: str

class UpgradeRequest(BaseModel):
    user_id: str
    tier: str
    email: str

class CouponRequest(BaseModel):
    user_id: str
    code: str

# =========================
# HELPERS
# =========================
def get_user_tier(user_id: int) -> str:
    res = supabase.table("evosgpt_users") \
        .select("tier") \
        .eq("id", user_id) \
        .limit(1) \
        .execute()
    if res.data:
        return res.data[0].get("tier", "Basic")
    return "Basic"


def get_short_memory(user_id: int, limit: int = 20) -> list:
    res = supabase.table("evosgpt_memory") \
        .select("role, content") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .limit(limit) \
        .execute()
    messages = res.data or []
    return list(reversed(messages))


def get_long_memory(user_id: int) -> Optional[str]:
    res = supabase.table("evosgpt_long_memory") \
        .select("summary") \
        .eq("user_id", user_id) \
        .limit(1) \
        .execute()
    if res.data:
        return res.data[0].get("summary")
    return None


def save_message(user_id: int, role: str, content: str):
    supabase.table("evosgpt_memory").insert({
        "user_id": user_id,
        "role": role,
        "content": content,
        "created_at": datetime.now(timezone.utc).isoformat()
    }).execute()


def trim_memory(user_id: int, tier: str):
    limit = TIER_MEMORY_LIMIT.get(tier, 20)
    res = supabase.table("evosgpt_memory") \
        .select("id") \
        .eq("user_id", user_id) \
        .order("created_at", desc=False) \
        .execute()
    rows = res.data or []
    if len(rows) > limit:
        excess = len(rows) - limit
        ids_to_delete = [r["id"] for r in rows[:excess]]
        for rid in ids_to_delete:
            supabase.table("evosgpt_memory") \
                .delete() \
                .eq("id", rid) \
                .execute()


def update_long_memory(user_id: int, tier: str, new_summary: str):
    existing = get_long_memory(user_id)
    if existing:
        # Merge old + new summary
        merge_prompt = f"""Merge these two summaries of the same user into one concise paragraph.
Old: {existing}
New: {new_summary}"""
        merged = call_openai("gpt-4o-mini", "You are a memory summarizer.", merge_prompt)
        summary = merged or new_summary
        supabase.table("evosgpt_long_memory") \
            .update({"summary": summary, "updated_at": datetime.now(timezone.utc).isoformat()}) \
            .eq("user_id", user_id) \
            .execute()
    else:
        supabase.table("evosgpt_long_memory").insert({
            "user_id": user_id,
            "summary": new_summary,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).execute()


def build_system_prompt(tier: str, long_memory: Optional[str]) -> str:
    base = {
        "Basic": "You are EVOSGPT, a helpful and friendly AI assistant. Keep answers clear and concise.",
        "Core": "You are EVOSGPT, a structured and helpful AI assistant. Use numbered lists and bullet points for clarity.",
        "Pro": "You are EVOSGPT, a confident and insightful AI assistant. Provide detailed, well-structured answers with examples.",
        "King": "You are EVOSGPT, a powerful and strategic AI. Provide expert-level answers with deep insights and pro tips.",
        "Founder": "You are EVOSGPT in Founder mode. You are witty, exclusive, and razor-sharp. Add personality to every response.",
    }
    prompt = base.get(tier, base["Basic"])
    if long_memory:
        prompt += f"\n\nUser context from past conversations:\n{long_memory}"
    return prompt


def call_openai(model: str, system: str, user_message: str, history: list = []) -> Optional[str]:
    try:
        messages = [{"role": "system", "content": system}]
        for h in history:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_message})

        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"model": model, "messages": messages},
            timeout=30
        )
        data = res.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("OPENAI ERROR:", str(e))
        return None


def summarize_recent_memory(user_id: int, history: list) -> Optional[str]:
    if not history:
        return None
    conversation = "\n".join([f"{h['role'].capitalize()}: {h['content']}" for h in history[-10:]])
    prompt = f"""Summarize this conversation in one concise paragraph. 
Focus on the user's goals, personality, and key topics discussed.

Conversation:
{conversation}"""
    return call_openai("gpt-4o-mini", "You are a memory summarizer.", prompt)


# =========================
# AUTH ROUTES
# =========================

@app.post("/auth/register")
def register(data: RegisterRequest):
    try:
        username = data.username.strip().lower()
        email = data.email.strip().lower()

        if len(username) < 3:
            raise HTTPException(400, "Username must be at least 3 characters")
        if len(data.password) < 6:
            raise HTTPException(400, "Password must be at least 6 characters")

        # Check username taken
        existing = supabase.table("evosgpt_users") \
            .select("id") \
            .eq("username", username) \
            .limit(1) \
            .execute()
        if existing.data:
            return {"status": "username_taken"}

        # Check email taken
        existing_email = supabase.table("evosgpt_users") \
            .select("id") \
            .eq("email", email) \
            .limit(1) \
            .execute()
        if existing_email.data:
            return {"status": "email_taken"}

        # Generate referral code
        referral_code = f"EVOS-{username[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"

        # Insert user
        insert = supabase.table("evosgpt_users").insert({
            "username": username,
            "email": email,
            "password": hash_password(data.password),
            "tier": "Basic",
            "referral_code": referral_code,
            "referred_by": data.referred_by or None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()

        if not insert.data:
            raise HTTPException(500, "Registration failed")

        user = insert.data[0]

        # Credit referrer if applicable
        if data.referred_by:
            supabase.table("evosgpt_users") \
                .update({"referral_count": supabase.table("evosgpt_users")
                    .select("referral_count")
                    .eq("referral_code", data.referred_by)
                    .limit(1).execute().data[0].get("referral_count", 0) + 1}) \
                .eq("referral_code", data.referred_by) \
                .execute()

        return {
            "status": "created",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "tier": user["tier"],
                "referral_code": user["referral_code"],
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print("REGISTER ERROR:", str(e))
        raise HTTPException(500, "Server error")


@app.post("/auth/login")
def login(data: LoginRequest):
    try:
        username = data.username.strip().lower()

        res = supabase.table("evosgpt_users") \
            .select("*") \
            .or_(f"username.eq.{username},email.eq.{username}") \
            .limit(1) \
            .execute()

        if not res.data:
            return {"status": "invalid_credentials"}

        user = res.data[0]

        if not verify_password(data.password, user["password"]):
            return {"status": "invalid_credentials"}

        return {
            "status": "ok",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "tier": user["tier"],
                "referral_code": user.get("referral_code", ""),
                "referred_by": user.get("referred_by", ""),
            }
        }

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        raise HTTPException(500, "Server error")


# =========================
# CHAT ROUTE
# =========================

@app.post("/chat")
def chat(data: ChatRequest):
    try:
        user_id = data.user_id
        message = data.message.strip()

        if not message:
            raise HTTPException(400, "Message cannot be empty")

        # Get tier
        tier = get_user_tier(user_id)
        model = TIER_MODELS.get(tier, "gpt-4o-mini")

        # Get memory
        short_memory = get_short_memory(user_id, limit=TIER_MEMORY_LIMIT.get(tier, 20))
        long_memory = get_long_memory(user_id)

        # Build system prompt
        system_prompt = build_system_prompt(tier, long_memory)

        # Call OpenAI
        reply = call_openai(model, system_prompt, message, short_memory)

        if not reply:
            raise HTTPException(500, "AI service unavailable")

        # Save messages
        save_message(user_id, "user", message)
        save_message(user_id, "assistant", reply)

        # Trim memory to tier limit
        trim_memory(user_id, tier)

        # Update long memory every 10 messages
        total_messages = len(short_memory) + 1
        if total_messages % 10 == 0:
            summary = summarize_recent_memory(user_id, short_memory)
            if summary:
                update_long_memory(user_id, tier, summary)

        return {
            "status": "ok",
            "reply": reply,
            "tier": tier,
            "model": model,
        }

    except HTTPException:
        raise
    except Exception as e:
        print("CHAT ERROR:", str(e))
        raise HTTPException(500, "Chat failed")


# =========================
# MEMORY ROUTES
# =========================

@app.get("/memory/{user_id}")
def get_memory(user_id: str):
    try:
        short = get_short_memory(user_id, limit=50)
        long = get_long_memory(user_id)
        return {
            "status": "ok",
            "short_memory": short,
            "long_memory": long,
        }
    except Exception as e:
        print("MEMORY ERROR:", str(e))
        raise HTTPException(500, "Failed to fetch memory")


@app.delete("/memory/{user_id}")
def clear_memory(user_id: str):
    try:
        supabase.table("evosgpt_memory") \
            .delete() \
            .eq("user_id", user_id) \
            .execute()
        return {"status": "ok", "message": "Memory cleared"}
    except Exception as e:
        print("CLEAR MEMORY ERROR:", str(e))
        raise HTTPException(500, "Failed to clear memory")


# =========================
# USER ROUTES
# =========================

@app.get("/user/{user_id}")
def get_user(user_id: str):
    try:
        res = supabase.table("evosgpt_users") \
            .select("id, username, email, tier, referral_code, referred_by, referral_count, created_at") \
            .eq("id", user_id) \
            .limit(1) \
            .execute()

        if not res.data:
            raise HTTPException(404, "User not found")

        user = res.data[0]

        # Get message count
        mem_res = supabase.table("evosgpt_memory") \
            .select("id", count="exact") \
            .eq("user_id", user_id) \
            .execute()

        return {
            "status": "ok",
            "user": {
                **user,
                "message_count": mem_res.count or 0,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print("GET USER ERROR:", str(e))
        raise HTTPException(500, "Failed to fetch user")


# =========================
# UPGRADE ROUTES
# =========================

@app.post("/upgrade/init")
def init_upgrade(data: UpgradeRequest):
    try:
        if data.tier not in VALID_UPGRADE_TIERS:
            raise HTTPException(400, "Invalid tier")

        amount_ghs = TIER_PRICES_GHS[data.tier]
        reference = f"EVOS-GPT-{data.user_id}-{uuid.uuid4().hex[:8].upper()}"

        paystack = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers={
                "Authorization": f"Bearer {PAYSTACK_SECRET}",
                "Content-Type": "application/json"
            },
            json={
                "email": data.email,
                "amount": int(amount_ghs * 100),
                "reference": reference,
                "callback_url": "https://evosgpt.xyz/upgrade/success",
                "metadata": {
                    "user_id": data.user_id,
                    "tier": data.tier,
                }
            },
            timeout=15
        ).json()

        if not paystack.get("status"):
            raise HTTPException(400, "Payment initialization failed")

        # Save pending purchase
        supabase.table("evosgpt_purchases").insert({
            "user_id": data.user_id,
            "tier": data.tier,
            "reference": reference,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()

        return {
            "status": "ok",
            "payment_url": paystack["data"]["authorization_url"],
            "reference": reference,
        }

    except HTTPException:
        raise
    except Exception as e:
        print("UPGRADE INIT ERROR:", str(e))
        raise HTTPException(500, "Upgrade initialization failed")


@app.post("/webhook/paystack")
async def paystack_webhook(request: Request):
    try:
        body = await request.body()
        signature = request.headers.get("x-paystack-signature", "")

        computed = hmac.new(
            PAYSTACK_SECRET.encode("utf-8"),
            body,
            hashlib.sha512
        ).hexdigest()

        if not hmac.compare_digest(computed, signature):
            return {"status": "invalid signature"}

        payload = await request.json()

        if payload.get("event") != "charge.success":
            return {"status": "ignored"}

        data = payload["data"]
        reference = data["reference"]
        meta = data.get("metadata", {})

        user_id = meta.get("user_id")
        tier = meta.get("tier")

        if not user_id or not tier:
            return {"status": "missing metadata"}

        # Check not already processed
        existing = supabase.table("evosgpt_purchases") \
            .select("id, status") \
            .eq("reference", reference) \
            .limit(1) \
            .execute()

        if existing.data and existing.data[0]["status"] == "paid":
            return {"status": "already processed"}

        # Upgrade user tier
        supabase.table("evosgpt_users") \
            .update({"tier": tier}) \
            .eq("id", user_id) \
            .execute()

        # Mark purchase paid
        supabase.table("evosgpt_purchases") \
            .update({"status": "paid"}) \
            .eq("reference", reference) \
            .execute()

        print(f"✅ User {user_id} upgraded to {tier}")
        return {"status": "success"}

    except Exception as e:
        print("PAYSTACK WEBHOOK ERROR:", str(e))
        return {"status": "error"}


# =========================
# COUPON ROUTE
# =========================

@app.post("/coupon/redeem")
def redeem_coupon(data: CouponRequest):
    try:
        code = data.code.strip().upper()

        res = supabase.table("evosgpt_coupons") \
            .select("*") \
            .eq("code", code) \
            .limit(1) \
            .execute()

        if not res.data:
            return {"status": "invalid", "message": "Invalid coupon code"}

        coupon = res.data[0]

        if coupon["used"]:
            return {"status": "used", "message": "Coupon already used"}

        # Apply tier
        supabase.table("evosgpt_users") \
            .update({"tier": coupon["tier"]}) \
            .eq("id", data.user_id) \
            .execute()

        # Mark used
        supabase.table("evosgpt_coupons") \
            .update({"used": True}) \
            .eq("code", code) \
            .execute()

        return {
            "status": "ok",
            "message": f"Upgraded to {coupon['tier']} successfully!",
            "tier": coupon["tier"]
        }

    except Exception as e:
        print("COUPON ERROR:", str(e))
        raise HTTPException(500, "Coupon redemption failed")


# =========================
# REFERRAL ROUTE
# =========================

@app.get("/referral/{user_id}")
def get_referral(user_id: str):
    try:
        res = supabase.table("evosgpt_users") \
            .select("referral_code, referral_count") \
            .eq("id", user_id) \
            .limit(1) \
            .execute()

        if not res.data:
            raise HTTPException(404, "User not found")

        user = res.data[0]
        referral_link = f"https://evosgpt.xyz/register?ref={user['referral_code']}"

        return {
            "status": "ok",
            "referral_code": user["referral_code"],
            "referral_count": user.get("referral_count", 0),
            "referral_link": referral_link,
        }

    except HTTPException:
        raise
    except Exception as e:
        print("REFERRAL ERROR:", str(e))
        raise HTTPException(500, "Failed to fetch referral")


# =========================
# HEALTH CHECK
# =========================

@app.get("/")
def health():
    return {"status": "ok", "service": "EVOSGPT API"}
