import os
import bcrypt
import time
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Define the database models (tables)
class School(Base):
    __tablename__ = 'school'
    name = Column(String, primary_key=True)
    domain = Column(String, unique=True)

class Term(Base):
    __tablename__ = 'term'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    school_name = Column(String, ForeignKey('school.name'))
    school = relationship('School')

class LigationOrder(Base):
    __tablename__ = 'ligation_orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    term_id = Column(Integer, ForeignKey('term.id'))
    order_name = Column(String)
    sequence = Column(Text)
    date = Column(String)
    students = Column(Text)
    term = relationship('Term')

class Account(Base):
    __tablename__ = 'accounts'
    email = Column(String, primary_key=True)
    school_name = Column(String, ForeignKey('school.name'))
    first_name = Column(String)
    last_name = Column(String)
    password = Column(Text)
    school = relationship('School')

class Observation(Base):
    __tablename__ = 'observations'
    observations_id = Column(Integer, primary_key=True, autoincrement=True)
    sequence = Column(Text)
    account_email = Column(String, ForeignKey('accounts.email'))
    observed_TX = Column(Integer)
    students = Column(Text)
    notes = Column(Text)
    date = Column(String)
    account = relationship('Account')


# Database class
class DataBase:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def insert_school(self, name, domain):
        if not self.session.query(School).filter_by(domain=domain).first():
            new_school = School(name=name, domain=domain)
            self.session.add(new_school)
            self.session.commit()
            return True
        return False

    def query_schools_domains(self):
        return self.session.query(School.name, School.domain).all()

    def query_schools(self):
        return [school.name for school in self.session.query(School).all()]

    def query_domains(self):
        return [school.domain for school in self.session.query(School).all()]

    def query_school_by_domain(self, domain):
        school = self.session.query(School.name).filter_by(domain=domain).first()
        return school.name if school else None

    def insert_term(self, term_name, school_name):
        term = self.session.query(Term).filter_by(name=term_name, school_name=school_name).first()
        if not term:
            new_term = Term(name=term_name, school_name=school_name)
            self.session.add(new_term)
            self.session.commit()
            return True
        return False

    def query_terms_by_school(self, school_name):
        return [term.name for term in self.session.query(Term).filter_by(school_name=school_name).all()]

    def insert_ligation_order(self, school_name, term_name, order_name, sequence, date, students):
        term = self.session.query(Term).filter_by(name=term_name, school_name=school_name).first()
        if term:
            new_order = LigationOrder(term_id=term.id, order_name=order_name, sequence=sequence, date=date, students=students)
            self.session.add(new_order)
            self.session.commit()
            return True
        return False

    def query_ligation_orders_by_school_and_term(self, school_name, term_name):
        return self.session.query(LigationOrder.order_name, LigationOrder.sequence, LigationOrder.date, LigationOrder.students).join(Term).filter(Term.name == term_name, Term.school_name == school_name).all()

    def insert_account(self, email, school_name, first_name, last_name, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        if not self.session.query(Account).filter_by(email=email).first():
            new_account = Account(email=email, school_name=school_name, first_name=first_name, last_name=last_name, password=hashed_password)
            self.session.add(new_account)
            self.session.commit()
            return True
        return False

    def insert_observation(self, sequence, account_email, observed_TX, students, notes, date):
        if self.session.query(Account).filter_by(email=account_email).first():
            new_observation = Observation(sequence=sequence, account_email=account_email, observed_TX=observed_TX, students=students, notes=notes, date=date)
            self.session.add(new_observation)
            self.session.commit()
            return True
        return False

    def query_observations_by_sequence(self, sequence):
        return self.session.query(Observation.account_email, Observation.observed_TX, Observation.students, Observation.notes, Observation.date).filter_by(sequence=sequence).all()

    def query_average_observed_TX_by_sequence(self, sequence):
        avg = self.session.query(self.session.query(Observation.observed_TX).filter_by(sequence=sequence).avg()).scalar()
        return avg if avg else None

    def query_accounts(self):
        return self.session.query(Account.email, Account.password).all()

    def login_account(self, email, password):
        account = self.session.query(Account.password).filter_by(email=email).first()
        if account and bcrypt.checkpw(password.encode('utf-8'), account.password.encode('utf-8')):
            return True
        return False

    def query_first_name_by_email(self, email):
        account = self.session.query(Account.first_name).filter_by(email=email).first()
        return account.first_name if account else None

    def query_last_name_by_email(self, email):
        account = self.session.query(Account.last_name).filter_by(email=email).first()
        return account.last_name if account else None

    def delete_database(self):
        Base.metadata.drop_all(self.engine)
        self.session.commit()
        return True
