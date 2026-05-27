from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from supabase import create_client, Client
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
SUPABASE_URL      = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_KEY      = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY")
PAYSTACK_SECRET   = os.getenv("PAYSTACK_SECRET_KEY")

# =========================
# SUPABASE CLIENTS
# auth_client -> anon key  -> Supabase Auth (sign_up / sign_in)
# db_client   -> service role key -> DB reads/writes (bypasses RLS)
# =========================
auth_client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
db_client: Client   = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# TIER CONFIG
# =========================
TIER_MODELS = {
    "Basic":   "gpt-4o-mini",
    "Core":    "gpt-4o-mini",
    "Pro":     "gpt-4o",
    "King":    "gpt-4o",
    "Founder": "gpt-4o",
}

TIER_MEMORY_LIMIT = {
    "Basic":   20,
    "Core":    50,
    "Pro":     100,
    "King":    200,
    "Founder": 500,
}

TIER_PRICES_GHS = {
    "Core": 15,
    "Pro":  75,
    "King": 135,
}

VALID_UPGRADE_TIERS = set(TIER_PRICES_GHS.keys())

# =========================
# REQUEST MODELS
# =========================
class RegisterRequest(BaseModel):
    username:    str
    email:       EmailStr
    password:    str
    referred_by: Optional[str] = None

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class ChatRequest(BaseModel):
    user_id: str
    message: str

class UpgradeRequest(BaseModel):
    user_id: str
    tier:    str
    email:   str

class CouponRequest(BaseModel):
    user_id: str
    code:    str


# =========================
# PROFILE HELPERS
# =========================

def get_profile(user_id: str) -> Optional[dict]:
    res = db_client.table("profiles") \
        .select("*") \
        .eq("id", user_id) \
        .limit(1) \
        .execute()
    return res.data[0] if res.data else None


def get_user_tier(user_id: str) -> str:
    profile = get_profile(user_id)
    return profile.get("tier", "Basic") if profile else "Basic"


def create_profile(user_id: str, username: str, email: str, referred_by: Optional[str]) -> str:
    referral_code = f"EVOS-{username[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"

    db_client.table("profiles").insert({
        "id":             user_id,
        "username":       username,
        "email":          email,
        "tier":           "Basic",
        "referral_code":  referral_code,
        "referred_by":    referred_by,
        "referral_count": 0,
        "created_at":     datetime.now(timezone.utc).isoformat()
    }).execute()

    if referred_by:
        try:
            ref_res = db_client.table("profiles") \
                .select("id, referral_count") \
                .eq("referral_code", referred_by) \
                .limit(1) \
                .execute()
            if ref_res.data:
                ref_user = ref_res.data[0]
                db_client.table("profiles") \
                    .update({"referral_count": (ref_user.get("referral_count") or 0) + 1}) \
                    .eq("id", ref_user["id"]) \
                    .execute()
        except Exception as e:
            print("REFERRAL CREDIT ERROR:", str(e))

    return referral_code


# =========================
# MEMORY HELPERS
# =========================

def get_short_memory(user_id: str, limit: int = 20) -> list:
    res = db_client.table("evosgpt_memory") \
        .select("role, content") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .limit(limit) \
        .execute()
    return list(reversed(res.data or []))


def get_long_memory(user_id: str) -> Optional[str]:
    res = db_client.table("evosgpt_long_memory") \
        .select("summary") \
        .eq("user_id", user_id) \
        .limit(1) \
        .execute()
    return res.data[0].get("summary") if res.data else None


def save_message(user_id: str, role: str, content: str):
    db_client.table("evosgpt_memory").insert({
        "user_id":    user_id,
        "role":       role,
        "content":    content,
        "created_at": datetime.now(timezone.utc).isoformat()
    }).execute()


def trim_memory(user_id: str, tier: str):
    limit = TIER_MEMORY_LIMIT.get(tier, 20)
    res = db_client.table("evosgpt_memory") \
        .select("id") \
        .eq("user_id", user_id) \
        .order("created_at", desc=False) \
        .execute()
    rows = res.data or []
    if len(rows) > limit:
        ids_to_delete = [r["id"] for r in rows[:len(rows) - limit]]
        for rid in ids_to_delete:
            db_client.table("evosgpt_memory") \
                .delete() \
                .eq("id", rid) \
                .execute()


