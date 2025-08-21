import sqlite3

DB_PATH = None

def set_db_path(db_path):
    global DB_PATH
    DB_PATH = db_path

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMAY KEY AUTO INCREMENT,
                     email TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL
                     )
        ''')

def add_user(email, hashed_password):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    
def get_user_password(email):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT password FROM users WHERE email = ?", (email))
        user = cursor.fetchone()
        if user:
            return user[0]
        return None
