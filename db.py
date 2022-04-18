import sqlite3

class DB():
	def __init__(self):
		self.conn = sqlite3.connect("sqlite.db", check_same_thread=False)

	def create(self):
		conn = self.conn
		conn.execute("""CREATE TABLE tags
			(tag TEXT NOT NULL PRIMARY KEY);""")
		conn.execute("""CREATE TABLE users
			(id TEXT NOT NULL PRIMARY KEY,
			username TEXT NOT NULL);""")
		conn.close()

	def insert(self, data, table, column):
		conn = self.conn
		command = f"""INSERT OR IGNORE INTO {table} ({column}) VALUES (?);"""
		q = (data,)
		conn.execute(command, q)
		conn.commit()

	def insert_users(self, id, username):
		conn = self.conn
		command = f"""INSERT OR IGNORE INTO users (id, username) VALUES (?, ?);"""
		q = (id, username)
		conn.execute(command, q)
		conn.commit()

	def remove(self, id):
		conn = self.conn
		conn.execute("DELETE FROM users WHERE id=?", (id, ))
		conn.commit()

	def remove_tag(self, tag):
		conn = self.conn
		conn.execute("DELETE FROM tags WHERE tag=?", (tag, ))
		conn.commit()

	def select(self, table, column):
		conn = self.conn
		cursor = conn.execute(f"SELECT {column} from {table}").fetchall()
		return cursor

	def select_users(self, username):
		conn = self.conn
		cursor = conn.execute(f"SELECT id from users WHERE username=?", (username, )).fetchone()
		return cursor

	def select_tag(self, tag):
		conn = self.conn
		cursor = conn.execute(f"SELECT tag from tags WHERE tag=?", (tag, )).fetchone()
		return cursor

	def close(self):
		self.conn.close()

def main():
	db = DB()
	db.create()
	db.close()

if __name__ == '__main__':
	main()
