from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response  # ← add this line
from pydantic import BaseModel, EmailStr
from typing import Optional
from supabase import create_client, Client
from passlib.context import CryptContext
from datetime import datetime, timezone
import os, uuid, hmac, hashlib, requests, re
from dotenv import load_dotenv

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9 fallback
    from backports.zoneinfo import ZoneInfo

load_dotenv()

app = FastAPI(title="EVOSGPT API", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://evosgpt.xyz",
        "https://www.evosgpt.xyz",
        "https://evosgpt.netlify.app",
        "https://evosdata.xyz",
        "https://www.evosdata.xyz",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ENV
SUPABASE_URL      = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_KEY      = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY")
PAYSTACK_SECRET   = os.getenv("PAYSTACK_SECRET_KEY")

anon_client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
db_client:   Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.on_event("startup")
def _startup():
    ensure_image_bucket()

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(p): return pwd.hash(p)
def verify_password(p, h): return pwd.verify(p, h)

TIERS = {
    "Basic":   {"model": "gpt-4o-mini", "memory_limit": 20,   "day_limit": 10,   "price_ghs": 0,   "icon": "🧊"},
    "Pro":     {"model": "gpt-4o",      "memory_limit": 100,  "day_limit": None, "price_ghs": 20,  "icon": "⚡"},
    "Core":    {"model": "gpt-4o",      "memory_limit": 300,  "day_limit": None, "price_ghs": 70, "icon": "🔥"},
    "Founder": {"model": "gpt-4o",      "memory_limit": 1000, "day_limit": None, "price_ghs": 0,   "icon": "👑"},
}
PURCHASABLE_TIERS = {"Pro", "Core"}
IMAGE_GEN_TIERS = {"Pro", "Core", "Founder"}  # Basic tier cannot generate images

BASE_PROMPT = """You are EVOSGPT — an evolving AI assistant built by EVOS Technologies.
You adapt, remember, and grow with each user over time.

FORMATTING RULES (always follow):
- Code -> wrap in markdown code blocks with language tag: ```python, ```javascript, etc.
- Letters / formal writing -> proper structure: date, salutation, body, closing. Clean and copy-paste ready.
- Lists -> numbered or bullet points.
- Tables -> markdown table format.
- Explanations -> short paragraphs with bold headers where helpful.
- Never output a wall of unformatted text.
- After code blocks or letters, add: "Copy the above and paste directly."

You serve users primarily in Ghana and across Africa. Be smart, direct, and practical.

IMAGE POLICY (always follow):
- You CAN see and analyze images the user uploads in this chat — describe them, read text in them, answer questions about them, give feedback on them.
- You CANNOT draw or generate an image yourself as part of a normal reply. Never output markdown image syntax (e.g. ![alt](url)), base64 image data, or claim you created/attached an image inline in your text.
- EVOSGPT has a separate built-in image-generation tool (the 🎨 button next to the message box) that actually creates images, available on Pro tier and above.
- If a user asks you to generate/create/draw/design an image, logo, photo, or picture: if they're eligible for it, tell them to tap the 🎨 button and describe what they want there. If they're on Basic tier, tell them image generation requires upgrading to Pro."""

TIER_PERSONA = {
    "Basic":   "\n\nYou are in Basic mode. Be helpful and concise. For advanced tasks, mention that Pro or Core tier unlocks more power.",
    "Pro":     "\n\nYou are in Pro mode. The user is a professional (developer, designer, writer, entrepreneur). Deliver expert-quality answers. Code must be clean, commented, production-ready. Design briefs detailed. Writing polished.",
    "Core":    "\n\nYou are in Core mode, the most powerful tier. Think like a senior engineer, creative director, and strategist combined. Give thorough, insightful, structured responses.",
    "Founder": "\n\nYou are in Founder mode, exclusive access, unlimited intelligence and context. Be brilliant.",
}

EVOS_NUDGE = "\n\nIf the user mentions running low on data or internet, remind them they can buy affordable Ghana data bundles instantly at https://evosdata.xyz, part of the EVOS ecosystem."

class RegisterRequest(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    referred_by: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    user_id: int
    message: str
    image_base64: Optional[str] = None   # raw base64, no data-URI prefix
    image_mime: Optional[str] = "image/jpeg"

class ImageGenRequest(BaseModel):
    user_id: int
    prompt: str

class UpgradeRequest(BaseModel):
    user_id: int
    tier: str
    email: str

class CouponRequest(BaseModel):
    user_id: int
    code: str


def get_user_by_id(user_id: int) -> Optional[dict]:
    res = db_client.table("users").select("*").eq("id", user_id).limit(1).execute()
    return res.data[0] if res.data else None

def get_user_tier(user_id: int) -> str:
    u = get_user_by_id(user_id)
    return u.get("evosgpt_tier", "Basic") if u else "Basic"

def generate_referral_code(username: str) -> str:
    return f"EVOS-{username[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"


def get_short_memory(user_id: int, limit: int = 20) -> list:
    res = db_client.table("evosgpt_memory").select("role,content").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    return list(reversed(res.data or []))

def get_long_memory(user_id: int) -> Optional[str]:
    res = db_client.table("evosgpt_long_memory").select("summary").eq("user_id", user_id).limit(1).execute()
    return res.data[0]["summary"] if res.data else None

def save_message(user_id: int, role: str, content: str):
    db_client.table("evosgpt_memory").insert({
        "user_id": user_id, "role": role, "content": content,
        "created_at": datetime.now(timezone.utc).isoformat()
    }).execute()

def trim_memory(user_id: int, limit: int):
    res = db_client.table("evosgpt_memory").select("id").eq("user_id", user_id).order("created_at", desc=False).execute()
    rows = res.data or []
    if len(rows) > limit:
        for r in rows[:len(rows) - limit]:
            db_client.table("evosgpt_memory").delete().eq("id", r["id"]).execute()

def update_long_memory(user_id: int, new_summary: str):
    existing = get_long_memory(user_id)
    if existing:
        merged = call_openai("gpt-4o-mini", "You are a memory summarizer. Be concise and factual.",
            f"Merge these two user summaries into one paragraph:\nOld: {existing}\nNew: {new_summary}")
        summary = merged or new_summary
        db_client.table("evosgpt_long_memory").update({"summary": summary, "updated_at": datetime.now(timezone.utc).isoformat()}).eq("user_id", user_id).execute()
    else:
        db_client.table("evosgpt_long_memory").insert({"user_id": user_id, "summary": new_summary, "updated_at": datetime.now(timezone.utc).isoformat()}).execute()


def get_today_count(user_id: int) -> int:
    today = datetime.now(timezone.utc).date().isoformat()
    res = db_client.table("evosgpt_daily_chats").select("count").eq("user_id", user_id).eq("date", today).limit(1).execute()
    return res.data[0]["count"] if res.data else 0

def increment_today_count(user_id: int):
    today = datetime.now(timezone.utc).date().isoformat()
    res = db_client.table("evosgpt_daily_chats").select("id,count").eq("user_id", user_id).eq("date", today).limit(1).execute()
    if res.data:
        db_client.table("evosgpt_daily_chats").update({"count": res.data[0]["count"] + 1}).eq("id", res.data[0]["id"]).execute()
    else:
        db_client.table("evosgpt_daily_chats").insert({"user_id": user_id, "date": today, "count": 1}).execute()


# =========================
# GEOLOCATION + LOCAL TIME
# =========================
def get_client_ip(request: Request) -> str:
    # Render/Railway/most proxies set X-Forwarded-For
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "8.8.8.8"

def get_geo_context(request: Request) -> dict:
    """
    Looks up the caller's approximate location + local time from their IP.
    Uses ip-api.com (free, no key required, ~45 req/min limit).
    Falls back to UTC if the lookup fails (e.g. localhost, rate limit, no network).
    """
    ip = get_client_ip(request)
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = res.json()
        if data.get("status") != "success":
            raise ValueError(data.get("message", "geo lookup failed"))

        tz_name = data.get("timezone", "UTC")
        try:
            local_dt = datetime.now(ZoneInfo(tz_name))
            local_time = local_dt.strftime("%A, %d %B %Y, %I:%M %p")
        except Exception:
            tz_name = "UTC"
            local_time = datetime.now(timezone.utc).strftime("%A, %d %B %Y, %I:%M %p UTC")

        return {
            "ip": ip,
            "city": data.get("city", ""),
            "region": data.get("regionName", ""),
            "country": data.get("country", ""),
            "country_code": data.get("countryCode", ""),
            "timezone": tz_name,
            "local_time": local_time,
        }
    except Exception as e:
        print("GEO LOOKUP ERROR:", e)
        return {
            "ip": ip,
            "city": "", "region": "", "country": "", "country_code": "",
            "timezone": "UTC",
            "local_time": datetime.now(timezone.utc).strftime("%A, %d %B %Y, %I:%M %p UTC"),
        }


# =========================
# STRAY-IMAGE-SYNTAX SAFETY NET
# =========================
# The model is told never to fabricate inline image markdown in a normal
# reply (real generated images come back from /image/generate as their own
# field, not inline markdown). This just catches any stray markdown image
# syntax that slips into a *text* reply so we never show a broken/fake image.
_MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")

def strip_stray_image_markdown(text: Optional[str]) -> Optional[str]:
    if not text:
        return text
    return _MD_IMAGE_RE.sub("", text).strip()


def call_openai(model: str, system: str, user_msg, history: list = []) -> Optional[str]:
    """user_msg can be a plain string, or a list of content blocks (for vision)."""
    try:
        messages = [{"role": "system", "content": system}]
        for h in history:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_msg})
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "temperature": 0.7},
            timeout=60
        )
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("OPENAI ERROR:", e)
        return None


