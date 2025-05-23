from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from sqlalchemy.sql import func
import bcrypt
import pandas as pd

# Define the base model for SQLAlchemy
Base = declarative_base()

class School(Base):
    __tablename__ = 'schools'

    name = Column(String, primary_key=True, nullable=False, unique=True)
    domain = Column(String, nullable=False, unique=True)

class Term(Base):
    __tablename__ = 'terms'

    name = Column(String, primary_key=True, nullable=False)
    school_name = Column(String, ForeignKey('schools.name'), nullable=False)
    school = relationship("School")

class LigationsOrder(Base):
    __tablename__ = 'ligation_orders'

    term_name = Column(String, ForeignKey('terms.name'), primary_key=True, nullable=False)
    school_name = Column(String, ForeignKey('schools.name'), nullable=False)
    order_name = Column(String, primary_key=True, nullable=False)
    sequence = Column(Text)
    date = Column(String)
    students = Column(Text)
    term = relationship("Term")

class Account(Base):
    __tablename__ = 'accounts'

    email = Column(String, primary_key=True)
    school_name = Column(String, ForeignKey('schools.name'))
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)
    school = relationship("School")

class Observation(Base):
    __tablename__ = 'observations'

    sequence = Column(Text, primary_key=True)
    account_email = Column(String, ForeignKey('accounts.email'))
    school_name = Column(String, ForeignKey('schools.name'), nullable=False)
    term_name = Column(String, ForeignKey('terms.name'), primary_key=True, nullable=False)
    observed_TX = Column(Integer)
    students = Column(Text)
    notes = Column(Text)
    date = Column(String)
    account = relationship("Account")

