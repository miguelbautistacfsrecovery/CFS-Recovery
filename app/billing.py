import stripe
from fastapi import APIRouter, Request, HTTPException, Header

from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_PRICE_ID, APP_URL, SUPABASE_URL, SUPABASE_KEY
from app.auth import get_user_from_token
from supabase import create_client

router = APIRouter()
stripe.api_key = STRIPE_SECRET_KEY
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@router.post("/create-checkout")
async def create_checkout(authorization: str = Header(None)):
    user = get_user_from_token(authorization)

    if not user.get("stripe_customer_id"):
        customer = stripe.Customer.create(email=user["email"])
        supabase.table("users").update({"stripe_customer_id": customer.id}).eq("id", user["id"]).execute()
        customer_id = customer.id
    else:
        customer_id = user["stripe_customer_id"]

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
        mode="subscription",
        success_url=f"{APP_URL}/?checkout=success",
        cancel_url=f"{APP_URL}/?checkout=cancel",
        metadata={"user_id": str(user["id"])},
    )
    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        if customer_id:
            supabase.table("users").update({
                "stripe_subscription_id": subscription_id,
                "subscription_status": "active",
            }).eq("stripe_customer_id", customer_id).execute()

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        if customer_id:
            supabase.table("users").update({
                "subscription_status": "canceled",
            }).eq("stripe_customer_id", customer_id).execute()

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        if customer_id:
            supabase.table("users").update({
                "subscription_status": "past_due",
            }).eq("stripe_customer_id", customer_id).execute()

    return {"status": "ok"}
