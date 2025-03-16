CREATE TABLE IF NOT EXISTS Bookings (
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (post_id) REFERENCES Posts(id),
    FOREIGN KEY (user_id) REFERENCES Users(chat_id),
    UNIQUE(post_id, user_id)
)
