CREATE TABLE IF NOT EXISTS Users (
    chat_id INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    email TEXT NOT NULL,
    is_moderator INTEGER NOT NULL DEFAULT 0
)
