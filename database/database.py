from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy import inspect
import bcrypt

# Define the base model for SQLAlchemy
Base = declarative_base()

class School(Base):
    __tablename__ = 'schools'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    domain = Column(String, nullable=False, unique=True)

class Term(Base):
    __tablename__ = 'terms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    school = relationship("School")

class LigationsOrder(Base):
    __tablename__ = 'ligation_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    term_id = Column(Integer, ForeignKey('terms.id'), nullable=False)
    order_name = Column(String)
    sequence = Column(Text)
    date = Column(String)
    students = Column(Text)
    term = relationship("Term")

class Account(Base):
    __tablename__ = 'accounts'

    email = Column(String, primary_key=True)
    school_id = Column(Integer, ForeignKey('schools.id'))
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)
    school = relationship("School")

class Observation(Base):
    __tablename__ = 'observations'

    observations_id = Column(Integer, primary_key=True, autoincrement=True)
    sequence = Column(Text)
    account_email = Column(String, ForeignKey('accounts.email'))
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
            new_term = Term(name=term_name, school_id=school.id)
            self.session.add(new_term)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            return False

    def query_terms_by_school(self, school_name):
        school_name = school_name.lower()
        school = self.session.query(School).filter_by(name=school_name).first()
        if not school:
            return []
        return [term.name for term in self.session.query(Term).filter_by(school_id=school.id).all()]

    def insert_ligation_order(self, school_name, term_name, order_name, sequence, date, students):
        school_name = school_name.lower()
        term_name = term_name.lower()
        order_name = order_name.lower()
        school = self.session.query(School).filter_by(name=school_name).first()
        if not school:
            return False
        term = self.session.query(Term).filter_by(name=term_name, school_id=school.id).first()
        if not term:
            return False
        try:
            new_order = LigationsOrder(term_id=term.id, order_name=order_name, sequence=sequence, date=date, students=students)
            self.session.add(new_order)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            return False

    def query_ligation_orders_by_school_and_term(self, school_name, term_name):
        school_name = school_name.lower()
        term_name = term_name.lower()
        school = self.session.query(School).filter_by(name=school_name).first()
        if not school:
            return []
        term = self.session.query(Term).filter_by(name=term_name, school_id=school.id).first()
        if not term:
            return []
        return self.session.query(LigationsOrder).filter_by(term_id=term.id).all()

    def insert_account(self, email, domain, first_name, last_name, password):
        email = email.lower()
        domain = domain.lower()
        first_name = first_name.lower()
        last_name = last_name.lower()

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        school = self.query_school_by_domain(domain)

        # Check if the account already exists
        if self.query_account_by_email(email):
            return 'TEST: Account already exists'
        
        # Check if the domain is valid
        if not school:
            return 'TEST: E-mail must have a valid domain'
        
        try:
            new_account = Account(email=email, school_id=school.id, first_name=first_name, last_name=last_name, password=hashed_password)
            self.session.add(new_account)
            self.session.commit()
            return None
        except Exception as e:
            self.session.rollback()
            return f'An exception occurred, {str(e)}'

    def insert_observation(self, sequence, account_email, observed_TX, students, notes, date):
        sequence = sequence.lower()
        account_email = account_email.lower()
        students = students.lower()
        notes = notes.lower()
        try:
            new_observation = Observation(sequence=sequence, account_email=account_email, observed_TX=observed_TX, students=students, notes=notes, date=date)
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
    
    def delete_all_rows(self, model):
        try:
            self.session.query(model).delete()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
        finally:
            self.session.close()

    def delete_all_tables(self):
        models = [School, Term, LigationsOrder, Account, Observation]
        try:
            for model in models:
                self.delete_all_rows(model)
        except Exception as e:
            print(f"Error occurred while clearing tables: {e}")

    def delete_all_rows(self, model):
        try:
            self.session.query(model).delete()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
        finally:
            self.session.close()