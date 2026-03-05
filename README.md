# Thriver AI - Setup Guide

This is a step-by-step guide to get Thriver AI running. I'll walk you through everything. Each step tells you exactly what to click and where.

---

## STEP 1: Create Your Accounts (15 minutes)

You need 5 accounts. Most are free or have free tiers.

### 1A. Supabase (your database - FREE)

1. Go to https://supabase.com
2. Click "Start your project" and sign up with your Google account or email
3. Click "New project"
4. Give it a name like "thriver-ai"
5. Set a database password (save this somewhere safe, you'll need it)
6. Select the region closest to you
7. Click "Create new project" and wait 2 minutes for it to set up
8. Once ready, click "Project Settings" (gear icon in the left sidebar)
9. Click "API" in the settings menu
10. You'll see two values you need. Copy and save them somewhere:
    - **Project URL** (looks like `https://something.supabase.co`)
    - **anon public** key (a long string of letters and numbers under "Project API keys")

### 1B. Anthropic (the AI brain - pay per use, roughly $10-30/month)

1. Go to https://console.anthropic.com
2. Sign up for an account
3. Add a payment method (Settings > Billing)
4. Go to "API Keys" in the left sidebar
5. Click "Create Key"
6. Name it "thriver-ai"
7. Copy the key and save it (starts with `sk-ant-`)

### 1C. Voyage AI (turns your content into searchable data - about $2 one-time)

1. Go to https://dash.voyageai.com
2. Sign up for an account
3. Go to API Keys
4. Create a new key
5. Copy and save it

### 1D. Stripe (handles the $7/month payments)

1. Go to https://dashboard.stripe.com and create an account
2. Once in the dashboard, click "Product catalog" in the left sidebar
3. Click "+ Add product"
4. Name: "Thriver AI Monthly"
5. Price: $7.00, Recurring, Monthly
6. Click "Save product"
7. Click on the product you just created
8. Under "Pricing", you'll see a Price ID (starts with `price_`). Copy and save it.
9. Now go to "Developers" in the left sidebar
10. Click "API keys"
11. Copy the "Secret key" (starts with `sk_test_` or `sk_live_`). Save it.
12. Still in Developers, click "Webhooks"
13. Click "+ Add endpoint"
14. For the URL, type: `https://your-app-url.up.railway.app/api/billing/webhook` (you'll update this later)
15. Under "Events to send", select these 3:
    - `checkout.session.completed`
    - `customer.subscription.deleted`
    - `invoice.payment_failed`
16. Click "Add endpoint"
17. On the webhook page, click "Reveal" next to the signing secret. Copy and save it (starts with `whsec_`).

### 1E. Railway (hosts your app online - $5/month)

1. Go to https://railway.app
2. Sign up with your GitHub account (if you don't have GitHub, create one at https://github.com first)
3. That's it for now, we'll come back to Railway later

---

## STEP 2: Set Up the Database (5 minutes)

This creates the tables that store your chatbot's data.

1. Go back to your Supabase project at https://supabase.com/dashboard
2. In the left sidebar, click "SQL Editor" (it looks like a terminal/code icon)
3. You'll see a blank text area where you can type
4. Open the file `scripts/setup_database.sql` from this project folder on your computer
5. Select ALL the text in that file (Command+A on Mac) and copy it (Command+C)
6. Paste it into the Supabase SQL Editor (Command+V)
7. Click the green "Run" button (or press Command+Enter)
8. You should see "Success. No rows returned" - that means it worked!

---

## STEP 3: Configure Your Secret Keys (5 minutes)

1. In this project folder, find the file called `.env.example`
2. Make a copy of it and rename the copy to `.env` (remove the `.example` part)
   - On Mac: Right-click the file > Duplicate, then rename
3. Open `.env` in any text editor (TextEdit works, or you can open it in VS Code)
4. Fill in each value with what you saved from Step 1:

```
SUPABASE_URL=paste-your-supabase-project-url-here
SUPABASE_KEY=paste-your-supabase-anon-key-here
ANTHROPIC_API_KEY=paste-your-anthropic-key-here
VOYAGE_API_KEY=paste-your-voyage-key-here
STRIPE_SECRET_KEY=paste-your-stripe-secret-key-here
STRIPE_WEBHOOK_SECRET=paste-your-stripe-webhook-secret-here
STRIPE_PRICE_ID=paste-your-stripe-price-id-here
APP_SECRET_KEY=type-any-random-long-string-here-like-thriver2026secretkey
APP_URL=http://localhost:8000
```

5. Save the file

---

## STEP 4: Add Your Training Data (10 minutes)

You need to copy your content files into the right folders. Open the `data/` folder inside this project. You'll see 4 subfolders:

### YouTube Transcripts
- Copy your YouTube transcript `.txt` files into `data/transcripts/`

### Discord Coaching Logs
- Copy your Discord export `.csv` files into `data/discord/`
- These are the files from: `CFS-Thriver-AI-Data/1-raw-data/discord-exports/`

### Recovery Playbook
- Copy `Recovery Playbook - JUNIOR DEVELOPMENT.txt` into `data/playbook/`

### Call Extractions
- Copy your call extraction `.csv` files into `data/calls/`
- These are from: `CFS-Thiver-AI-Data/3-processed-data/` (the CSV files in each subfolder)

---

## STEP 5: Install and Run (10 minutes)

You'll need to open Terminal on your Mac. Here's how:

1. Press Command+Space to open Spotlight
2. Type "Terminal" and press Enter
3. A black/white window opens. This is where you type commands.

Now type these commands one at a time, pressing Enter after each:

### Install Python (if you don't have it)
```
brew install python
```
If that doesn't work, download Python from https://www.python.org/downloads/ and install it.

### Go to the project folder
```
cd "/Users/miguelbautista/Desktop/CLAUDE COWORK/CFS RECOVERY - CLAUDE COWORK/cfs-recovery-chatbot"
```

### Install the required packages
```
pip install -r requirements.txt
```
Wait for this to finish (it downloads some code the app needs).

### Load your data into the database
```
python scripts/run_ingestion.py
```
This will take a few minutes. You'll see it processing your files and showing progress. When it says "INGESTION COMPLETE", you're good.

### Start the chatbot locally
```
uvicorn app.main:app --reload --port 8000
```
You should see something like "Uvicorn running on http://0.0.0.0:8000"

### Test it
Open your web browser and go to: http://localhost:8000

You should see the Thriver AI landing page! Try signing up with your email and asking it a question.

Press Control+C in Terminal when you want to stop it.

---

## STEP 6: Put It Online With Railway (10 minutes)

### Push your code to GitHub

1. Go to https://github.com and log in
2. Click the "+" icon in the top right and select "New repository"
3. Name it "thriver-ai" and keep it Private
4. Click "Create repository"
5. Back in Terminal, run these commands:

```
cd "/Users/miguelbautista/Desktop/CLAUDE COWORK/CFS RECOVERY - CLAUDE COWORK/cfs-recovery-chatbot"
git init
git add -A
git commit -m "Initial Thriver AI build"
git branch -M main
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/thriver-ai.git
git push -u origin main
```
Replace YOUR-GITHUB-USERNAME with your actual GitHub username.

### Deploy on Railway

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Find and select your "thriver-ai" repository
5. Railway will start building. While it builds, click on the service
6. Go to the "Variables" tab
7. Add each of these variables (click "+ New Variable" for each one):
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase key
   - `ANTHROPIC_API_KEY` = your Anthropic key
   - `VOYAGE_API_KEY` = your Voyage key
   - `STRIPE_SECRET_KEY` = your Stripe secret key
   - `STRIPE_WEBHOOK_SECRET` = your Stripe webhook secret
   - `STRIPE_PRICE_ID` = your Stripe price ID
   - `APP_SECRET_KEY` = same random string you used in .env
   - `APP_URL` = (leave blank for now, we'll fill this in next)

8. Go to the "Settings" tab
9. Under "Networking", click "Generate Domain"
10. Railway gives you a URL like `thriver-ai-production.up.railway.app`
11. Copy that URL
12. Go back to "Variables" and set `APP_URL` to that full URL (with https://)
13. Also go back to Stripe > Developers > Webhooks and update the endpoint URL to: `https://YOUR-RAILWAY-URL/api/billing/webhook`

Your chatbot is now live at your Railway URL!

---

## STEP 7: Connect Your Custom Domain (Optional)

If you want it at something like `thriverai.cfsrecovery.co`:

1. In Railway, go to Settings > Networking > Custom Domain
2. Type `thriverai.cfsrecovery.co`
3. Railway will show you a CNAME record
4. Go to your domain registrar (wherever you manage cfsrecovery.co)
5. Add a CNAME record pointing `thriverai` to the Railway value
6. Wait 10-30 minutes for it to propagate
7. Update `APP_URL` in Railway variables to `https://thriverai.cfsrecovery.co`
8. Update the Stripe webhook URL too

---

## How to Add New Content Later

When you make new YouTube videos and want to add those transcripts:

1. Save the transcript as a `.txt` file
2. Drop it in the `data/transcripts/` folder
3. Open Terminal and run:
```
cd "/Users/miguelbautista/Desktop/CLAUDE COWORK/CFS RECOVERY - CLAUDE COWORK/cfs-recovery-chatbot"
python scripts/run_ingestion.py
```

---

## Monthly Costs

| Service | Cost |
|---------|------|
| Railway (hosting) | $5/month |
| Supabase (database) | Free |
| Claude API (AI responses) | ~$10-30/month depending on usage |
| Voyage AI (one-time data processing) | ~$2 |
| Stripe (payment processing) | 2.9% + 30 cents per transaction |
| **Total** | **~$15-35/month** |

At $7/month per subscriber, you're profitable after 3-5 subscribers.
