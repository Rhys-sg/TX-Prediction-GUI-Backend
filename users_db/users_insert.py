import sqlite3
import bcrypt

def register_user(name, email, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check if the email already exists
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        # Email already exists
        conn.close()
        return False

    # Hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert user into database
    cursor.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                   (name, email, password_hash.decode('utf-8')))
    conn.commit()

    conn.close()
    return True
