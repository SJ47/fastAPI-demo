import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
# from sqlalchemy.orm.session import Session
load_dotenv()

# Load up env variables
DBHOST=os.getenv("HOST")
DBNAME=os.getenv("DBNAME")
DBUSER=os.getenv("DBUSER")  # Using DBUSER instead of USER and USER uses the USER variable in the system environment (the logged in user to the OS)
DBPASSWORD=os.getenv("PASSWORD")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DBUSER}:{DBPASSWORD}@{DBHOST}/{DBNAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency Function used to create a session to our database anytime we get a request to our API endpoint
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()