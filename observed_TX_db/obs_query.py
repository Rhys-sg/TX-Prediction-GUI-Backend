import sqlite3

def query_by_coding_strand(coding_strand):
    conn = sqlite3.connect('observed_TX.db')
    cursor = conn.cursor()

    cursor.execute('''
    SELECT 
        md.InputID,
        md.CodingStrand,
        md.ObservedTXRate,
        md.notes,
        s.FirstName,
        s.LastName,
        s.EmailAddress
    FROM 
        MainData md
    LEFT JOIN 
        Students s ON md.InputID = s.InputID
    WHERE 
        md.CodingStrand = ?
    ''', (coding_strand,))

    rows = cursor.fetchall()
    conn.close()
    return rows
