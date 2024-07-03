import sqlite3

def insert_main_data(coding_strand, observed_tx_rate, notes):
    conn = sqlite3.connect('observed_TX.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO MainData (CodingStrand, ObservedTXRate, Notes)
    VALUES (?, ?, ?)
    ''', (coding_strand, observed_tx_rate, notes))

    conn.commit()
    input_id = cursor.lastrowid
    conn.close()
    return input_id

def insert_student(input_id, first_name, last_name, email_address):
    conn = sqlite3.connect('observed_TX.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO Students (InputID, FirstName, LastName, EmailAddress)
    VALUES (?, ?, ?, ?)
    ''', (input_id, first_name, last_name, email_address))

    conn.commit()
    conn.close()