def generate_image(prompt: str, size: str = "1024x1024") -> Optional[str]:
    """Calls OpenAI's image generation API and returns base64 PNG data (no data-URI prefix)."""
    try:
        res = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={"model": "gpt-image-1", "prompt": prompt, "size": size, "n": 1},
            timeout=90
        )
        data = res.json()
        return data["data"][0]["b64_json"]
    except Exception as e:
        print("IMAGE GEN ERROR:", e)
        return None


IMAGE_BUCKET = "evosgpt-images"

def ensure_image_bucket():
    try:
        buckets = db_client.storage.list_buckets()
        if not any(b.name == IMAGE_BUCKET for b in buckets):
            db_client.storage.create_bucket(IMAGE_BUCKET, options={"public": True})
    except Exception as e:
        print("BUCKET SETUP WARNING:", e)

def upload_generated_image(user_id: int, b64_png: str) -> Optional[str]:
    try:
        import base64 as _b64
        raw = _b64.b64decode(b64_png)
        path = f"{user_id}/{uuid.uuid4().hex}.png"
        db_client.storage.from_(IMAGE_BUCKET).upload(
            path, raw, file_options={"content-type": "image/png"}
        )
        return db_client.storage.from_(IMAGE_BUCKET).get_public_url(path)
    except Exception as e:
        print("IMAGE UPLOAD ERROR:", e)
        return None

