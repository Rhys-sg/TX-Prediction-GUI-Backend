import sqlite3

def create_tables():
    conn = sqlite3.connect('observed_TX.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS MainData (
        InputID INTEGER PRIMARY KEY AUTOINCREMENT,
        CodingStrand TEXT NOT NULL,
        ObservedTXRate REAL,
        Notes TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Students (
        StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
        InputID INTEGER,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        EmailAddress TEXT NOT NULL,
        FOREIGN KEY (InputID) REFERENCES MainData(InputID)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
