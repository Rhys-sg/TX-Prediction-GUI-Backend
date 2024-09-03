import psycopg2
import bcrypt
import os
import time

"""
Database Class for Managing Users, Schools, and Observed Transcription Rates after Ligations

This class provides an interface for interacting with a PostgreSQL database that stores information related to schools, terms, ligation orders, user accounts, and observations. It includes methods for creating tables, inserting and querying data, and handling common database operations with retry logic.

Key Features:
- Initializes the database connection and creates necessary tables.
- Provides methods to insert and query schools, terms, ligation orders, user accounts, and observations.
- Utilizes retry logic for handling transient database errors.
- Supports password hashing for secure account management.

Dependencies:
- psycopg2: PostgreSQL adapter for Python.
- bcrypt: Library for password hashing.
- os: For environment variable access.
- time: For handling retry delays.

Usage:
- Create an instance of the class by passing the database URL to the constructor.
- Use methods like `insert_school`, `query_schools`, `insert_ligation_order`, etc., to interact with the database.
- Call `close()` to close the database connection when done.

Example:
    db = Database(db_url)
    db.insert_school('Example School', 'example.com')
    schools = db.query_schools()
    db.close()
"""


class Database:
    def __init__(self, db_url):
        self.db_url = db_url
        self.conn = psycopg2.connect(self.db_url)
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS school (
                name TEXT PRIMARY KEY,
                domain TEXT UNIQUE
            )''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS term (
                id SERIAL PRIMARY KEY,
                name TEXT,
                school TEXT,
                FOREIGN KEY(school) REFERENCES school(name)
            )''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ligation_orders (
                id SERIAL PRIMARY KEY,
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
                observations_id SERIAL PRIMARY KEY,
                sequence TEXT,
                account_email TEXT,
                observed_TX INTEGER,
                students TEXT,
                notes TEXT,
                date TEXT,
                FOREIGN KEY(account_email) REFERENCES accounts(email)
            )''')
            self.conn.commit()

    def close(self):
        self.conn.close()

    def execute_with_retry(self, query, params=(), retries=5):
        for attempt in range(retries):
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(query, params)
                    self.conn.commit()
                    return cursor
            except psycopg2.OperationalError as e:
                if "database is locked" in str(e):  # PostgreSQL doesn't have this issue, so adjust as needed
                    time.sleep(0.1)  # Wait a bit before retrying
                else:
                    raise
        raise psycopg2.OperationalError("database is locked")

    def insert_school(self, name, domain):
        try:
            self.execute_with_retry('INSERT INTO school (name, domain) VALUES (%s, %s)', (name, domain))
            return True
        except psycopg2.IntegrityError:
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
        cursor = self.execute_with_retry('SELECT name FROM school WHERE domain = %s', (domain,))
        result = cursor.fetchone()
        return result[0] if result else None

    def insert_term(self, term_name, school_name):
        # Check if the term already exists for the school
        cursor = self.execute_with_retry('SELECT id FROM term WHERE name = %s AND school = %s', (term_name, school_name))
        term_row = cursor.fetchone()
        if term_row: return False
        try:
            self.execute_with_retry('INSERT INTO term (name, school) VALUES (%s, %s)', (term_name, school_name))
            return True
        except psycopg2.IntegrityError:
            return False

    
    def query_terms_by_school(self, school_name):
        cursor = self.execute_with_retry('SELECT name FROM term WHERE school = %s', (school_name,))
        return [row[0] for row in cursor.fetchall()]
    
    def insert_ligation_order(self, school_name, term_name, order_name, sequence, date, students):
        try:
            cursor = self.execute_with_retry('SELECT id FROM term WHERE name = %s AND school = %s', (term_name, school_name))
            term_row = cursor.fetchone()
            
            if term_row is None:
                return False
            
            term_id = term_row[0]
            
            self.execute_with_retry('''
                INSERT INTO ligation_orders (term_id, order_name, sequence, date, students)
                VALUES (%s, %s, %s, %s, %s)
            ''', (term_id, order_name, sequence, date, students))
            
            return True
        
        except psycopg2.IntegrityError:
            return False

    def query_ligation_orders_by_school_and_term(self, school_name, term_name):
        cursor = self.execute_with_retry('''
            SELECT lo.order_name, lo.sequence, lo.date, lo.students
            FROM ligation_orders lo
            INNER JOIN term t ON lo.term_id = t.id
            WHERE t.name = %s AND t.school = %s
        ''', (term_name, school_name))
        return cursor.fetchall()
    
    def insert_account(self, email, school_name, first_name, last_name, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            self.execute_with_retry('''
                INSERT INTO accounts (email, school, first_name, last_name, password)
                VALUES (%s, %s, %s, %s, %s)
            ''', (email, school_name, first_name, last_name, hashed_password))
            return True
        except psycopg2.IntegrityError:
            return False
    
    def insert_observation(self, sequence, account_email, observed_TX, students, notes, date):
        try:
            self.execute_with_retry('''
                INSERT INTO observations (sequence, account_email, observed_TX, students, notes, date)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (sequence, account_email, observed_TX, students, notes, date))
            return True
        except psycopg2.IntegrityError:
            return False
    
    def query_observations_by_sequence(self, sequence):
        cursor = self.execute_with_retry('''
            SELECT account_email, observed_TX, students, notes, date
            FROM observations
            WHERE sequence = %s
        ''', (sequence,))
        return cursor.fetchall()
    
    def query_average_observed_TX_by_sequence(self, sequence):
        cursor = self.execute_with_retry('SELECT AVG(observed_TX) FROM observations WHERE sequence = %s', (sequence,))
        result = cursor.fetchone()
        return result[0] if result else None

    
    def query_accounts(self):
        cursor = self.execute_with_retry('SELECT email, password FROM accounts')
        return cursor.fetchall()
    
    def login_account(self, email, password):
        cursor = self.execute_with_retry('SELECT password FROM accounts WHERE email = %s', (email,))
        result = cursor.fetchone()
        if result is None: return False
        stored_password = result[0]
        return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
    
    def query_first_name_by_email(self, email):
        cursor = self.execute_with_retry('SELECT first_name FROM accounts WHERE email = %s', (email,))
        result = cursor.fetchone()
        return result[0] if result else None
        
    def query_last_name_by_email(self, email):
        cursor = self.execute_with_retry('SELECT last_name FROM accounts WHERE email = %s', (email,))
        result = cursor.fetchone()
        return result[0] if result else None
