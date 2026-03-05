import hashlib
import hmac
import json
import time
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Header
from supabase import create_client

from app.config import SUPABASE_URL, SUPABASE_KEY, APP_SECRET_KEY, DAILY_MESSAGE_LIMIT

router = APIRouter()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_token(user_id: int, email: str) -> str:
    payload = json.dumps({"user_id": user_id, "email": email, "ts": int(time.time())})
    sig = hmac.new(APP_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}|{sig}"


def verify_token(token: str) -> dict:
    try:
        payload_str, sig = token.rsplit("|", 1)
        expected = hmac.new(APP_SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise HTTPException(status_code=401, detail="Invalid token")
        return json.loads(payload_str)
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user_from_token(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")
    token = authorization.removeprefix("Bearer ")
    payload = verify_token(token)
    result = supabase.table("users").select("*").eq("id", payload["user_id"]).single().execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="User not found")
    return result.data


def check_access(user: dict) -> str:
    """Returns 'active' if user can chat, or the reason they can't."""
    status = user["subscription_status"]
    if status == "active":
        return "active"
    if status == "trial":
        trial_ends = datetime.fromisoformat(user["trial_ends"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) < trial_ends:
            return "active"
        return "trial_expired"
    return "inactive"


def get_daily_usage(user_id: int) -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = supabase.table("daily_usage").select("message_count").eq("user_id", user_id).eq("usage_date", today).execute()
    if result.data:
        return result.data[0]["message_count"]
    return 0


def increment_usage(user_id: int) -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = supabase.table("daily_usage").select("*").eq("user_id", user_id).eq("usage_date", today).execute()
    if result.data:
        new_count = result.data[0]["message_count"] + 1
        supabase.table("daily_usage").update({"message_count": new_count}).eq("id", result.data[0]["id"]).execute()
        return new_count
    else:
        supabase.table("daily_usage").insert({"user_id": user_id, "usage_date": today, "message_count": 1}).execute()
        return 1


@router.post("/signup")
async def signup(email: str):
    existing = supabase.table("users").select("id, subscription_status, trial_ends").eq("email", email).execute()
    if existing.data:
        user = existing.data[0]
        token = create_token(user["id"], email)
        access = check_access(user)
        usage = get_daily_usage(user["id"])
        return {
            "token": token,
            "status": access,
            "messages_used": usage,
            "messages_remaining": max(0, DAILY_MESSAGE_LIMIT - usage),
        }
    result = supabase.table("users").insert({"email": email}).execute()
    user = result.data[0]
    token = create_token(user["id"], email)
    return {
        "token": token,
        "status": "active",
        "messages_used": 0,
        "messages_remaining": DAILY_MESSAGE_LIMIT,
    }


@router.get("/status")
async def get_status(authorization: str = Header(None)):
    user = get_user_from_token(authorization)
    access = check_access(user)
    usage = get_daily_usage(user["id"])
    return {
        "status": access,
        "subscription_status": user["subscription_status"],
        "messages_used": usage,
        "messages_remaining": max(0, DAILY_MESSAGE_LIMIT - usage),
        "email": user["email"],
    }
