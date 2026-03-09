CREATE DATABASE etl_warehouse;

\c etl_warehouse;

-- 1. Сессии пользователей
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    pages_visited TEXT[],
    device VARCHAR(20),
    actions TEXT[],
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Логи событий
CREATE TABLE IF NOT EXISTS event_logs (
    event_id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    details JSONB,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Обращения в поддержку
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    issue_type VARCHAR(50) NOT NULL,
    messages JSONB,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Рекомендации
CREATE TABLE IF NOT EXISTS user_recommendations (
    user_id VARCHAR(50) PRIMARY KEY,
    recommended_products TEXT[],
    last_updated TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Очередь модерации
CREATE TABLE IF NOT EXISTS moderation_queue (
    review_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    review_text TEXT,
    rating INTEGER,
    moderation_status VARCHAR(20) NOT NULL,
    flags TEXT[],
    submitted_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_start_time ON user_sessions(start_time);
CREATE INDEX idx_event_logs_timestamp ON event_logs(timestamp);
CREATE INDEX idx_support_tickets_user_id ON support_tickets(user_id);
CREATE INDEX idx_support_tickets_status ON support_tickets(status);
CREATE INDEX idx_moderation_queue_status ON moderation_queue(moderation_status);