def update_long_memory(user_id: str, new_summary: str):
    existing = get_long_memory(user_id)
    if existing:
        merge_prompt = f"Merge these two summaries of the same user into one concise paragraph.\nOld: {existing}\nNew: {new_summary}"
        merged = call_openai("gpt-4o-mini", "You are a memory summarizer.", merge_prompt)
        summary = merged or new_summary
        db_client.table("evosgpt_long_memory") \
            .update({"summary": summary, "updated_at": datetime.now(timezone.utc).isoformat()}) \
            .eq("user_id", user_id) \
            .execute()
    else:
        db_client.table("evosgpt_long_memory").insert({
            "user_id":    user_id,
            "summary":    new_summary,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).execute()


# =========================
# AI HELPERS
# =========================

def build_system_prompt(tier: str, long_memory: Optional[str]) -> str:
    base = {
        "Basic":   "You are EVOSGPT, a helpful and friendly AI assistant. Keep answers clear and concise.",
        "Core":    "You are EVOSGPT, a structured and helpful AI assistant. Use numbered lists and bullet points for clarity.",
        "Pro":     "You are EVOSGPT, a confident and insightful AI assistant. Provide detailed, well-structured answers with examples.",
        "King":    "You are EVOSGPT, a powerful and strategic AI. Provide expert-level answers with deep insights and pro tips.",
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
                "Content-Type":  "application/json"
            },
            json={"model": model, "messages": messages},
            timeout=30
        )
        data = res.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("OPENAI ERROR:", str(e))
        return None


def summarize_recent_memory(history: list) -> Optional[str]:
    if not history:
        return None
    conversation = "\n".join([f"{h['role'].capitalize()}: {h['content']}" for h in history[-10:]])
    prompt = f"Summarize this conversation in one concise paragraph. Focus on the user's goals, personality, and key topics.\n\nConversation:\n{conversation}"
    return call_openai("gpt-4o-mini", "You are a memory summarizer.", prompt)


# =========================
# AUTH ROUTES
# =========================

