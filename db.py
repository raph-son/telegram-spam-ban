import sqlite3

conn = sqlite3.connect("sqlite.db")

def create():
	conn.execute("""CREATE TABLE tags
         (tag TEXT NOT NULL);""")
	conn.close()

def insert(data):
	for value in data:
		command = """INSERT INTO tags (tag) VALUES (?);"""
		q = (value,)
		conn.execute(command, q)
		conn.commit()

def select():
	cursor = conn.execute("SELECT tag from tags")
	return cursor

def close():
	conn.close()

def main():
	create()

if __name__ == '__main__':
	main()