def build_system_prompt(tier: str, long_memory: Optional[str], username: str, geo: Optional[dict] = None) -> str:
    prompt = BASE_PROMPT + TIER_PERSONA.get(tier, TIER_PERSONA["Basic"]) + EVOS_NUDGE
    prompt += f"\n\nThe user's name is {username}."
    if tier in IMAGE_GEN_TIERS:
        prompt += " This user's tier includes access to the 🎨 image-generation button."
    else:
        prompt += " This user is on Basic tier: image generation is NOT available to them until they upgrade to Pro."

    if geo and geo.get("local_time"):
        location_str = ", ".join(filter(None, [geo.get("city"), geo.get("country")]))
        prompt += f"\n\nThe user's current local time is {geo['local_time']}"
        if location_str:
            prompt += f", and they appear to be located in {location_str}."
        else:
            prompt += "."
        prompt += " Use this naturally when it's relevant (greetings, deadlines, scheduling, local context, time-sensitive answers). Don't mention that you're using IP-based geolocation unless the user asks how you know."

    if long_memory:
        prompt += f"\n\nWhat you know about this user from past conversations:\n{long_memory}"
    return prompt

def summarize_memory(history: list) -> Optional[str]:
    if len(history) < 4:
        return None
    convo = "\n".join([f"{h['role'].capitalize()}: {h['content']}" for h in history[-10:]])
    return call_openai("gpt-4o-mini", "You are a memory summarizer for an AI assistant. Be concise.",
        f"Summarize this conversation in 2-3 sentences. Focus on the user's goals, skills, and key topics:\n\n{convo}")


