DROP TABLE IF EXISTS audiofile;
DROP TABLE IF EXISTS user;

CREATE TABLE audiofile
(
    id        INTEGER NOT NULL
        PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER NOT NULL
        REFERENCES user,
    title     TEXT    NOT NULL,
    author    TEXT    NOT NULL,
    file_path TEXT    NOT NULL,
    UNIQUE (
            user_id,
            file_path
        )
);

CREATE TABLE user
(
    id       INTEGER PRIMARY KEY AUTOINCREMENT
                  NOT NULL,
    name     TEXT NOT NULL,
    login    TEXT UNIQUE
                  NOT NULL,
    password TEXT NOT NULL
);
