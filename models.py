from sqlalchemy import Boolean, Column, Integer, String, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    surname = Column(String)
    blocked = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)


class Confirm(Base):
    __tablename__ = "confirm_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    actual = Column(Boolean, default=False)

    user = relationship("User", back_populates="confirm_codes")


# Добавьте обратную связь в модель User
User.confirm_codes = relationship("Confirm", back_populates="user")

