from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import declared_attr

from db.base import Base, TimestampMixin


class DiscordMixin:
    @declared_attr
    def discord(cls):
        return Column(String(32), nullable=True)


class BalanceMixin:
    @declared_attr
    def balance(cls):
        return Column(Numeric(10, 2), nullable=True, default=None)


class Users(TimestampMixin, Base):
    __abstract__ = True

    user_id = Column(BigInteger, unique=True, nullable=False, primary_key=True, autoincrement=False)  # tg user id
    username = Column(String(32), nullable=True)
    name = Column(String(32), nullable=False)
    surname = Column(String(32), nullable=False)
    phone = Column(String(16), nullable=True)


class Tutors(DiscordMixin, Users):
    second_name = Column(String(32), nullable=True)
    lesson_max_duration = Column(Integer, nullable=False)


class Parents(BalanceMixin, Users):
    __tablename__ = 'parents'


class Students(BalanceMixin, DiscordMixin, Users):
    parent = Column(BigInteger, ForeignKey('parents.user_id'), nullable=True)
    grade = Column(Integer, nullable=True)


class Notes(Users):
    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    tutor = Column(BigInteger, ForeignKey('tutors.user_id'), nullable=False)
    student = Column(BigInteger, ForeignKey('students.user_id'), nullable=False)
    text = Column(String(256), nullable=False)
