"""Inline keyboard builders."""
from sqlmodel import Session, select
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.db import engine
from database.models import Course


def get_courses_keyboard() -> InlineKeyboardMarkup:
    """Build an inline keyboard with one button per available course.

    Each button's callback_data is ``course_<id>``, which the
    course-selection callback handler parses.
    """
    keyboard = InlineKeyboardMarkup()

    with Session(engine) as session:
        courses = session.exec(select(Course)).all()
        for course in courses:
            keyboard.add(
                InlineKeyboardButton(
                    text=course.title,
                    callback_data=f"course_{course.id}",
                )
            )

    return keyboard