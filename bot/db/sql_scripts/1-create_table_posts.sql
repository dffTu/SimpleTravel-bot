CREATE TABLE IF NOT EXISTS Posts (
    id INTEGER PRIMARY KEY,
    author_ID INTEGER NOT NULL,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    region TEXT NOT NULL,
    photos TEXT NOT NULL,
    contacts TEXT NOT NULL,
    latitude REAL,
    longitude REAL
)
