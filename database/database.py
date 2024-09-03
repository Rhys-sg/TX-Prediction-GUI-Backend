import sqlite3
import bcrypt
import os
import time

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS school (
                name TEXT PRIMARY KEY,
                domain TEXT UNIQUE
            )''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS term (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                school TEXT,
                FOREIGN KEY(school) REFERENCES school(name)
            )''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ligation_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_id INTEGER,
                order_name TEXT,
                sequence TEXT,
                date TEXT,
                students TEXT,
                FOREIGN KEY(term_id) REFERENCES term(id)
            )''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                email TEXT PRIMARY KEY,
                school TEXT,
                first_name TEXT,
                last_name TEXT,
                password TEXT,
                FOREIGN KEY(school) REFERENCES school(name)
            )''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS observations (
                observations_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence TEXT,
                account_email TEXT,
                observed_TX INTEGER,
                students TEXT,
                notes TEXT,
                date TEXT,
                FOREIGN KEY(account_email) REFERENCES accounts(email)
            )''')

    def close(self):
        self.conn.close()

    def execute_with_retry(self, query, params=(), retries=5):
        for attempt in range(retries):
            try:
                with self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute(query, params)
                    return cursor
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    time.sleep(0.1)  # Wait a bit before retrying
                else:
                    raise
        raise sqlite3.OperationalError("database is locked")

    def insert_school(self, name, domain):
        try:
            self.execute_with_retry('INSERT INTO school (name, domain) VALUES (?, ?)', (name, domain))
            return True
        except sqlite3.IntegrityError:
            return False

    def query_schools_domains(self):
        cursor = self.execute_with_retry('SELECT name, domain FROM school')
        return cursor.fetchall()

    def query_schools(self):
        cursor = self.execute_with_retry('SELECT name FROM school')
        results = cursor.fetchall()
        return [row[0] for row in results]
    
    def query_domains(self):
        cursor = self.execute_with_retry('SELECT domain FROM school')
        results = cursor.fetchall()
        return [row[0] for row in results]

    def query_school_by_domain(self, domain):
        cursor = self.execute_with_retry('SELECT name FROM school WHERE domain = ?', (domain,))
        result = cursor.fetchone()
        return result[0] if result else None

    def insert_term(self, term_name, school_name):
        # Check if the term already exists for the school
        cursor = self.execute_with_retry('SELECT id FROM term WHERE name = ? AND school = ?', (term_name, school_name))
        term_row = cursor.fetchone()
        if term_row: return False
        try:
            self.execute_with_retry('INSERT INTO term (name, school) VALUES (?, ?)', (term_name, school_name))
            return True
        except sqlite3.IntegrityError:
            return False

    
    def query_terms_by_school(self, school_name):
        cursor = self.execute_with_retry('SELECT name FROM term WHERE school = ?', (school_name,))
        return [row[0] for row in cursor.fetchall()]
    
    def insert_ligation_order(self, school_name, term_name, order_name, sequence, date, students):
        try:
            cursor = self.execute_with_retry('SELECT id FROM term WHERE name = ? AND school = ?', (term_name, school_name))
            term_row = cursor.fetchone()
            
            if term_row is None:
                return False
            
            term_id = term_row[0]
            
            self.execute_with_retry('''
                INSERT INTO ligation_orders (term_id, order_name, sequence, date, students)
                VALUES (?, ?, ?, ?, ?)
            ''', (term_id, order_name, sequence, date, students))
            
            return True
        
        except sqlite3.IntegrityError:
            return False

    def query_ligation_orders_by_school_and_term(self, school_name, term_name):
        cursor = self.execute_with_retry('''
            SELECT lo.order_name, lo.sequence, lo.date, lo.students
            FROM ligation_orders lo
            INNER JOIN term t ON lo.term_id = t.id
            WHERE t.name = ? AND t.school = ?
        ''', (term_name, school_name))
        return cursor.fetchall()
    
    def insert_account(self, email, school_name, first_name, last_name, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            self.execute_with_retry('''
                INSERT INTO accounts (email, school, first_name, last_name, password)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, school_name, first_name, last_name, hashed_password))
            return True
        except sqlite3.IntegrityError:
            return False
    
    def insert_observation(self, sequence, account_email, observed_TX, students, notes, date):
        try:
            self.execute_with_retry('''
                INSERT INTO observations (sequence, account_email, observed_TX, students, notes, date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (sequence, account_email, observed_TX, students, notes, date))
            return True
        except sqlite3.IntegrityError:
            return False
    
    def query_observations_by_sequence(self, sequence):
        cursor = self.execute_with_retry('''
            SELECT account_email, observed_TX, students, notes, date
            FROM observations
            WHERE sequence = ?
        ''', (sequence,))
        return cursor.fetchall()
    
    def query_average_observed_TX_by_sequence(self, sequence):
        cursor = self.execute_with_retry('SELECT AVG(observed_TX) FROM observations WHERE sequence = ?', (sequence,))
        result = cursor.fetchone()
        return result[0] if result else None

    
    def query_accounts(self):
        cursor = self.execute_with_retry('SELECT email, password FROM accounts')
        return cursor.fetchall()
    
    def login_account(self, email, password):
        cursor = self.execute_with_retry('SELECT password FROM accounts WHERE email = ?', (email,))
        result = cursor.fetchone()
        if result is None: return False
        stored_password = result[0]
        return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
    
    def query_first_name_by_email(self, email):
        cursor = self.execute_with_retry('SELECT first_name FROM accounts WHERE email = ?', (email,))
        result = cursor.fetchone()
        return result[0] if result else None
        
    def query_last_name_by_email(self, email):
        cursor = self.execute_with_retry('SELECT last_name FROM accounts WHERE email = ?', (email,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def delete_database(self):
        self.conn.close()
        try:
            os.remove(self.db_name)
            return True
        except FileNotFoundError:
            return False