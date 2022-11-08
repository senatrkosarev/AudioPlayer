import sqlite3

db_path = 'App/audioplayer.db'


class UserDao:
    def __init__(self):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def save(self, name, login, password):
        query = 'INSERT INTO user(name, login, password) VALUES (?, ?, ?)'
        self.cur.execute(query, (name, login, password))
        self.con.commit()

    def get(self, login):
        query = 'SELECT * FROM user WHERE login = ?'
        user = self.cur.execute(query, (login,)).fetchone()
        return user


class AudiofileDao:
    def __init__(self):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def save(self, user_id, title, author, file_path):
        query = 'INSERT INTO audiofile(user_id, title, author, file_path) VALUES (?, ?, ?, ?)'
        try:
            self.cur.execute(query, (user_id, title, author, file_path))
            self.con.commit()
        except sqlite3.IntegrityError:
            pass

    def get_all(self, user_id):
        query = 'SELECT id, title, author, file_path FROM audiofile WHERE user_id = ?'
        return self.cur.execute(query, (user_id,)).fetchall()

    def delete(self, path):
        query = 'DELETE FROM audiofile WHERE file_path = ?'
        self.cur.execute(query, (path,))
        self.con.commit()
