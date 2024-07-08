import sqlite3
import bcrypt

def login_user(email, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT password_hash FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()

    if row:
        stored_hash = row[0].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True
        else:
            return False
    else:
        return False