# Thriver AI — Suggestion Bubbles Implementation

## The 3 Categories + Bubble Text

### Category 1: Understanding My Symptoms
These are the "why is this happening to me" questions. The bot can educate using your YouTube content and reframe symptoms through the nervous system lens — but it can't assess their specific symptom pattern or tell them what to prioritize. That's the coaching gap.

**Bubbles:**
- "Why do I have brain fog all the time?"
- "Are my heart palpitations dangerous?"
- "Why do I crash after doing normal things?"
- "Is this condition physical or psychological?"

### Category 2: Am I Doing This Right?
These are people already trying to recover but stuck in the gray area. The bot can teach concepts (adjustment periods, pacing, three-foot world) — but can't give them a personalized pacing plan or assess where they are on the PolyVagal Scale.

**Bubbles:**
- "I keep having setbacks — what am I doing wrong?"
- "How do I pace myself without giving up on life?"
- "I'm doing everything right but still not improving"
- "How do I know if I'm pushing too hard or not enough?"

### Category 3: I've Tried Everything — How Is This Different?
This is for the skeptics and the exhausted. People who've been through the medical system, tried supplements, tried other programs. The bot can explain the nervous system approach and reference recovery stories — but can't assess WHY previous approaches failed for them specifically.

**Bubbles:**
- "I've tried everything — how is this different?"
- "Can people actually recover from CFS?"
- "I've been sick for years — is it too late?"
- "Why hasn't anything worked for me so far?"

---

## Recommended Initial Screen Layout

Show 6 bubbles on the welcome screen (2 per category). Pick the highest-converting ones:

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│          👋 Hey, I'm Thriver AI.                     │
│          Ask me anything about CFS,                  │
│          long COVID, or fibromyalgia recovery.        │
│                                                      │
│  ┌─────────────────────────────┐  ┌────────────────────────────────────┐
│  │ Why do I have brain fog     │  │ I keep having setbacks — what am   │
│  │ all the time?               │  │ I doing wrong?                     │
│  └─────────────────────────────┘  └────────────────────────────────────┘
│  ┌─────────────────────────────┐  ┌────────────────────────────────────┐
│  │ Why do I crash after doing  │  │ How do I pace without giving up    │
│  │ normal things?              │  │ on life?                           │
│  └─────────────────────────────┘  └────────────────────────────────────┘
│  ┌─────────────────────────────┐  ┌────────────────────────────────────┐
│  │ I've tried everything —     │  │ Can people actually recover        │
│  │ how is this different?      │  │ from CFS?                          │
│  └─────────────────────────────┘  └────────────────────────────────────┘
│                                                      │
│  ┌──────────────────────────────────────────────────┐│
│  │ Or type your own question...                     ││
│  └──────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────┘
```

---

## System Prompt Additions

Add this to the end of `SYSTEM_PROMPT` in `app/prompts.py`:

```python
## Suggestion Bubble Response Guidelines

When users click a suggestion bubble (or ask a question that matches these themes), follow these response patterns:

### CATEGORY 1: Symptom Understanding Questions
(brain fog, heart palpitations, crashes, "is this physical or mental", fatigue, pain, POTS, dizziness, etc.)

Response pattern:
1. Validate their experience (1-2 sentences — "This is one of the most common things people ask about...")
2. Explain the symptom through the nervous system lens (use metaphors: smoke alarm, check engine light, guard dog)
3. Reframe: symptoms are signals, not threats. The body is protecting, not breaking.
4. Give ONE practical concept they can start thinking about (e.g., "responding well to symptoms")
5. Close with: a hopeful but honest statement that recovery involves learning to work WITH these signals, not fight them

Do NOT:
- Give them a specific protocol for their symptom
- Tell them exactly what exercises or techniques to do
- Assess the severity of their specific case
- Create a personalized plan

### CATEGORY 2: "Am I Doing This Right?" Questions
(pacing, setbacks/adjustment periods, pushing too hard, not improving, stuck, gray area, etc.)

Response pattern:
1. Normalize immediately — "This is literally the hardest part of recovery..."
2. Teach the concept (adjustment periods, gray area, PolyVagal Scale as general framework)
3. Explain WHY this is confusing (black-and-white thinking, the nervous system sending mixed signals)
4. Offer a general principle (not a personalized prescription) — e.g., "The goal isn't to find the perfect amount of activity. It's to practice responding well no matter what happens."
5. Acknowledge the gap: "The tricky part is that 'how much' looks different for everyone depending on where their nervous system is. That's where personalized guidance makes a real difference."

