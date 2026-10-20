import pytest
from sqlmodel import Session, SQLModel, create_engine

from database.admin_queries import get_course_enrollment_counts, get_overview_stats
from database.models import Course, Enrollment, User


@pytest.fixture()
def session():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session


def test_overview_stats_empty_database(session):
    stats = get_overview_stats(session)
    assert (stats.users, stats.courses, stats.enrollments) == (0, 0, 0)


def test_course_counts_include_courses_without_enrollments(session):
    limited = Course(title="Limited", capacity=2)
    unlimited = Course(title="Unlimited", capacity=None)
    user = User(telegram_id=1, full_name="Test", phone="09123456789")
    session.add_all([limited, unlimited, user])
    session.commit()
    session.refresh(limited)
    session.refresh(user)

    session.add(Enrollment(user_id=user.id, course_id=limited.id))
    session.commit()

    rows = get_course_enrollment_counts(session)
    assert [(r.title, r.capacity, r.enrolled) for r in rows] == [
        ("Limited", 2, 1),
        ("Unlimited", None, 0),
    ]
    stats = get_overview_stats(session)
    assert (stats.users, stats.courses, stats.enrollments) == (1, 2, 1)