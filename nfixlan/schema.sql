DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS watch_history;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE watch_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  seek_position FLOAT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);