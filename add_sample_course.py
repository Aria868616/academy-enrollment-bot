"""Seed the database with sample courses.

Safe to run more than once: a course is added only if no course with the
same title exists yet. Tables are created automatically if missing.

Usage:
    python add_sample_course.py
"""
from sqlmodel import Session, select

from database.db import create_db_and_tables, engine
from database.models import Course

# capacity=None means "no limit". Edit this list to match your own courses.
SAMPLE_COURSES = [
    {
        "title": "دوره آموزش پایتون مقدماتی",
        "description": "آشنایی با مفاهیم پایه‌ی پایتون و حل تمرین‌های عملی",
        "price": 1_500_000,
        "capacity": 30,
    },
    {
        "title": "دوره آموزش پایتون پیشرفته",
        "description": "شی‌گرایی، مدیریت خطا، تست‌نویسی و ساختار پروژه",
        "price": 2_500_000,
        "capacity": 20,
    },
    {
        "title": "دوره ساخت ربات تلگرام با پایتون",
        "description": "ساخت ربات کاربردی با دیتابیس و مدیریت وضعیت مکالمه",
        "price": 2_000_000,
        "capacity": 15,
    },
    {
        "title": "دوره آموزش SQL و پایگاه داده",
        "description": "طراحی جدول، کوئری‌نویسی و کار با ORM",
        "price": 1_800_000,
        "capacity": 25,
    },
    {
        "title": "دوره آموزش Git و GitHub",
        "description": "کار تیمی، شاخه‌بندی و ساخت پورتفولیو",
        "price": 0,
        "capacity": None,
    },
    {
        "title": "دوره آموزش HTML و CSS مقدماتی",
        "description": "ساخت صفحه‌ی وب ساده و واکنش‌گرا",
        "price": 1_200_000,
        "capacity": 40,
    },
]


def seed_courses() -> None:
    create_db_and_tables()

    added = 0
    skipped = 0
    with Session(engine) as session:
        for data in SAMPLE_COURSES:
            exists = session.exec(
                select(Course).where(Course.title == data["title"])
            ).first()
            if exists:
                skipped += 1
                continue

            session.add(Course(**data))
            added += 1

        session.commit()

    print(f"Done: {added} course(s) added, {skipped} already existed.")


if __name__ == "__main__":
    seed_courses()