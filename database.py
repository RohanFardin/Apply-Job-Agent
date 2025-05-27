import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('database')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    google_oauth_id = Column(String, unique=True, nullable=True)
    email_verified_at = Column(DateTime, nullable=True)
    role = Column(String, nullable=False, default='customer')
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    resumes = relationship('Resume', back_populates='user')
    subscriptions = relationship('UserSubscription', back_populates='user')
    payments = relationship('Payment', back_populates='user')
    job_applications = relationship('JobApplication', back_populates='user')
    ai_usage_logs = relationship('AIUsageLog', back_populates='user')

class Resume(Base):
    __tablename__ = 'resumes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    resume_data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parsed_summary_json = Column(Text, nullable=True)
    version_name = Column(String, nullable=True)
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    user = relationship('User', back_populates='resumes')
    job_applications = relationship('JobApplication', back_populates='original_resume')

class Plan(Base):
    __tablename__ = 'plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    application_limit = Column(Integer, nullable=True)
    customization_limit = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship('UserSubscription', back_populates='plan')

class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='subscriptions')
    plan = relationship('Plan', back_populates='subscriptions')

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, nullable=False)
    payment_method = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='payments')

class JobApplication(Base):
    __tablename__ = 'job_applications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=False)
    job_title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    application_date = Column(Date, nullable=False)
    status = Column(String, default='applied')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='job_applications')
    original_resume = relationship('Resume', back_populates='job_applications')

class AIUsageLog(Base):
    __tablename__ = 'ai_usage_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action_type = Column(String, nullable=False)
    usage_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='ai_usage_logs')

# Database dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables
def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

