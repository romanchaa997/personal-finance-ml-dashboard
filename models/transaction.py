"""SQLAlchemy ORM models for transactions"""
from db.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class TransactionCategory(str, enum.Enum):
    INCOME = "INCOME"
    FOOD = "FOOD"
    TRANSPORT = "TRANSPORT"
    ENTERTAINMENT = "ENTERTAINMENT"
    UTILITIES = "UTILITIES"
    HEALTHCARE = "HEALTHCARE"
    SHOPPING = "SHOPPING"
    OTHER = "OTHER"


class Transaction(Base):
    """Transaction database model"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    external_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    currency = Column(String, default="USD")
    merchant = Column(String)
    description = Column(String)
    category = Column(Enum(TransactionCategory), default=TransactionCategory.OTHER)
    transaction_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction {self.id}: {self.merchant} {self.amount}>"