@app.post("/auth/register")
def register(data: RegisterRequest):
    try:
        username = data.username.strip().lower()
        email    = data.email.strip().lower()

        if len(username) < 3:
            raise HTTPException(400, "Username must be at least 3 characters")
        if len(data.password) < 6:
            raise HTTPException(400, "Password must be at least 6 characters")

        # Check username taken in profiles
        existing = db_client.table("profiles") \
            .select("id") \
            .eq("username", username) \
            .limit(1) \
            .execute()
        if existing.data:
            return {"status": "username_taken"}

        # Register via Supabase Auth (handles hashing + sessions)
        auth_res = auth_client.auth.sign_up({
            "email":    email,
            "password": data.password,
        })

        if not auth_res.user:
            return {"status": "email_taken"}

        user_id = auth_res.user.id

        # Create profile linked to auth.users.id
        referral_code = create_profile(
            user_id=user_id,
            username=username,
            email=email,
            referred_by=data.referred_by
        )

        return {
            "status": "created",
            "user": {
                "id":            user_id,
                "username":      username,
                "email":         email,
                "tier":          "Basic",
                "referral_code": referral_code,
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
        email = data.email.strip().lower()

        # Supabase Auth verifies password
        auth_res = auth_client.auth.sign_in_with_password({
            "email":    email,
            "password": data.password,
        })

        if not auth_res.user:
            return {"status": "invalid_credentials"}

        user_id = auth_res.user.id

        # Fetch from shared profiles table
        profile = get_profile(user_id)

        if not profile:
            return {"status": "profile_not_found"}

        return {
            "status": "ok",
            "user": {
                "id":            user_id,
                "username":      profile.get("username", ""),
                "email":         profile.get("email", ""),
                "tier":          profile.get("tier", "Basic"),
                "referral_code": profile.get("referral_code", ""),
                "referred_by":   profile.get("referred_by", ""),
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

        tier  = get_user_tier(user_id)
        model = TIER_MODELS.get(tier, "gpt-4o-mini")

        short_memory  = get_short_memory(user_id, limit=TIER_MEMORY_LIMIT.get(tier, 20))
        long_memory   = get_long_memory(user_id)
        system_prompt = build_system_prompt(tier, long_memory)

        reply = call_openai(model, system_prompt, message, short_memory)

        if not reply:
            raise HTTPException(500, "AI service unavailable")

        save_message(user_id, "user", message)
        save_message(user_id, "assistant", reply)
        trim_memory(user_id, tier)

        total = len(short_memory) + 1
        if total % 10 == 0:
            summary = summarize_recent_memory(short_memory)
            if summary:
                update_long_memory(user_id, summary)

        return {
            "status": "ok",
            "reply":  reply,
            "tier":   tier,
            "model":  model,
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
        return {
            "status":       "ok",
            "short_memory": get_short_memory(user_id, limit=50),
            "long_memory":  get_long_memory(user_id),
        }
    except Exception as e:
        print("MEMORY ERROR:", str(e))
        raise HTTPException(500, "Failed to fetch memory")


@app.delete("/memory/{user_id}")
def clear_memory(user_id: str):
    try:
        db_client.table("evosgpt_memory").delete().eq("user_id", user_id).execute()
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
        profile = get_profile(user_id)
        if not profile:
            raise HTTPException(404, "User not found")

        mem_res = db_client.table("evosgpt_memory") \
            .select("id", count="exact") \
            .eq("user_id", user_id) \
            .execute()

        return {
            "status": "ok",
            "user": {**profile, "message_count": mem_res.count or 0}
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
        reference  = f"EVOS-GPT-{data.user_id[:8]}-{uuid.uuid4().hex[:8].upper()}"

        paystack = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers={"Authorization": f"Bearer {PAYSTACK_SECRET}", "Content-Type": "application/json"},
            json={
                "email":        data.email,
                "amount":       int(amount_ghs * 100),
                "reference":    reference,
                "callback_url": "https://evosgpt.xyz/upgrade/success",
                "metadata":     {"user_id": data.user_id, "tier": data.tier}
            },
            timeout=15
        ).json()

        if not paystack.get("status"):
            raise HTTPException(400, "Payment initialization failed")

        db_client.table("evosgpt_purchases").insert({
            "user_id":    data.user_id,
            "tier":       data.tier,
            "reference":  reference,
            "status":     "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()

        return {
            "status":      "ok",
            "payment_url": paystack["data"]["authorization_url"],
            "reference":   reference,
        }

    except HTTPException:
        raise
    except Exception as e:
        print("UPGRADE INIT ERROR:", str(e))
        raise HTTPException(500, "Upgrade initialization failed")


@app.post("/webhook/paystack")
async def paystack_webhook(request: Request):
    try:
        body      = await request.body()
        signature = request.headers.get("x-paystack-signature", "")
        computed  = hmac.new(PAYSTACK_SECRET.encode("utf-8"), body, hashlib.sha512).hexdigest()

        if not hmac.compare_digest(computed, signature):
            return {"status": "invalid signature"}

        payload = await request.json()

        if payload.get("event") != "charge.success":
            return {"status": "ignored"}

        data      = payload["data"]
        reference = data["reference"]
        meta      = data.get("metadata", {})
        user_id   = meta.get("user_id")
        tier      = meta.get("tier")

        if not user_id or not tier:
            return {"status": "missing metadata"}

        existing = db_client.table("evosgpt_purchases") \
            .select("id, status").eq("reference", reference).limit(1).execute()

        if existing.data and existing.data[0]["status"] == "paid":
            return {"status": "already processed"}

        # Upgrade tier in shared profiles table
        db_client.table("profiles").update({"tier": tier}).eq("id", user_id).execute()
        db_client.table("evosgpt_purchases").update({"status": "paid"}).eq("reference", reference).execute()

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
        res  = db_client.table("evosgpt_coupons").select("*").eq("code", code).limit(1).execute()

        if not res.data:
            return {"status": "invalid", "message": "Invalid coupon code"}

        coupon = res.data[0]
        if coupon["used"]:
            return {"status": "used", "message": "Coupon already used"}

        # Upgrade in shared profiles table
        db_client.table("profiles").update({"tier": coupon["tier"]}).eq("id", data.user_id).execute()
        db_client.table("evosgpt_coupons").update({"used": True}).eq("code", code).execute()

        return {"status": "ok", "message": f"Upgraded to {coupon['tier']}!", "tier": coupon["tier"]}

    except Exception as e:
        print("COUPON ERROR:", str(e))
        raise HTTPException(500, "Coupon redemption failed")


# =========================
# REFERRAL ROUTE
# =========================

@app.get("/referral/{user_id}")
def get_referral(user_id: str):
    try:
        profile = get_profile(user_id)
        if not profile:
            raise HTTPException(404, "User not found")

        return {
            "status":         "ok",
            "referral_code":  profile["referral_code"],
            "referral_count": profile.get("referral_count", 0),
            "referral_link":  f"https://evosgpt.xyz/register?ref={profile['referral_code']}",
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
    return {"status": "ok", "service": "EVOSGPT API v2"}