@app.post("/auth/register")
def register(data: RegisterRequest):
    try:
        username  = data.username.strip().lower()
        email     = data.email.strip().lower()
        full_name = data.full_name.strip()
        phone     = (data.phone or "").strip()

        if len(username) < 3:
            raise HTTPException(400, "Username must be at least 3 characters")
        if len(data.password) < 6:
            raise HTTPException(400, "Password must be at least 6 characters")

        if db_client.table("users").select("id").eq("username", username).limit(1).execute().data:
            return {"status": "username_taken"}
        if db_client.table("users").select("id").eq("email", email).limit(1).execute().data:
            return {"status": "email_taken"}

        try:
            hashed_password = hash_password(data.password)
        except Exception as e:
            print("HASH ERROR:", e)
            raise HTTPException(500, "Password hashing failed")

        referral_code = generate_referral_code(username)

        res = db_client.table("users").insert({
            "username":      username,
            "full_name":     full_name,
            "email":         email,
            "phone":         phone,
            "password":      hashed_password,
            "referral_code": referral_code,
            "referred_by":   data.referred_by or None,
            "evosgpt_tier":  "Basic",
            "role":          "customer",
            "created_at":    datetime.now(timezone.utc).isoformat(),
        }).execute()

        if not res.data:
            raise HTTPException(500, "Registration failed")

        user = res.data[0]

        if data.referred_by:
            try:
                ref = db_client.table("users").select("id,order_count").eq("referral_code", data.referred_by).limit(1).execute()
                if ref.data:
                    db_client.table("users").update({
                        "order_count": (ref.data[0].get("order_count") or 0) + 1
                    }).eq("id", ref.data[0]["id"]).execute()
            except Exception as e:
                print("REFERRAL ERROR:", e)

        return {
            "status": "created",
            "user": {
                "id":            user["id"],
                "username":      user["username"],
                "full_name":     user["full_name"],
                "email":         user["email"],
                "evosgpt_tier":  "Basic",
                "referral_code": referral_code,
            }
        }
    except HTTPException: raise
    except Exception as e:
        print("REGISTER ERROR:", e)
        raise HTTPException(500, "Server error")


@app.post("/auth/login")
def login(data: LoginRequest):
    try:
        identifier = (data.username or "").strip().lower()
        if not identifier:
            raise HTTPException(400, "Username required")

        res = db_client.table("users").select("*").or_(
            f"username.eq.{identifier},email.eq.{identifier}"
        ).limit(1).execute()

        # Timing-safe: always run verify even if user not found
        dummy_hash = "$2b$12$KIXzCq3C3T6tFkUd9nj6aO.WwSIFqh4fQieFzpxKx5Mj5.z1rklHC"
        stored_password = res.data[0].get("password") if res.data else dummy_hash

        try:
            password_ok = verify_password(data.password, stored_password)
        except Exception:
            password_ok = False

        if not res.data or not password_ok:
            return {"status": "invalid_credentials"}

        user = res.data[0]

        return {
            "status": "ok",
            "user": {
                "id":            user["id"],
                "username":      user["username"],
                "full_name":     user.get("full_name", ""),
                "email":         user["email"],
                "evosgpt_tier":  user.get("evosgpt_tier", "Basic"),
                "referral_code": user.get("referral_code", ""),
                "role":          user.get("role", "user"),
            }
        }
    except HTTPException: raise
    except Exception as e:
        print("LOGIN ERROR:", e)
        raise HTTPException(500, "Server error")

