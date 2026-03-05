# Feature Spec: Saved Reframes + Conversation Continuity

## Current Architecture (for reference)

- **Backend:** FastAPI (app/main.py, app/rag.py)
- **Database:** Supabase (PostgreSQL)
- **AI:** Anthropic Claude Sonnet (streaming), Voyage AI embeddings
- **Auth:** HMAC token, users table with subscription/trial status
- **Frontend:** Vanilla JS (static/chat.js, static/index.html)
- **Session history:** Last 10 messages sent from frontend per request, NOT persisted server-side

---

## Feature 1: Save a Reframe

### What it does

Users can tap a heart/bookmark icon on any bot message to save it. Saved messages appear in a "My Reframes" section they can access anytime, like a personal recovery reference library built from their own conversations.

### Why it matters

People with brain fog forget what helped. At 2am when they're spiraling, they can pull up the exact message that calmed them down last week. It makes the app their safety net.

### Database

Add one new table in Supabase:

```sql
CREATE TABLE saved_reframes (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  message_text TEXT NOT NULL,
  conversation_context TEXT,  -- the user's question that prompted this response
  saved_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_saved_reframes_user ON saved_reframes(user_id);
```

### API Endpoints

Add a new file: `app/reframes.py`

```
POST /api/reframes/save
  Body: { message_text: string, conversation_context: string }
  Auth: Bearer token
  Returns: { id, saved_at }

GET /api/reframes
  Auth: Bearer token
  Returns: [ { id, message_text, conversation_context, saved_at } ]

DELETE /api/reframes/{id}
  Auth: Bearer token
  Returns: { success: true }
```

### Backend Code (app/reframes.py)

```python
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY
from app.auth import get_user_from_token

router = APIRouter()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class SaveReframeRequest(BaseModel):
    message_text: str
    conversation_context: str = ""


@router.post("/save")
async def save_reframe(request: SaveReframeRequest, authorization: str = Header(None)):
    user = get_user_from_token(authorization)
    result = supabase.table("saved_reframes").insert({
        "user_id": user["id"],
        "message_text": request.message_text,
        "conversation_context": request.conversation_context,
    }).execute()
    return result.data[0]


@router.get("/")
async def list_reframes(authorization: str = Header(None)):
    user = get_user_from_token(authorization)
    result = (
        supabase.table("saved_reframes")
        .select("*")
        .eq("user_id", user["id"])
        .order("saved_at", desc=True)
        .execute()
    )
    return result.data or []


@router.delete("/{reframe_id}")
async def delete_reframe(reframe_id: int, authorization: str = Header(None)):
    user = get_user_from_token(authorization)
    supabase.table("saved_reframes").delete().eq("id", reframe_id).eq("user_id", user["id"]).execute()
    return {"success": True}
```

Register in `app/main.py`:
```python
from app.reframes import router as reframes_router
app.include_router(reframes_router, prefix="/api/reframes")
```

### Frontend

**On every bot message bubble, add a small heart/bookmark icon (bottom right).**

When tapped:
1. Icon fills in (visual feedback, saved state)
2. POST to /api/reframes/save with the message text + the user's preceding question as context
3. Show a brief toast: "Saved to My Reframes"

When tapped again on an already-saved message:
1. Icon unfills
2. DELETE to /api/reframes/{id}

**Add a "My Reframes" tab/page accessible from the header or a sidebar icon.**

Layout:
- List of saved messages, most recent first
- Each card shows the bot's message + a smaller line showing the user's original question
- Tap to expand, long-press or swipe to delete
- Search/filter if they have more than 10 saved

### Lovable Prompt for Save a Reframe

```
Add a small heart icon to the bottom-right corner of every bot message bubble.
When tapped, the heart fills in and the message is saved. When tapped again,
it unfills and the message is unsaved.

Add a "My Reframes" page accessible from a small bookmark icon in the header
bar. This page shows all saved messages in a scrollable list, most recent
first. Each saved item shows the bot's message as the main text, and the
user's question that prompted it in smaller muted text above. Include a
delete option (small X or swipe to delete) on each saved item.

The page should feel warm and personal, like a recovery journal. If there
are no saved reframes yet, show a gentle empty state: "Nothing saved yet.
Tap the heart on any message that helps you to save it here."
```

---

## Feature 2: Conversation Continuity

### What it does

The bot remembers what you talked about in past sessions. When you come back, it can reference previous conversations: "Last time you mentioned the good days/bad days cycle. How's that been going?"

### Why it matters

This is the difference between a chatbot and a relationship. People come back because it feels like someone who knows them. Without this, every session starts cold and they have to re-explain everything.

### How it works (architecture)

**The problem:** Storing and sending full conversation history is expensive (tokens) and slow. A user who's had 20 sessions could have 200+ messages.

**The solution:** Conversation summaries. At the end of each session, generate a short summary of key themes, reframes that landed, and open threads. On the next session, inject the last 2-3 summaries into the system prompt. This gives Claude the "memory" without blowing up the context window.

### Database

Two new tables:

```sql
-- Store every conversation session
CREATE TABLE conversations (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  message_count INT DEFAULT 0,
  summary TEXT,  -- AI-generated summary, filled when session ends
  key_themes TEXT[],  -- tags like ['adjustment_periods', 'pacing', 'brain_fog']
  status TEXT DEFAULT 'active'  -- 'active' or 'completed'
);

CREATE INDEX idx_conversations_user ON conversations(user_id);

-- Store individual messages for context (and potential future features)
CREATE TABLE messages (
  id BIGSERIAL PRIMARY KEY,
  conversation_id BIGINT REFERENCES conversations(id) ON DELETE CASCADE,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL,  -- 'user' or 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_user ON messages(user_id);
```

