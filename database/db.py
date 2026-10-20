from sqlmodel import SQLModel, create_engine, Session
from config import DB_NAME
from database.models import User, Course, Enrollment  # ایمپورت مدل‌ها برای شناخته شدن توسط اسکیما

# ایجاد موتور اتصال به دیتابیس SQLite
engine = create_engine(DB_NAME, echo=True)

def create_db_and_tables():
    """این تابع اسکیماهای تعریف‌شده را می‌خواند و جداول را در دیتابیس می‌سازد"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """تولیدکننده سشن (Session) برای ارتباط با دیتابیس در طول اجرای کوئری‌ها"""
    with Session(engine) as session:
        yield session