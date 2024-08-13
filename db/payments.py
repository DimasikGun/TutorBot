import enum


from sqlalchemy import Column, Integer, ForeignKey, BigInteger, Numeric, Enum

from db.base import TimestampMixin, Base


class PaymentStatusEnum(enum.Enum):
    in_process = 'В процесі'
    reviewing = 'На розгляді'
    declined = 'Відхилено'
    accepted = 'Прийнято'


class Payments(TimestampMixin, Base):
    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    lesson_type = Column(Integer, ForeignKey('lessontypes.id'), nullable=False)
    student = Column(BigInteger, ForeignKey('students.user_id'), nullable=False)
    tutor = Column(BigInteger, ForeignKey('tutors.user_id'), nullable=False)
    amount = Column(Numeric(12, 2), default=0)
    day_of_week = Column(Enum(PaymentStatusEnum), nullable=True)
