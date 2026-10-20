"""Read-only queries for the admin panel.

Each function takes a Session so it can be tested with an in-memory database.
"""
from typing import List, NamedTuple, Optional

from sqlmodel import Session, func, select

from database.models import Course, Enrollment, User


class OverviewStats(NamedTuple):
    users: int
    courses: int
    enrollments: int


class CourseCount(NamedTuple):
    title: str
    capacity: Optional[int]
    enrolled: int


def get_overview_stats(session: Session) -> OverviewStats:
    return OverviewStats(
        users=session.exec(select(func.count(User.id))).one(),
        courses=session.exec(select(func.count(Course.id))).one(),
        enrollments=session.exec(select(func.count(Enrollment.id))).one(),
    )


def get_course_enrollment_counts(session: Session) -> List[CourseCount]:
    """Return every course with its enrollment count (0 if nobody enrolled)."""
    rows = session.exec(
        select(Course.title, Course.capacity, func.count(Enrollment.id))
        .select_from(Course)
        .join(Enrollment, Enrollment.course_id == Course.id, isouter=True)
        .group_by(Course.id, Course.title, Course.capacity)
        .order_by(Course.id)
    ).all()
    return [CourseCount(title, capacity, enrolled) for title, capacity, enrolled in rows]