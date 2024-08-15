from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey
from sqlalchemy.orm import declared_attr

from db.base import Base, TimestampMixin


class DiscordMixin:
    @declared_attr
    def discord(cls):
        return Column(String(32), nullable=True)


class Users(TimestampMixin, Base):
    __abstract__ = True

    user_id = Column(BigInteger, unique=True, nullable=False, primary_key=True, autoincrement=False)  # tg user id
    username = Column(String(32), nullable=True)
    name = Column(String(32), nullable=False)
    surname = Column(String(32), nullable=False)
    phone = Column(String(16), nullable=True)


class Tutors(DiscordMixin, Users):
    second_name = Column(String(32), nullable=False)
    lesson_max_duration = Column(Integer, nullable=False)


class Parents(Users):
    __tablename__ = 'parents'


class Students(DiscordMixin, Users):
    parent = Column(BigInteger, ForeignKey('parents.user_id'), nullable=True)
    grade = Column(Integer, nullable=True)
