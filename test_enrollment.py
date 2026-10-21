import pytest
from sqlmodel import Session, SQLModel, create_engine, func, select

from database.enrollment import EnrollmentResult, enroll_user
from database.models import Course, Enrollment, User


@pytest.fixture()
def session():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session


def _make_course(session, title="Course", capacity=None):
    course = Course(title=title, capacity=capacity)
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


def _enroll(session, course, telegram_id=1):
    return enroll_user(
        session,
        telegram_id=telegram_id,
        full_name="Test",
        phone="09123456789",
        course_id=course.id,
    )


def _count(session, model):
    return session.exec(select(func.count(model.id))).one()


def test_new_user_is_enrolled(session):
    course = _make_course(session)
    assert _enroll(session, course) == EnrollmentResult.ENROLLED
    assert _count(session, User) == 1
    assert _count(session, Enrollment) == 1


def test_same_user_twice_is_already_enrolled(session):
    course = _make_course(session)
    _enroll(session, course)
    assert _enroll(session, course) == EnrollmentResult.ALREADY_ENROLLED
    assert _count(session, Enrollment) == 1


def test_full_course_rejects_new_user_without_creating_them(session):
    course = _make_course(session, capacity=1)
    assert _enroll(session, course, telegram_id=1) == EnrollmentResult.ENROLLED
    assert _enroll(session, course, telegram_id=2) == EnrollmentResult.COURSE_FULL
    assert _count(session, Enrollment) == 1
    second_user = session.exec(select(User).where(User.telegram_id == 2)).first()
    assert second_user is None


def test_already_enrolled_user_is_not_told_course_is_full(session):
    course = _make_course(session, capacity=1)
    _enroll(session, course, telegram_id=1)
    assert _enroll(session, course, telegram_id=1) == EnrollmentResult.ALREADY_ENROLLED


def test_course_without_capacity_is_unlimited(session):
    course = _make_course(session, capacity=None)
    results = [_enroll(session, course, telegram_id=i) for i in range(1, 4)]
    assert results == [EnrollmentResult.ENROLLED] * 3


def test_unknown_course_creates_nothing(session):
    ghost = Course(id=999, title="ghost")  # never added to the database
    assert _enroll(session, ghost) == EnrollmentResult.COURSE_NOT_FOUND
    assert _count(session, User) == 0