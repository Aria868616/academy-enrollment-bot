"""Enrollment business logic, independent of Telegram.

Takes a Session so it can be tested with an in-memory database.
"""
import threading
from enum import Enum

from sqlmodel import Session, func, select

from database.models import Course, Enrollment, User

# telebot handles messages in threads. The lock makes "count then insert"
# atomic inside this one process, so two users cannot take the last seat.
_enroll_lock = threading.Lock()


class EnrollmentResult(Enum):
    ENROLLED = "enrolled"
    ALREADY_ENROLLED = "already_enrolled"
    COURSE_FULL = "course_full"
    COURSE_NOT_FOUND = "course_not_found"


def enroll_user(
    session: Session,
    telegram_id: int,
    full_name: str,
    phone: str,
    course_id: int,
) -> EnrollmentResult:
    with _enroll_lock:
        course = session.get(Course, course_id)
        if course is None:
            return EnrollmentResult.COURSE_NOT_FOUND

        db_user = session.exec(
            select(User).where(User.telegram_id == telegram_id)
        ).first()

        if db_user is not None:
            existing = session.exec(
                select(Enrollment).where(
                    Enrollment.user_id == db_user.id,
                    Enrollment.course_id == course_id,
                )
            ).first()
            if existing:
                return EnrollmentResult.ALREADY_ENROLLED

        if course.capacity is not None:
            enrolled = session.exec(
                select(func.count(Enrollment.id)).where(
                    Enrollment.course_id == course_id
                )
            ).one()
            if enrolled >= course.capacity:
                return EnrollmentResult.COURSE_FULL

        if db_user is None:
            db_user = User(telegram_id=telegram_id, full_name=full_name, phone=phone)
            session.add(db_user)
            session.flush()  # assigns db_user.id without committing yet

        session.add(Enrollment(user_id=db_user.id, course_id=course_id))
        session.commit()
        return EnrollmentResult.ENROLLED