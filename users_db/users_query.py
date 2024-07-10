import sqlite3
import bcrypt

def login_user(email, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT first_name, last_name, password_hash FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()

    if row:
        first_name, last_name, stored_hash = row
        stored_hash = stored_hash.encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return first_name, last_name
        else:
            return None, None
    else:
        return None, None