@app.post("/chat")
def chat(data: ChatRequest, request: Request):
    try:
        user_id = data.user_id
        message = data.message.strip()
        if not message:
            raise HTTPException(400, "Message cannot be empty")

        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")

        tier     = user.get("evosgpt_tier", "Basic")
        username = user.get("username", "friend")
        tier_cfg = TIERS.get(tier, TIERS["Basic"])
        model     = tier_cfg["model"]
        mem_limit = tier_cfg["memory_limit"]
        day_limit = tier_cfg["day_limit"]

        today_count        = get_today_count(user_id)
        show_upgrade_nudge = False

        if day_limit is not None and today_count >= day_limit:
            return {
                "status": "limit_reached",
                "reply": f"You've used all {day_limit} free chats for today. Come back tomorrow or upgrade to Pro for unlimited chats!",
                "tier": tier, "limit_reached": True,
                "today_count": today_count, "day_limit": day_limit,
            }

        if day_limit is not None and today_count in [4, 7]:
            show_upgrade_nudge = True

        geo           = get_geo_context(request)
        short_memory  = get_short_memory(user_id, limit=mem_limit)
        long_memory   = get_long_memory(user_id)
        system_prompt = build_system_prompt(tier, long_memory, username, geo)

        if data.image_base64:
            user_content = [
                {"type": "text", "text": message or "What's in this image?"},
                {"type": "image_url", "image_url": {"url": f"data:{data.image_mime or 'image/jpeg'};base64,{data.image_base64}"}},
            ]
            # Vision models need gpt-4o (or mini); both tiers already map to a vision-capable model.
            reply = call_openai(model, system_prompt, user_content, short_memory)
        else:
            reply = call_openai(model, system_prompt, message, short_memory)

        if not reply:
            raise HTTPException(500, "AI service unavailable. Try again.")
        reply = strip_stray_image_markdown(reply)

        # Store a text-only record in memory (images aren't persisted into long-term history).
        stored_user_msg = message if not data.image_base64 else f"[Image uploaded] {message}".strip()
        save_message(user_id, "user", stored_user_msg)
        save_message(user_id, "assistant", reply)
        trim_memory(user_id, mem_limit)
        increment_today_count(user_id)

        total = len(short_memory) + 1
        if total % 10 == 0:
            summary = summarize_memory(short_memory)
            if summary:
                update_long_memory(user_id, summary)

        return {
            "status": "ok", "reply": reply, "tier": tier, "model": model,
            "today_count": today_count + 1, "day_limit": day_limit,
            "show_upgrade_nudge": show_upgrade_nudge,
            "location": {
                "city": geo.get("city", ""),
                "country": geo.get("country", ""),
                "timezone": geo.get("timezone", "UTC"),
                "local_time": geo.get("local_time", ""),
            },
        }
    except HTTPException: raise
    except Exception as e:
        print("CHAT ERROR:", e)
        raise HTTPException(500, "Chat failed")


