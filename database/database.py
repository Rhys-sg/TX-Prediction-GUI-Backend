from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the base model for SQLAlchemy
Base = declarative_base()

class School(Base):
    __tablename__ = 'schools'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    domain = Column(String, nullable=False, unique=True)

class DataBase:
    def __init__(self, db_url):
        # Initialize the engine and session
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def insert_school(self, name, domain):
        # Insert a school if it doesn't exist
        school = self.session.query(School).filter_by(domain=domain).first()
        if not school:
            new_school = School(name=name, domain=domain)
            self.session.add(new_school)
            self.session.commit()

    def query_schools(self):
        # Query and return all schools
        return self.session.query(School).all()

    def query_domains(self):
        # Query and return all existing domains
        return [school.domain for school in self.session.query(School).all()]

