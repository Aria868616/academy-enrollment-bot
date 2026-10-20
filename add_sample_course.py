from sqlmodel import SQLModel
from database.db import get_session, engine
from database.models import Course, User, Enrollment  # مدل‌ها باید ایمپورت شوند تا جداول شناسایی شوند

def add_course():
    # ۱. ساخت تمام جداول دیتابیس در صورت عدم وجود
    SQLModel.metadata.create_all(engine)
    print("🛠️ جداول دیتابیس با موفقیت بررسی و ساخته شدند.")

    session = next(get_session())
    
    # ۲. ساخت یک دوره تستی نمونه
    sample_course = Course(
        title="دوره آموزش پایتون مقدماتی",
        description="آموزش جامع و از صفر زبان پایتون",
        price=1000000,
        capacity=50
    )
    
    session.add(sample_course)
    session.commit()
    print("✅ دوره تستی با موفقیت به دیتابیس اضافه شد!")

if __name__ == "__main__":
    add_course()