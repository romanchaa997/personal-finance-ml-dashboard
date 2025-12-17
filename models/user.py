"""SQLAlchemy ORM models for users and authentication"""
from db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from hashlib import sha256


class User(Base):
    """User database model with authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transactions = relationship("Transaction", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return self.password_hash == sha256(password.encode()).hexdigest()


class Prediction(Base):
    """ML prediction storage model"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    prediction_type = Column(String)
    prediction_value = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="predictions")
    
    def __repr__(self):
        return f"<Prediction {self.prediction_type}: {self.prediction_value}>"
