from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Time, DateTime
from sqlalchemy.orm import relationship

from ..service.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    modified_when = Column(DateTime)
    created_when = Column(DateTime)
    hashed_password = Column(String)
    is_active = Column(Boolean)
    role = Column(String)




