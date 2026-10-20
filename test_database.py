import pytest
from sqlmodel import SQLModel, create_engine, Session, select
from database.models import User, Course, Enrollment

@pytest.fixture
def session():
    # 🧪 ایجاد یک دیتابیس موقت و ایزوله در حافظه رم فقط برای مدت زمان تست
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_create_user_and_course(session: Session):
    # 👤 تست ثبت کاربر
    user = User(full_name="کاربر تستی", phone="09123456789", telegram_id=12345678)
    session.add(user)
    
    # 📚 تست ثبت دوره
    course = Course(title="آموزش پیشرفته FastAPI")
    session.add(course)
    session.commit()

    # 🔍 بررسی ذخیره شدن در دیتابیس
    saved_user = session.exec(select(User).where(User.telegram_id == 12345678)).first()
    saved_course = session.exec(select(Course).where(Course.title == "آموزش پیشرفته FastAPI")).first()

    assert saved_user is not None
    assert saved_user.full_name == "کاربر تستی"
    assert saved_course is not None
    assert saved_course.title == "آموزش پیشرفته FastAPI"

def test_prevent_duplicate_enrollment(session: Session):
    # 🏗️ آماده‌سازی داده‌های اولیه
    user = User(full_name="علی رضایی", phone="09111111111", telegram_id=987654)
    course = Course(title="پایتون مقدماتی")
    session.add(user)
    session.add(course)
    session.commit()

    # 🔗 ثبت‌نام اولیه کاربر در دوره (باید موفق باشد)
    enrollment1 = Enrollment(user_id=user.id, course_id=course.id)
    session.add(enrollment1)
    session.commit()

    # 🛡️ بررسی منطق جلوگیری از ثبت‌نام تکراری
    existing_enrollment = session.exec(
        select(Enrollment).where(
            Enrollment.user_id == user.id,
            Enrollment.course_id == course.id
        )
    ).first()

    # چون این رکورد از قبل وجود دارد، باید پیدا شود
    assert existing_enrollment is not None
    
    # شبیه‌سازی شرط ربات: اگر رکورد موجود بود، اجازه ثبت‌نام مجدد داده نشود
    can_enroll = existing_enrollment is None
    assert can_enroll == False