@app.post("/image/generate")
def image_generate(data: ImageGenRequest, request: Request):
    try:
        user_id = data.user_id
        prompt  = data.prompt.strip()
        if not prompt:
            raise HTTPException(400, "Prompt cannot be empty")

        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")

        tier = user.get("evosgpt_tier", "Basic")
        if tier not in IMAGE_GEN_TIERS:
            return {
                "status": "tier_restricted",
                "reply": "Image generation is a Pro-tier feature. Upgrade to unlock it!",
                "tier": tier,
            }

        tier_cfg  = TIERS.get(tier, TIERS["Basic"])
        day_limit = tier_cfg["day_limit"]
        today_count = get_today_count(user_id)
        if day_limit is not None and today_count >= day_limit:
            return {
                "status": "limit_reached",
                "reply": f"You've used all {day_limit} free chats for today. Come back tomorrow or upgrade for unlimited chats!",
                "tier": tier, "limit_reached": True,
                "today_count": today_count, "day_limit": day_limit,
            }

        b64_png = generate_image(prompt)
        if not b64_png:
            raise HTTPException(500, "Image generation failed. Try again.")

        image_url = upload_generated_image(user_id, b64_png)
        if not image_url:
            raise HTTPException(500, "Image was generated but could not be saved. Try again.")

        reply = f"![Generated image]({image_url})\n\n*Prompt: {prompt}*"

        save_message(user_id, "user", f"[Image generation request] {prompt}")
        save_message(user_id, "assistant", reply)
        increment_today_count(user_id)

        return {
            "status": "ok", "reply": reply, "image_url": image_url,
            "tier": tier, "today_count": today_count + 1, "day_limit": day_limit,
        }
    except HTTPException: raise
    except Exception as e:
        print("IMAGE ENDPOINT ERROR:", e)
        raise HTTPException(500, "Image generation failed")


@app.get("/memory/{user_id}")
def get_memory(user_id: int):
    try:
        return {"status": "ok", "short_memory": get_short_memory(user_id, 50), "long_memory": get_long_memory(user_id)}
    except Exception:
        raise HTTPException(500, "Failed to fetch memory")

@app.delete("/memory/{user_id}")
def clear_memory(user_id: int):
    try:
        db_client.table("evosgpt_memory").delete().eq("user_id", user_id).execute()
        db_client.table("evosgpt_long_memory").delete().eq("user_id", user_id).execute()
        return {"status": "ok", "message": "Memory cleared. EVOSGPT starts fresh."}
    except Exception:
        raise HTTPException(500, "Failed to clear memory")


@app.get("/user/{user_id}")
def get_user(user_id: int):
    try:
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")

        tier_cfg    = TIERS.get(user.get("evosgpt_tier", "Basic"), TIERS["Basic"])
        today_count = get_today_count(user_id)
        mem_count   = db_client.table("evosgpt_memory").select("id", count="exact").eq("user_id", user_id).execute()
        long_mem    = get_long_memory(user_id)

        return {
            "status": "ok",
            "user": {
                "id": user["id"], "username": user["username"], "full_name": user.get("full_name", ""),
                "email": user["email"], "evosgpt_tier": user.get("evosgpt_tier", "Basic"),
                "referral_code": user.get("referral_code", ""),
                "today_count": today_count, "day_limit": tier_cfg["day_limit"],
                "mem_count": mem_count.count or 0,
                "has_long_mem": long_mem is not None, "long_memory": long_mem,
            }
        }
    except HTTPException: raise
    except Exception:
        raise HTTPException(500, "Failed to fetch user")


@app.get("/geo")
def geo_check(request: Request):
    """Quick utility endpoint to test/debug geolocation + local time detection."""
    try:
        return {"status": "ok", "geo": get_geo_context(request)}
    except Exception as e:
        print("GEO CHECK ERROR:", e)
        raise HTTPException(500, "Failed to detect location")


