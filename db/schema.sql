BEGIN TRANSACTION;
CREATE TABLE tasks (
        id      serial PRIMARY KEY,
        serial  INTEGER,
        type    VARCHAR (128),
        json    TEXT
);
CREATE TABLE IF NOT EXISTS "events" (
        id      serial PRIMARY KEY,
        time    INTEGER NOT NULL,
        event   INTEGER NOT NULL,
        card    TEXT NOT NULL,
        flags   INTEGER
);
CREATE TABLE IF NOT EXISTS "controllers" (
        id      serial PRIMARY KEY,
        serial  INTEGER,
        type    TEXT,
        fw      TEXT,
        conn_fw TEXT,
        active  INTEGER,
        mode    NUMERIC,
        last_conn       INTEGER,
        license TEXT,
        interval        INTEGER NOT NULL DEFAULT 10
);
CREATE TABLE cards (
        id      serial PRIMARY KEY,
        card    TEXT,
        flags   INTEGER,
        tz      INTEGER
);
COMMIT;