### Session Lifecycle

**1. Session Start (user opens chat or sends first message)**
- Check for an active conversation for this user
- If none exists (or last one is > 30 min old), create a new conversation
- Load the last 2-3 conversation summaries for this user

**2. During Session (every message)**
- Save both user and assistant messages to the messages table
- Update conversation.message_count

**3. Session End (30 min inactivity or user closes tab)**
- Trigger a summary generation call to Claude
- Save summary + key_themes to the conversation record
- Mark conversation as 'completed'

### Summary Generation

When a session ends, make a separate API call to Claude to generate a summary:

```python
SUMMARY_PROMPT = """Summarize this conversation in 2-3 sentences for future reference.
Focus on:
- What the user was struggling with
- Key concepts or reframes that resonated with them
- Any action items or "one small things" they committed to
- Open threads (things they might want to follow up on)

Also provide 1-3 key theme tags from this list:
adjustment_periods, pacing, brain_fog, fatigue, anxiety, sleep,
good_days_bad_days, gray_area, responding_to_symptoms, skepticism,
flare_ups, exercise, work, relationships, fear, hope, progress

Format:
SUMMARY: [2-3 sentence summary]
THEMES: [comma-separated tags]
"""
```

### Injecting Memory into New Sessions

When a new session starts, load the last 2-3 summaries and prepend them to the system prompt:

```python
def build_memory_context(user_id: int) -> str:
    result = (
        supabase.table("conversations")
        .select("summary, key_themes, ended_at")
        .eq("user_id", user_id)
        .eq("status", "completed")
        .not_.is_("summary", "null")
        .order("ended_at", desc=True)
        .limit(3)
        .execute()
    )

    if not result.data:
        return ""

    memory_parts = []
    for conv in reversed(result.data):  # chronological order
        date = conv["ended_at"][:10]  # just the date
        memory_parts.append(f"[{date}] {conv['summary']}")

    return (
        "## What You Know About This Person\n\n"
        "You've talked with this person before. Here's what you know from "
        "previous conversations. Use this to personalize your responses, "
        "reference past discussions naturally, and check in on things they "
        "mentioned before. Don't force it, just weave it in when relevant.\n\n"
        + "\n\n".join(memory_parts)
    )
```

Then in the chat endpoint, inject it:

```python
memory_context = build_memory_context(user["id"])
full_system_prompt = SYSTEM_PROMPT
if memory_context:
    full_system_prompt = SYSTEM_PROMPT + "\n\n" + memory_context
```

### API Changes

**Modified: POST /api/chat** (in rag.py)
- Create or retrieve active conversation
- Save user message to messages table
- Save assistant response to messages table (after streaming completes)
- Inject memory context into system prompt

**New: POST /api/conversations/end** (called from frontend on tab close or inactivity)
- Triggers summary generation
- Marks conversation as completed

**New: GET /api/conversations/history** (optional, for a "Past Conversations" view)
- Returns list of past conversations with summaries

### Frontend Changes

**Session tracking:**
- On first message, call the backend to create/retrieve a conversation
- Store conversation_id in JS state
- On tab close (beforeunload) or 30 min inactivity, call /api/conversations/end

**Opening message:**
- If the user has past conversations, the bot's welcome message can reference them
- Backend returns a flag: `has_history: true` and the latest summary
- Welcome message changes from "Hey, what's on your mind?" to something like:
  "Welcome back. Last time we talked about [theme]. How have things been going?"

### Lovable Prompt for Conversation Continuity

```
When a returning user opens the chat, instead of the default welcome
message, show a personalized welcome that references their last
conversation. For example: "Welcome back. Last time we talked about
pacing and the good days/bad days cycle. How have things been going
since then?"

If it's a brand new user with no history, show the normal welcome
screen with suggestion bubbles.

Add a subtle "Past Conversations" link in the header that opens a
simple list of previous sessions showing the date and a 1-2 sentence
summary of what was discussed. Tapping one opens a read-only view of
that conversation.
```

---

## Implementation Priority

### Phase 1 (Build First): Message Persistence + Saved Reframes
These are simpler and immediately valuable:
1. Add the messages and conversations tables
2. Start saving messages to DB on every chat
3. Build the saved reframes feature (heart icon + My Reframes page)
4. This gives you data to work with for Phase 2

### Phase 2 (Build Second): Conversation Continuity
Depends on Phase 1 being in place:
1. Add the summary generation on session end
2. Build the memory injection into the system prompt
3. Update the welcome experience for returning users
4. Add the past conversations view

### Estimated Costs

- **Supabase:** Still free tier (these tables are tiny)
- **Claude API for summaries:** ~$0.003 per summary (100 tokens in, 200 out on Haiku)
  - Use claude-haiku for summaries to keep costs minimal
  - At 100 active users doing 1 session/day = $9/month
- **Token overhead for memory injection:** ~200-300 extra tokens per request
  - Negligible cost increase

---

## Token Budget Note

The current system prompt is ~2,500 tokens. With memory context (3 summaries at ~100 tokens each), you'd add ~300 tokens. RAG context chunks add another ~1,000-2,000. User messages (last 10) add ~500-1,000. Total per request: ~4,500-6,000 tokens input. Well within Claude's context window and keeps costs manageable.