@app.post("/upgrade/init")
def init_upgrade(data: UpgradeRequest):
    try:
        if data.tier not in PURCHASABLE_TIERS:
            raise HTTPException(400, "Invalid tier")

        tier_cfg   = TIERS[data.tier]
        reference  = f"EVOS-GPT-{data.user_id}-{uuid.uuid4().hex[:8].upper()}"
        amount_ghs = tier_cfg["price_ghs"]

        print(f"UPGRADE ATTEMPT: user={data.user_id} tier={data.tier} email={data.email} amount={amount_ghs} secret_set={bool(PAYSTACK_SECRET)}")

        paystack_res = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers={"Authorization": f"Bearer {PAYSTACK_SECRET}", "Content-Type": "application/json"},
            json={
                "email": data.email, "amount": int(amount_ghs * 100), "currency": "GHS",
                "reference": reference, "callback_url": "https://evosgpt.xyz/upgrade/success",
                "metadata": {"user_id": data.user_id, "tier": data.tier, "product": "evosgpt"},
            }, timeout=15
        )
        paystack = paystack_res.json()
        print("PAYSTACK RESPONSE:", paystack)

        if not paystack.get("status"):
            raise HTTPException(400, paystack.get("message", "Payment initialization failed"))

        db_client.table("evosgpt_purchases").insert({
            "user_id": data.user_id, "tier": data.tier, "reference": reference,
            "status": "pending", "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()

        return {"status": "ok", "payment_url": paystack["data"]["authorization_url"], "reference": reference}
    except HTTPException: raise
    except Exception as e:
        print("UPGRADE ERROR:", e)
        raise HTTPException(500, "Upgrade failed")

@app.post("/webhook/paystack")
async def paystack_webhook(request: Request):
    try:
        body      = await request.body()
        signature = request.headers.get("x-paystack-signature", "")
        computed  = hmac.new(PAYSTACK_SECRET.encode(), body, hashlib.sha512).hexdigest()

        if not hmac.compare_digest(computed, signature):
            return {"status": "invalid_signature"}

        payload = await request.json()
        if payload.get("event") != "charge.success":
            return {"status": "ignored"}

        data      = payload["data"]
        reference = data["reference"]
        meta      = data.get("metadata", {})
        user_id   = meta.get("user_id")
        tier      = meta.get("tier")

        if not user_id or not tier:
            return {"status": "missing_metadata"}

        existing = db_client.table("evosgpt_purchases").select("status").eq("reference", reference).limit(1).execute()
        if existing.data and existing.data[0]["status"] == "paid":
            return {"status": "already_processed"}

        db_client.table("users").update({"evosgpt_tier": tier}).eq("id", user_id).execute()
        db_client.table("evosgpt_purchases").update({"status": "paid"}).eq("reference", reference).execute()

        print(f"User {user_id} upgraded to {tier}")
        return {"status": "success"}
    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return {"status": "error"}


@app.post("/coupon/redeem")
def redeem_coupon(data: CouponRequest):
    try:
        code = data.code.strip().upper()
        res  = db_client.table("evosgpt_coupons").select("*").eq("code", code).limit(1).execute()

        if not res.data:
            return {"status": "invalid", "message": "Invalid coupon code."}

        coupon = res.data[0]
        if coupon["used"]:
            return {"status": "used", "message": "This coupon has already been used."}

        db_client.table("users").update({"evosgpt_tier": coupon["tier"]}).eq("id", data.user_id).execute()
        db_client.table("evosgpt_coupons").update({"used": True, "used_by": data.user_id}).eq("code", code).execute()

        return {"status": "ok", "message": f"Welcome to {coupon['tier']} tier!", "tier": coupon["tier"]}
    except Exception as e:
        print("COUPON ERROR:", e)
        raise HTTPException(500, "Coupon redemption failed")


@app.get("/referral/{user_id}")
def get_referral(user_id: int):
    try:
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return {
            "status": "ok", "referral_code": user["referral_code"],
            "referral_count": user.get("order_count", 0),
            "referral_link": f"https://evosgpt.xyz/register?ref={user['referral_code']}",
        }
    except HTTPException: raise
    except Exception:
        raise HTTPException(500, "Failed")


@app.api_route("/", methods=["GET", "HEAD"])
def health(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"status": "ok", "service": "EVOSGPT API", "version": "2.0", "ecosystem": "EVOS Business Hub"}
