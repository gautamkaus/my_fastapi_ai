from sqlalchemy import create_engine, Column, Integer, Text, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Load environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/dollar_ai_db")

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a configured Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

# Define the Interaction model
class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    user_input_text = Column(Text, nullable=True)
    user_input_voice_path = Column(String, nullable=True)  # Store file path
    response_text = Column(Text, nullable=True)
    response_voice_path = Column(String, nullable=True)  # Store file path
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()