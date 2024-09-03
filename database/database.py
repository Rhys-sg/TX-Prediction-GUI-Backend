import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

class Database:
    def __init__(self, db_url):
        self.db_url = db_url
    
    def create_tables(self):
        """Create tables in the database if they do not exist."""
        
        # List of tables to check and their respective creation queries
        tables_to_create = {
            'schools': """
                CREATE TABLE schools (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    domain VARCHAR(255) UNIQUE NOT NULL
                );
            """,
            'accounts': """
                CREATE TABLE accounts (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    school_id INTEGER NOT NULL,
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    password VARCHAR(255),
                    FOREIGN KEY (school_id) REFERENCES schools(id)
                );
            """,
            'observations': """
                CREATE TABLE observations (
                    id SERIAL PRIMARY KEY,
                    coding_strand TEXT NOT NULL,
                    account_email VARCHAR(255) NOT NULL,
                    observed_tx FLOAT NOT NULL,
                    students TEXT,
                    notes TEXT,
                    date DATE,
                    FOREIGN KEY (account_email) REFERENCES accounts(email)
                );
            """,
            'ligations': """
                CREATE TABLE ligations (
                    id SERIAL PRIMARY KEY,
                    school VARCHAR(255) NOT NULL,
                    term VARCHAR(255) NOT NULL,
                    order_name VARCHAR(255) NOT NULL,
                    sequence TEXT NOT NULL,
                    date DATE NOT NULL,
                    students TEXT
                );
            """
        }
        
        with self.conn.cursor() as cursor:
            for table_name, create_query in tables_to_create.items():
                # Check if the table already exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    );
                """, (table_name,))
                
                # Fetch result
                exists = cursor.fetchone()[0]
                
                # Create table if it does not exist
                if not exists:
                    cursor.execute(create_query)
                    print(f"Table '{table_name}' created.")
                else:
                    print(f"Table '{table_name}' already exists.")

            # Commit changes to the database
            self.conn.commit()


    def connect(self):
        """
        Establishes a connection to the PostgreSQL database.
        """
        return psycopg2.connect(self.db_url)

    def query_domains(self):
        """
        Queries all domains from the 'schools' table.
        """
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT domain FROM schools")
                results = cursor.fetchall()
        return [row[0] for row in results]

    def insert_school(self, name, domain):
        """
        Inserts a new school into the 'schools' table.
        """
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO schools (name, domain) VALUES (%s, %s)", (name, domain))
                conn.commit()

    def query_schools(self):
        """
        Queries all schools from the 'schools' table.
        """
        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM schools")
                results = cursor.fetchall()
        return results

    def query_terms_by_school(self, school_name):
        """
        Queries terms by school from the 'terms' table based on school name.
        """
        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM terms WHERE school_name = %s", (school_name,))
                results = cursor.fetchall()
        return results

    def insert_observation(self, coding_strand, account_email, observed_TX, students, notes, date_observed):
        """
        Inserts an observation into the 'observed_TX' table.
        """
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO observed_TX (coding_strand, account_email, observed_TX, students, notes, date_observed) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (coding_strand, account_email, observed_TX, students, notes, date_observed))
                conn.commit()
        return True

    def query_average_observed_TX_by_sequence(self, coding_strand):
        """
        Queries the average observed transcription by coding strand.
        """
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT AVG(observed_TX) FROM observed_TX WHERE coding_strand = %s
                """, (coding_strand,))
                result = cursor.fetchone()
        return result[0] if result else None

    def insert_ligation_order(self, school, term, order_name, sequence, date_ordered, students):
        """
        Inserts a ligation order into the 'ligation_orders' table.
        """
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ligation_orders (school, term, order_name, sequence, date_ordered, students) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (school, term, order_name, sequence, date_ordered, students))
                conn.commit()
        return True

    def query_ligation_orders_by_school_and_term(self, school, term):
        """
        Queries ligation orders by school and term.
        """
        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM ligation_orders WHERE school = %s AND term = %s
                """, (school, term))
                results = cursor.fetchall()
        return results

    def insert_account(self, email, school, first_name, last_name, password):
        """
        Inserts a new account into the 'accounts' table.
        """
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO accounts (email, school, first_name, last_name, password) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (email, school, first_name, last_name, password))
                conn.commit()
        return True

    def login_account(self, email, password):
        """
        Verifies the account credentials for login.
        """
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS(SELECT 1 FROM accounts WHERE email = %s AND password = %s)
                """, (email, password))
                result = cursor.fetchone()
        return result[0]

    def query_first_name_by_email(self, email):
        """
        Queries the first name of the account holder by email.
        """
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT first_name FROM accounts WHERE email = %s", (email,))
                result = cursor.fetchone()
        return result[0] if result else None

    def query_last_name_by_email(self, email):
        """
        Queries the last name of the account holder by email.
        """
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT last_name FROM accounts WHERE email = %s", (email,))
                result = cursor.fetchone()
        return result[0] if result else None
