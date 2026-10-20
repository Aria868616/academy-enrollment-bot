from telebot import types
from telebot.states import State, StatesGroup
from telebot.states.sync.context import StateContext
import re
from database.db import get_session
from database.models import User, Enrollment, Course
from sqlmodel import select
from database.keyboards.inline import get_courses_keyboard

# 📌 شیء مرکزی bot از loader.py ایمپورت می‌شود
from loader import bot


class enrolling(StatesGroup):
    full_name = State()
    phone_number = State()


@bot.message_handler(state="*", commands=["cancel"])
def cancel(message, state: StateContext):
    state.delete()
    bot.send_message(message.chat.id, "فرآیند لغو شد.")


@bot.message_handler(commands=["start"])
def starting(message, state: StateContext):
    # پاک کردن هرگونه وضعیت قبلی
    state.delete()

    bot.send_message(
        message.chat.id,
        "سلام! خوش آمدید. 🌸\nلطفاً از لیست زیر دوره‌ی مورد نظر خود را انتخاب کنید:",
        reply_markup=get_courses_keyboard()
    )


@bot.message_handler(state=enrolling.full_name)
def process_full_name(message, state: StateContext):
    with state.data() as data:
        data["full_name"] = message.text
    state.set(enrolling.phone_number)
    bot.send_message(message.chat.id, "لطفاً شماره تماس خود را وارد کنید 📱:")


@bot.message_handler(state=enrolling.phone_number)
def process_phone_number(message, state: StateContext):
    phone = message.text

    # 📱 بررسی الگوی شماره موبایل با Regex
    if not re.match(r"^09\d{9}$", phone):
        bot.send_message(
            message.chat.id,
            "❌ شماره تماس نامعتبر است. لطفاً شماره را به شکل صحیح وارد کنید (مثلاً 09123456789):"
        )
        return

    # 📂 خواندن اطلاعات از حافظه موقت FSM
    with state.data() as data:
        full_name = data.get("full_name")
        course_id = data.get("course_id")

    # ⚠️ اگر دوره‌ای انتخاب نشده باشد، پیام می‌دهیم و کار را همین‌جا تمام می‌کنیم
    if not course_id:
        bot.send_message(
            message.chat.id,
            "⚠️ دوره‌ای انتخاب نشده است. لطفاً با /start دوباره شروع کنید."
        )
        state.delete()
        return

    session = next(get_session())

    # 🔍 بررسی اینکه آیا کاربر از قبل در دیتابیس وجود دارد یا خیر
    statement = select(User).where(User.telegram_id == message.from_user.id)
    db_user = session.exec(statement).first()

    if not db_user:
        # اگر کاربر جدید است، او را می‌سازیم
        db_user = User(
            telegram_id=message.from_user.id,
            full_name=full_name,
            phone=phone
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    # 🔗 بررسی و ثبت‌نام در دوره
    existing_enrollment = session.exec(
        select(Enrollment).where(
            Enrollment.user_id == db_user.id,
            Enrollment.course_id == course_id
        )
    ).first()

    if existing_enrollment:
        bot.send_message(
            message.chat.id,
            "⚠️ شما پیش از این در این دوره ثبت‌نام کرده‌اید!"
        )
    else:
        enrollment = Enrollment(
            user_id=db_user.id,
            course_id=course_id
        )
        session.add(enrollment)
        session.commit()

        bot.send_message(
            message.chat.id,
            "🎉 ثبت‌نام شما در دوره مورد نظر با موفقیت انجام شد!"
        )

    # 🧹 پاک کردن وضعیت موقت FSM
    state.delete()


@bot.callback_query_handler(func=lambda call: call.data.startswith("course_"))
def process_course_selection(call: types.CallbackQuery, state: StateContext):
    # 🔍 استخراج شناسه دوره از callback_data
    course_id = int(call.data.split("_")[1])

    # 📂 ذخیره course_id در حافظه موقت FSM
    with state.data() as data:
        data["course_id"] = course_id

    # 🚀 تغییر وضعیت به دریافت نام
    state.set(enrolling.full_name)

    bot.answer_callback_query(call.id, "دوره با موفقیت انتخاب شد.")
    bot.send_message(
        call.message.chat.id,
        "لطفاً نام و نام خانوادگی خود را وارد کنید 👤:"
    )


@bot.message_handler(commands=["my_courses"])
def get_user_courses(message, state: StateContext):
    session = next(get_session())

    # 🔍 پیدا کردن کاربر در دیتابیس بر اساس شناسه تلگرام
    statement = select(User).where(User.telegram_id == message.from_user.id)
    db_user = session.exec(statement).first()

    if not db_user:
        bot.send_message(
            message.chat.id,
            "❌ شما هنوز فرآیند ثبت‌نام اولیه را انجام نداده‌اید. لطفاً با دستور /start شروع کنید."
        )
        return

    # 📚 استخراج تمام ثبت‌نام‌های کاربر از جدول واسط
    enrollment_statement = select(Enrollment).where(Enrollment.user_id == db_user.id)
    enrollments = session.exec(enrollment_statement).all()

    if not enrollments:
        bot.send_message(
            message.chat.id,
            "📭 شما در حال حاضر در هیچ دوره‌ای ثبت‌نام نکرده‌اید."
        )
        return

    # 📝 ساخت لیست دوره‌ها برای نمایش به کاربر
    response_text = "📚 **دوره‌هایی که شما در آن‌ها ثبت‌نام کرده‌اید:**\n\n"
    for index, enrollment in enumerate(enrollments, 1):
        course = session.get(Course, enrollment.course_id)
        if course:
            response_text += f"{index}. **{course.title}**\n"

    bot.send_message(message.chat.id, response_text, parse_mode="Markdown")