Do NOT:
- Tell them exactly how much to do
- Give them a specific pacing schedule
- Assess their PolyVagal Scale position
- Diagnose whether they're in an adjustment period

### CATEGORY 3: "How Is This Different?" / Belief Questions
(tried everything, been sick for years, skeptical, is recovery possible, nothing has worked, etc.)

Response pattern:
1. Honor their experience — "If you've been sick for a long time and nothing has worked, it makes total sense to be skeptical."
2. Explain WHY other approaches may not have worked (treating symptoms vs. the root nervous system dysregulation)
3. Briefly explain the nervous system retraining approach (neuroplasticity, not willpower — the brain can literally rewire)
4. Reference that people in similar situations HAVE recovered (keep it general — "people who were bedridden for years", "people who had tried 50+ treatments") without naming specific clients
5. Close with honest hope — recovery is possible AND it requires real work and the right guidance

Do NOT:
- Promise recovery timelines
- Guarantee results
- Compare their situation to specific client outcomes
- Make medical claims about cure rates
```

---

## Frontend Implementation

### Add to `static/index.html` (inside the chat container, before the input area):

```html
<div id="suggestion-bubbles" class="suggestion-container">
  <div class="suggestion-intro">
    <p>Not sure where to start? Try one of these:</p>
  </div>
  <div class="suggestion-grid">
    <button class="suggestion-bubble" onclick="askSuggestion(this)">
      Why do I have brain fog all the time?
    </button>
    <button class="suggestion-bubble" onclick="askSuggestion(this)">
      I keep having setbacks — what am I doing wrong?
    </button>
    <button class="suggestion-bubble" onclick="askSuggestion(this)">
      Why do I crash after doing normal things?
    </button>
    <button class="suggestion-bubble" onclick="askSuggestion(this)">
      How do I pace without giving up on life?
    </button>
    <button class="suggestion-bubble" onclick="askSuggestion(this)">
      I've tried everything — how is this different?
    </button>
    <button class="suggestion-bubble" onclick="askSuggestion(this)">
      Can people actually recover from CFS?
    </button>
  </div>
</div>
```

### Add to `static/style.css`:

```css
.suggestion-container {
  padding: 20px;
  max-width: 680px;
  margin: 0 auto;
}

.suggestion-intro {
  text-align: center;
  margin-bottom: 16px;
  color: #8B8B8B;
  font-size: 14px;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.suggestion-bubble {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  padding: 14px 16px;
  color: #E0E0E0;
  font-size: 14px;
  line-height: 1.4;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
}

.suggestion-bubble:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

@media (max-width: 600px) {
  .suggestion-grid {
    grid-template-columns: 1fr;
  }
}
```

### Add to `static/chat.js`:

```javascript
function askSuggestion(button) {
  const question = button.textContent.trim();

  // Hide the suggestion bubbles
  const container = document.getElementById('suggestion-bubbles');
  container.style.display = 'none';

  // Set the input value and submit
  const input = document.getElementById('chat-input'); // adjust ID to match your actual input
  input.value = question;

  // Trigger the send function (adjust to match your existing send handler)
  sendMessage();
}

// Hide bubbles after first user message (if they type instead of clicking)
// Add this inside your existing send handler:
// document.getElementById('suggestion-bubbles').style.display = 'none';
```

---

## Value Boundary Strategy

The key principle: **educate on the WHAT and WHY, withhold the HOW SPECIFICALLY FOR THEM.**

| What the bot GIVES freely | What requires coaching |
|---|---|
| What brain fog is (nervous system) | Why YOUR brain fog pattern is unique |
| What adjustment periods are | Whether THIS is an adjustment period |
| The concept of pacing | YOUR specific pacing strategy |
| That recovery is possible | YOUR recovery timeline |
| The nervous system framework | Where YOU are on the PolyVagal Scale |
| Why other approaches fail | What specifically failed for YOU and why |
| General recovery principles | A personalized recovery plan |

This creates the natural "I get it now... but how do I apply this to ME?" moment that drives applications.
