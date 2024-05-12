from sqlalchemy import String, Column, Integer

from app.db.connection import Base


class User(Base):
    __tablename__ = "users"

    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
