import sqlite3

db_path = 'audioplayer.db'


class UserDao:
    def __init__(self):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def save(self, name, login, password):
        query = 'INSERT INTO user(name, login, password) VALUES (?, ?, ?)'
        self.cur.execute(query, (name, login, password))
        self.con.commit()

    def delete(self, id):
        query = 'DELETE FROM user WHERE id = ?'
        self.cur.execute(query, (id,))
        self.con.commit()

    def get(self, login):
        query = 'SELECT * FROM user WHERE login = ?'
        user = self.cur.execute(query, (login,)).fetchone()
        return user

    def get_all(self):
        query = 'SELECT login FROM user'
        users = self.cur.execute(query, ).fetchall()
        return users


class AudiofileDao:
    def __init__(self):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def get(self, id):
        query = 'SELECT * FROM audiofile WHERE id = ?'
        audio = self.cur.execute(query, (id,)).fetchone()
        return audio

    def save(self, user_id, title, author, file_path):
        query = 'INSERT INTO audiofile(user_id, title, author, file_path) VALUES (?, ?, ?, ?)'
        try:
            self.cur.execute(query, (user_id, title, author, file_path))
            self.con.commit()
        except sqlite3.IntegrityError:
            pass

    def delete(self, path):
        query = 'DELETE FROM audiofile WHERE file_path = ?'
        self.cur.execute(query, (path,))
        self.con.commit()

    def get_all(self, user_id):
        query = 'SELECT id, title, author, file_path FROM audiofile'
        return self.cur.execute(query).fetchall()
