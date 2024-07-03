import sqlite3

def print_all_entries():
    conn = sqlite3.connect('observed_TX.db')
    cursor = conn.cursor()

    cursor.execute('''
    SELECT 
        md.InputID,
        md.CodingStrand,
        md.ObservedTXRate,
        md.Notes,
        s.FirstName,
        s.LastName,
        s.EmailAddress
    FROM 
        MainData md
    LEFT JOIN 
        Students s ON md.InputID = s.InputID
    ORDER BY 
        md.InputID, s.StudentID
    ''')

    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        print(f"InputID: {row[0]}, CodingStrand: {row[1]}, ObservedTXRate: {row[2]}, Notes: {row[3]}, FirstName: {row[4]}, LastName: {row[5]}, EmailAddress: {row[6]}")
