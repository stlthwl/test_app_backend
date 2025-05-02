from sqlalchemy import Boolean, Column, Integer, String, BigInteger
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    surname = Column(String)
    blocked = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
