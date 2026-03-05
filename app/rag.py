import json
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
import anthropic
import voyageai

from app.config import ANTHROPIC_API_KEY, VOYAGE_API_KEY, SUPABASE_URL, SUPABASE_KEY, DAILY_MESSAGE_LIMIT
from app.auth import get_user_from_token, check_access, get_daily_usage, increment_usage
from app.safety import check_crisis, check_out_of_scope
from app.upsell import check_upsell
from app.prompts import SYSTEM_PROMPT
from app.models import ChatRequest
from supabase import create_client

router = APIRouter()
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
voyage_client = voyageai.Client(api_key=VOYAGE_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def embed_query(text: str) -> list[float]:
    result = voyage_client.embed([text], model="voyage-3", input_type="query")
    return result.embeddings[0]


def search_chunks(query_embedding: list[float], match_count: int = 10) -> list[dict]:
    result = supabase.rpc("match_chunks", {
        "query_embedding": query_embedding,
        "match_count": match_count,
        "match_threshold": 0.3,
    }).execute()
    return result.data or []


def build_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant context found in the knowledge base."

    context_parts = []
    for chunk in chunks:
        source = chunk.get("source_type", "unknown")
        category = chunk.get("category", "")
        topic = chunk.get("topic", "")
        label_parts = [f"[{source}]"]
        if category:
            label_parts.append(f"[{category}]")
        if topic:
            label_parts.append(f"[{topic}]")
        label = " ".join(label_parts)
        context_parts.append(f"{label}\n{chunk['content']}")

    return "\n\n---\n\n".join(context_parts)


@router.post("/chat")
async def chat(request: ChatRequest, authorization: str = Header(None)):
    user = get_user_from_token(authorization)

    access = check_access(user)
    if access != "active":
        raise HTTPException(status_code=403, detail=access)

    usage = get_daily_usage(user["id"])
    if usage >= DAILY_MESSAGE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="daily_limit",
        )

    # Safety checks before RAG
    crisis_result = check_crisis(request.message)
    crisis_prefix = None
    if crisis_result:
        if crisis_result["hard_stop"]:
            increment_usage(user["id"])
            return StreamingResponse(
                iter([f"data: {json.dumps({'text': crisis_result['response'], 'done': True})}\n\n"]),
                media_type="text/event-stream",
            )
        else:
            # Soft crisis: prepend resources, then continue with RAG response
            crisis_prefix = crisis_result["response"]

    scope_response = check_out_of_scope(request.message)
    if scope_response:
        increment_usage(user["id"])
        return StreamingResponse(
            iter([f"data: {json.dumps({'text': scope_response, 'done': True})}\n\n"]),
            media_type="text/event-stream",
        )

    # Check for upsell
    upsell_message = check_upsell(user["id"], request.message)

    # RAG: embed query, search, build context
    query_embedding = embed_query(request.message)
    chunks = search_chunks(query_embedding)
    context = build_context(chunks)

    # Build messages for Claude
    messages = []

    # Add session history (current session only, sent from frontend)
    for msg in request.session_messages[-10:]:  # Last 10 messages for context
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Add current message with context
    user_message = f"""Here is relevant context from CFS Recovery's knowledge base:

{context}

---

User question: {request.message}"""

    messages.append({"role": "user", "content": user_message})

    increment_usage(user["id"])
    new_usage = usage + 1

    async def generate():
        try:
            # If soft crisis detected, prepend resources before the AI response
            if crisis_prefix:
                yield f"data: {json.dumps({'text': crisis_prefix})}\n\n"

            with anthropic_client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {json.dumps({'text': text})}\n\n"

            # After response, append upsell if triggered
            if upsell_message:
                yield f"data: {json.dumps({'upsell': upsell_message})}\n\n"

            yield f"data: {json.dumps({'done': True, 'messages_remaining': DAILY_MESSAGE_LIMIT - new_usage})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
