from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import bcrypt

# Define the base model for SQLAlchemy
Base = declarative_base()

class School(Base):
    __tablename__ = 'schools'

    name = Column(String, primary_key=True, nullable=False, unique=True)
    domain = Column(String, nullable=False, unique=True)

    @classmethod
    def insert(cls, session, name, domain):
        name = name.lower()
        domain = domain.lower()
        try:
            new_school = cls(name=name, domain=domain)
            session.add(new_school)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False

    @classmethod
    def query_all(cls, session):
        return session.query(cls).all()
    
    @classmethod
    def query_schools(cls, session):
        return [school.name for school in cls.query_all(session)]
    
    @classmethod
    def query_domains(cls, session):
        return [school.domain for school in cls.query_all(session)]

    @classmethod
    def query_by_domain(cls, session, domain):
        domain = domain.lower()
        school = session.query(cls).filter_by(domain=domain).first()
        return school.name if school else None


class Term(Base):
    __tablename__ = 'terms'

    name = Column(String, primary_key=True, nullable=False)
    school_name = Column(String, ForeignKey('schools.name'), nullable=False)
    school = relationship("School")

    @classmethod
    def insert(cls, session, term_name, school_name):
        term_name = term_name.lower()
        school_name = school_name.lower()
        if not session.query(School).filter_by(name=school_name).first():
            return False
        try:
            new_term = cls(name=term_name, school_name=school_name)
            session.add(new_term)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False

    @classmethod
    def query_by_school(cls, session, school_name):
        school_name = school_name.lower()
        return [term.name for term in session.query(cls).filter_by(school_name=school_name).all()]


class LigationsOrder(Base):
    __tablename__ = 'ligation_orders'

    term_name = Column(String, ForeignKey('terms.name'), primary_key=True, nullable=False)
    school_name = Column(String, ForeignKey('schools.name'), nullable=False)
    order_name = Column(String, primary_key=True, nullable=False)
    sequence = Column(Text)
    date = Column(String)
    students = Column(Text)
    term = relationship("Term")

    @classmethod
    def insert(cls, session, school_name, term_name, order_name, sequence, date, students):
        school_name = school_name.lower()
        term_name = term_name.lower()
        order_name = order_name.lower()
        if not session.query(School).filter_by(name=school_name).first():
            return False
        if not session.query(Term).filter_by(name=term_name, school_name=school_name).first():
            return False
        try:
            new_order = cls(term_name=term_name, school_name=school_name, order_name=order_name, sequence=sequence, date=date, students=students)
            session.add(new_order)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False

    @classmethod
    def query_by_school_and_term(cls, session, school_name, term_name):
        school_name = school_name.lower()
        term_name = term_name.lower()
        return session.query(cls).filter_by(school_name=school_name, term_name=term_name).all()


class Account(Base):
    __tablename__ = 'accounts'

    email = Column(String, primary_key=True)
    school_name = Column(String, ForeignKey('schools.name'))
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)
    school = relationship("School")

    @classmethod
    def insert(cls, session, email, domain, first_name, last_name, password):
        email = email.lower()
        domain = domain.lower()
        first_name = first_name.lower()
        last_name = last_name.lower()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        school_name = School.query_by_domain(session, domain)
        if cls.query_by_email(session, email):
            return 'Account already exists'
        if not school_name:
            return f'E-mail must have a valid domain.'
        try:
            new_account = cls(email=email, school_name=school_name, first_name=first_name, last_name=last_name, password=hashed_password)
            session.add(new_account)
            session.commit()
            return None
        except Exception as e:
            session.rollback()
            return f'An exception occurred, {str(e)}'

    @classmethod
    def query_all(cls, session):
        return session.query(cls).all()
    
    @classmethod
    def query_by_email(cls, session, email):
        email = email.lower()
        return session.query(cls).filter_by(email=email).first()

    @classmethod
    def login(cls, session, email, password):
        email = email.lower()
        account = cls.query_by_email(session, email)
        if account is None:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), account.password.encode('utf-8'))

    @classmethod
    def query_first_name(cls, session, email):
        email = email.lower()
        account = cls.query_by_email(session, email)
        return account.first_name if account else None

    @classmethod
    def query_last_name(cls, session, email):
        email = email.lower()
        account = cls.query_by_email(session, email)
        return account.last_name if account else None


class Observation(Base):
    __tablename__ = 'observations'

    sequence = Column(Text, primary_key=True)
    account_email = Column(String, ForeignKey('accounts.email'))
    observed_TX = Column(Integer)
    students = Column(Text)
    notes = Column(Text)
    date = Column(String)
    account = relationship("Account")

    @classmethod
    def insert(cls, session, sequence, account_email, observed_TX, students, notes, date):
        sequence = sequence.lower()
        account_email = account_email.lower()
        students = students.lower()
        notes = notes.lower()
        try:
            new_observation = cls(sequence=sequence, account_email=account_email, observed_TX=observed_TX, students=students, notes=notes, date=date)
            session.add(new_observation)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False

    @classmethod
    def query_by_sequence(cls, session, sequence):
        sequence = sequence.lower()
        return session.query(cls).filter_by(sequence=sequence).all()
    
    @classmethod
    def query_average_observed_TX(cls, session, sequence):
        sequence = sequence.lower()
        return session.query(func.avg(cls.observed_TX)).filter_by(sequence=sequence).scalar()


class DataBase:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def close(self):
        self.session.close()