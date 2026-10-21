"""Handlers for the course enrollment flow.

Flow: /start -> course selection (inline button) -> full name -> phone number.
Temporary conversation data lives in the FSM storage and is written to the
database only after the last step succeeds.
"""
import html
import logging


from sqlmodel import Session, select
from telebot import types
from telebot.states import State, StatesGroup
from telebot.states.sync.context import StateContext

from database.db import engine
from database.enrollment import EnrollmentResult, enroll_user
from database.keyboards.inline import get_courses_keyboard
from database.models import Course, Enrollment, User
from loader import bot
from phone import PHONE_PATTERN, is_valid_phone, normalize_phone  # noqa: F401
logger = logging.getLogger(__name__)


GENERIC_ERROR_TEXT = "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید."

RESULT_MESSAGES = {
    EnrollmentResult.ENROLLED: "🎉 ثبت‌نام شما در دوره مورد نظر با موفقیت انجام شد!",
    EnrollmentResult.ALREADY_ENROLLED: "⚠️ شما پیش از این در این دوره ثبت‌نام کرده‌اید!",
    EnrollmentResult.COURSE_FULL: (
        "😕 ظرفیت این دوره تکمیل شده است.\n"
        "برای انتخاب دوره‌ی دیگر از /start استفاده کنید."
    ),
    EnrollmentResult.COURSE_NOT_FOUND: (
        "⚠️ این دوره دیگر وجود ندارد. لطفاً با /start دوباره شروع کنید."
    ),
}


def _is_plain_text(message: types.Message) -> bool:
    """True for ordinary text, False for commands such as /my_courses.

    Used on the FSM step handlers so that a command typed in the middle of
    the flow is not stored as the user's name or phone number.
    """
    return bool(message.text) and not message.text.startswith("/")


class enrolling(StatesGroup):
    """Conversation steps of the enrollment flow."""

    full_name = State()
    phone_number = State()


@bot.message_handler(commands=["cancel"])
def cancel(message, state: StateContext):
    state.delete()
    bot.send_message(message.chat.id, "فرآیند لغو شد.")


@bot.message_handler(commands=["start"])
def starting(message, state: StateContext):
    # Drop any leftover state from a previous, unfinished flow.
    state.delete()

    bot.send_message(
        message.chat.id,
        "سلام! خوش آمدید. 🌸\nلطفاً از لیست زیر دوره‌ی مورد نظر خود را انتخاب کنید:",
        reply_markup=get_courses_keyboard(),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("course_"))
def process_course_selection(call: types.CallbackQuery, state: StateContext):
    course_id = int(call.data.split("_")[1])

    # Set the state first: in the pyTelegramBotAPI version used here,
    # state.set() on a fresh state discards data stored just before it.
    state.set(enrolling.full_name)

    with state.data() as data:
        data["course_id"] = course_id

    bot.answer_callback_query(call.id, "دوره با موفقیت انتخاب شد.")
    bot.send_message(
        call.message.chat.id,
        "لطفاً نام و نام خانوادگی خود را وارد کنید 👤:",
    )


@bot.message_handler(state=enrolling.full_name, func=_is_plain_text)
def process_full_name(message, state: StateContext):
    with state.data() as data:
        data["full_name"] = message.text

    state.set(enrolling.phone_number)
    bot.send_message(message.chat.id, "لطفاً شماره تماس خود را وارد کنید 📱:")


@bot.message_handler(state=enrolling.phone_number, func=_is_plain_text)
@bot.message_handler(state=enrolling.phone_number, func=_is_plain_text)
def process_phone_number(message, state: StateContext):
    phone = normalize_phone(message.text)

    if not is_valid_phone(phone):
        bot.send_message(
            message.chat.id,
            "❌ شماره تماس نامعتبر است. لطفاً شماره را به شکل صحیح وارد کنید (مثلاً 09123456789):",
        )
        return

    with state.data() as data:
        full_name = data.get("full_name")
        course_id = data.get("course_id")

    if not course_id:
        bot.send_message(
            message.chat.id,
            "⚠️ دوره‌ای انتخاب نشده است. لطفاً با /start دوباره شروع کنید.",
        )
        state.delete()
        return

    try:
        with Session(engine) as session:
            result = enroll_user(
                session,
                telegram_id=message.from_user.id,
                full_name=full_name,
                phone=phone,
                course_id=course_id,
            )
    except Exception:
        # The state is kept so the user can simply resend the phone number.
        logger.exception("Enrollment failed for telegram_id=%s", message.from_user.id)
        bot.send_message(message.chat.id, GENERIC_ERROR_TEXT)
        return

    bot.send_message(message.chat.id, RESULT_MESSAGES[result])
    state.delete()


@bot.message_handler(commands=["my_courses"])
def get_user_courses(message, state: StateContext):
    try:
        with Session(engine) as session:
            db_user = session.exec(
                select(User).where(User.telegram_id == message.from_user.id)
            ).first()

            if not db_user:
                bot.send_message(
                    message.chat.id,
                    "❌ شما هنوز فرآیند ثبت‌نام اولیه را انجام نداده‌اید. لطفاً با دستور /start شروع کنید.",
                )
                return

            enrollments = session.exec(
                select(Enrollment).where(Enrollment.user_id == db_user.id)
            ).all()

            titles = []
            for enrollment in enrollments:
                course = session.get(Course, enrollment.course_id)
                if course:
                    titles.append(course.title)
    except Exception:
        logger.exception("Failed to load courses for telegram_id=%s", message.from_user.id)
        bot.send_message(message.chat.id, GENERIC_ERROR_TEXT)
        return

    if not titles:
        bot.send_message(
            message.chat.id,
            "📭 شما در حال حاضر در هیچ دوره‌ای ثبت‌نام نکرده‌اید.",
        )
        return

    # HTML with escaping is safer than Markdown: a title containing "_" or "*"
    # would otherwise make Telegram reject the message.
    lines = [f"{index}. <b>{html.escape(title)}</b>" for index, title in enumerate(titles, 1)]
    text = "📚 <b>دوره‌هایی که شما در آن‌ها ثبت‌نام کرده‌اید:</b>\n\n" + "\n".join(lines)
    bot.send_message(message.chat.id, text, parse_mode="HTML")


# Keep this handler LAST: telebot checks handlers in registration order, so this
# catch-all only runs when no other handler matched the message.
@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "متوجه پیام شما نشدم 🤔\nبرای شروع ثبت‌نام از دستور /start استفاده کنید.",
    )