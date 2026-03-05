-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    trial_start TIMESTAMPTZ DEFAULT NOW(),
    trial_ends TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '3 days'),
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    subscription_status TEXT DEFAULT 'trial',
    personal_question_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Knowledge base chunks
CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    source_type TEXT NOT NULL,
    source_file TEXT,
    category TEXT,
    topic TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_type);
CREATE INDEX IF NOT EXISTS idx_chunks_category ON chunks(category);

-- Daily usage tracking
CREATE TABLE IF NOT EXISTS daily_usage (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    usage_date DATE DEFAULT CURRENT_DATE,
    message_count INTEGER DEFAULT 0,
    UNIQUE(user_id, usage_date)
);

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding VECTOR(1024),
    match_count INT DEFAULT 10,
    match_threshold FLOAT DEFAULT 0.3
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    source_type TEXT,
    source_file TEXT,
    category TEXT,
    topic TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.content,
        c.source_type,
        c.source_file,
        c.category,
        c.topic,
        c.metadata,
        1 - (c.embedding <=> query_embedding) AS similarity
    FROM chunks c
    WHERE 1 - (c.embedding <=> query_embedding) > match_threshold
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