class DataBase:
    def __init__(self, db_url):
        # Initialize the engine and session
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def insert_school(self, name, domain):
        name = name.lower()
        domain = domain.lower()
        try:
            new_school = School(name=name, domain=domain)
            self.session.add(new_school)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            return False

    def query_schools_domains(self):
        return self.session.query(School.name, School.domain).all()

    def query_schools(self):
        return [school.name for school in self.session.query(School).all()]
    
    def query_domains(self):
        return [school.domain for school in self.session.query(School).all()]

    def query_school_by_domain(self, domain):
        domain = domain.lower()
        school = self.session.query(School).filter_by(domain=domain).first()
        return school.name if school else None

    def insert_term(self, term_name, school_name):
        term_name = term_name.lower()
        school_name = school_name.lower()
        school = self.session.query(School).filter_by(name=school_name).first()
        if not school:
            return False
        try:
            new_term = Term(name=term_name, school_name=school_name)
            self.session.add(new_term)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            return False

    def query_terms_by_school(self, school_name):
        school_name = school_name.lower()
        return [term.name for term in self.session.query(Term).filter_by(school_name=school_name).all()]

    def insert_ligation_order(self, school_name, term_name, order_name, sequence, date, students):
        school_name = school_name.lower()
        term_name = term_name.lower()
        order_name = order_name.lower()
        school = self.session.query(School).filter_by(name=school_name).first()
        if not school:
            return False
        term = self.session.query(Term).filter_by(name=term_name, school_name=school_name).first()
        if not term:
            return False
        try:
            new_order = LigationsOrder(term_name=term_name, school_name=school_name, order_name=order_name, sequence=sequence, date=date, students=students)
            self.session.add(new_order)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            return False

    def query_ligation_orders_by_school_and_term(self, school_name, term_name):
        school_name = school_name.lower()
        term_name = term_name.lower()

        student_ligations = self.session.query(LigationsOrder).filter_by(school_name=school_name, term_name=term_name).all()

        # Convert the results to a list of dictionaries
        ligations_list = [
            {
                'Order Name': ligation.order_name,
                'Sequence': ligation.sequence,
                'Date': ligation.date,
                'Students': ligation.students
            }
            for ligation in student_ligations
        ]

        return {'studentLigations': ligations_list}

    def insert_account(self, email, domain, first_name, last_name, password):
        email = email.lower()
        domain = domain.lower()
        first_name = first_name.lower()
        last_name = last_name.lower()

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        school_name = self.query_school_by_domain(domain)

        # Check if the account already exists
        if self.query_account_by_email(email):
            return 'Account already exists'
        
        # Check if the domain is valid
        if not school_name:
            return f'E-mail must have a valid domain.'
        
        try:
            new_account = Account(email=email, school_name=school_name, first_name=first_name, last_name=last_name, password=hashed_password)
            self.session.add(new_account)
            self.session.commit()
            return None
        except Exception as e:
            self.session.rollback()
            return f'An exception occurred, {str(e)}'

    def insert_observation(self, sequence, account_email, school_name, term_name, observed_TX, students, notes, date):
        sequence = sequence.lower()
        account_email = account_email.lower()
        students = students.lower()
        notes = notes.lower()
        try:
            new_observation = Observation(
                sequence=sequence,
                account_email=account_email,
                school_name=school_name,
                term_name=term_name,
                observed_TX=observed_TX,
                students=students,
                notes=notes,
                date=date
            )
            self.session.add(new_observation)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            return False

    def query_observations_by_sequence(self, sequence):
        sequence = sequence.lower()
        return self.session.query(Observation).filter_by(sequence=sequence).all()
    
    def query_average_observed_TX_by_sequence(self, sequence):
        sequence = sequence.lower()
        result = self.session.query(func.avg(Observation.observed_TX)).filter_by(sequence=sequence).scalar()
        return result
    
    def query_observations_by_school_and_term(self, school_name, term_name):
        school_name = school_name.lower()
        term_name = term_name.lower()

        observations = self.session.query(Observation).filter_by(school_name=school_name, term_name=term_name).all()
        observations = [
            {
                'Sequence': observation.sequence,
                'Observed TX': observation.observed_TX,
                'Students': observation.students,
                'Notes': observation.notes,
                'Date': observation.date
            }
            for observation in observations
        ]

        return observations
    
    def replace_observations_from_df(self, df, school_name, term_name):

        account_email = df['account_email'].iloc[0].lower()
        if not self.query_account_by_email(account_email):
            return False
        
        school_name = school_name.lower()
        term_name = term_name.lower()

        try:
            # Delete existing observations for the given school and term
            self.session.query(Observation).filter(
                and_(
                    Observation.school_name == school_name,
                    Observation.term_name == term_name
                )
            ).delete(synchronize_session=False)

            # Insert new observations from the DataFrame
            for _, row in df.iterrows():
                new_observation = Observation(
                    sequence=row['sequence'].lower(),
                    account_email=row['account_email'].lower(),
                    school_name=school_name,
                    term_name=term_name,
                    observed_TX=int(row['observed_TX']) if pd.notnull(row['observed_TX']) else None,
                    students=row['students'].lower() if pd.notnull(row['students']) else '',
                    notes=row['notes'].lower() if pd.notnull(row['notes']) else '',
                    date=row['date']
                )
                self.session.add(new_observation)

            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error replacing observations: {e}")
            return False

    def query_accounts(self):
        return self.session.query(Account.email, Account.password).all()
    
    def query_account_by_email(self, email):
        email = email.lower()
        return self.session.query(Account).filter_by(email=email).first()

    def login_account(self, email, password):
        email = email.lower()
        account = self.session.query(Account).filter_by(email=email).first()
        if account is None:
            return False
        stored_password = account.password
        return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))

    def query_first_name_by_email(self, email):
        email = email.lower()
        account = self.session.query(Account).filter_by(email=email).first()
        return account.first_name if account else None

    def query_last_name_by_email(self, email):
        email = email.lower()
        account = self.session.query(Account).filter_by(email=email).first()
        return account.last_name if account else None

    def close(self):
        self.session.close()
