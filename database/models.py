import datetime

from sqlalchemy.orm import declarative_base
from sqlalchemy import Table, Integer, String, Column, TIMESTAMP, Boolean, ForeignKey

Base = declarative_base()

class Record(Base):
    __tablename__ = "record"

    id = Column(Integer, primary_key=True)
    auther = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    tag_name = Column(String, nullable=False)


class TagsRecord(Base):
    __tablename__ = "tagsrecord"

    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    record_id = Column(Integer, ForeignKey("record.id", ondelete="CASCADE"), nullable=False)

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

class UserTg(Base):
    __tablename__ = "usertg"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    tg_id = Column(Integer, nullable=False)