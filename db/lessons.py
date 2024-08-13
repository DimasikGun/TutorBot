import enum

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, BigInteger, Enum, DateTime, Time, Date

from db.base import Base, TimestampMixin


class LessonTypesEnum(enum.Enum):
    individual = 'Індивідуальний'
    group = 'Груповий'


class LessonStatusEnum(enum.Enum):
    scheduled = 'У розкладі'
    completed = 'Завершено'
    cancelled = 'Скасовано'


class DayOfWeekEnum(enum.Enum):
    monday = 'Понеділок'
    tuesday = 'Вівторок'
    wednesday = 'Середа'
    thursday = 'Четвер'
    friday = 'П\'ятниця'
    saturday = 'Субота'
    sunday = 'Неділя'


class LessonTypes(Base):
    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    price = Column(Numeric(10, 2), default=0)
    tutor = Column(BigInteger, ForeignKey('tutors.user_id'), nullable=False)
    lesson_subtype = Column(Enum(LessonTypesEnum), nullable=True)


class SingleLessons(TimestampMixin, Base):
    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    lesson_type = Column(Integer, ForeignKey('lessontypes.id'), nullable=False)
    student = Column(BigInteger, ForeignKey('students.user_id'), nullable=False)
    date_time = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)
    is_payed = Column(Integer, default=False)
    lesson_status = Column(Enum(LessonStatusEnum), nullable=True)


class RegularLessons(TimestampMixin, Base):
    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    lesson_type = Column(Integer, ForeignKey('lessontypes.id'), nullable=False)
    student = Column(BigInteger, ForeignKey('students.user_id'), nullable=False)
    duration = Column(Integer, nullable=False)
    day_of_week = Column(Enum(DayOfWeekEnum), nullable=True)
    time = Column(Time, nullable=False)
    end_date = Column(DateTime, nullable=True)


class SingleRegularLessons(TimestampMixin, Base):
    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    regular_lesson = Column(Integer, ForeignKey('regularlessons.id'), nullable=False)
    lesson_status = Column(Enum(LessonStatusEnum), nullable=True)
    is_payed = Column(Integer, default=False)
    date = Column(Date, nullable=False)
