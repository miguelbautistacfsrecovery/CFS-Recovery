import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
VOYAGE_API_KEY = os.environ["VOYAGE_API_KEY"]
STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]
STRIPE_WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]
STRIPE_PRICE_ID = os.environ["STRIPE_PRICE_ID"]
APP_SECRET_KEY = os.environ["APP_SECRET_KEY"]
APP_URL = os.environ.get("APP_URL", "http://localhost:8000")

DAILY_MESSAGE_LIMIT = 50
TRIAL_DAYS = 3
PERSONAL_QUESTION_THRESHOLD = 5
