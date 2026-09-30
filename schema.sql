-- createdb jeans   then:   psql -d jeans -f schema.sql

CREATE TABLE IF NOT EXISTS admins (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(80) UNIQUE NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Replaces the old `carsale` (men's) and `womens` tables.
CREATE TABLE IF NOT EXISTS clothes (
    id          SERIAL PRIMARY KEY,
    category    VARCHAR(10) NOT NULL CHECK (category IN ('men', 'women')),
    name        VARCHAR(255) NOT NULL,
    brand       VARCHAR(255),
    size        VARCHAR(10),
    info        TEXT,
    price       NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    image_path  VARCHAR(255) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS wishlist (
    id        SERIAL PRIMARY KEY,
    user_id   INTEGER NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    cloth_id  INTEGER NOT NULL REFERENCES clothes(id) ON DELETE CASCADE,
    added_on  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, cloth_id)
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(255) NOT NULL,
    subject    VARCHAR(255),
    message    TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clothes_category ON clothes(category);
CREATE INDEX IF NOT EXISTS idx_wishlist_user    ON wishlist(user_id);
