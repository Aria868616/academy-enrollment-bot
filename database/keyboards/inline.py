
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlmodel import select
from database.db import get_session
from database.models import Course
def get_main_menu_keyboard():
    """ساخت منوی اصلی ربات"""
    keyboard = InlineKeyboardMarkup()
    btn_courses = InlineKeyboardButton("📚 مشاهده دوره‌ها", callback_data="show_courses")
    btn_my_courses = InlineKeyboardButton("👤 دوره‌های من", callback_data="my_courses")
    keyboard.add(btn_courses, btn_my_courses)
    return keyboard

def get_courses_keyboard(courses):
    """ساخت کیبورد برای نمایش لیست دوره‌ها"""
    keyboard = InlineKeyboardMarkup()
    
    for course in courses:
        btn_course = InlineKeyboardButton(course.title, callback_data=f"course_{course.id}")
        keyboard.add(btn_course)
        
    # دکمه بازگشت به منوی اصلی
    btn_back = InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")
    keyboard.add(btn_back)
    
    return keyboard




def get_courses_keyboard():
    session = next(get_session())
    statement = select(Course)
    courses = session.exec(statement).all()
    
    keyboard = InlineKeyboardMarkup()
    for course in courses:
        # 📌 ایجاد دکمه شیشه‌ای برای هر دوره با ذخیره id در callback_data
        keyboard.add(
            InlineKeyboardButton(
                text=course.title,
                callback_data=f"course_{course.id}"
            )
        )
    return keyboard