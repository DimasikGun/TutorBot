from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base, declared_attr

BaseModel = declarative_base()


class Base(BaseModel):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.now())
