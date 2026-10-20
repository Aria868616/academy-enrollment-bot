"""Database models for the enrollment bot.

Three tables: users, courses, and enrollments. The enrollments table is a
join table modelling the many-to-many relationship between users and courses.
"""
from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


def _utcnow() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """A Telegram user who has registered with the bot."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True, index=True)
    full_name: str
    phone: str
    joined_at: datetime = Field(default_factory=_utcnow)

    enrollments: List["Enrollment"] = Relationship(back_populates="user")


class Course(SQLModel, table=True):
    """A course users can enroll in."""

    __tablename__ = "courses"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = Field(default=None)
    price: Optional[int] = Field(default=0)
    capacity: Optional[int] = Field(default=None)

    enrollments: List["Enrollment"] = Relationship(back_populates="course")


class Enrollment(SQLModel, table=True):
    """Join table linking a user to a course."""

    __tablename__ = "enrollments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    course_id: int = Field(foreign_key="courses.id")
    enrolled_at: datetime = Field(default_factory=_utcnow)

    user: User = Relationship(back_populates="enrollments")
    course: Course = Relationship(back_populates="enrollments")