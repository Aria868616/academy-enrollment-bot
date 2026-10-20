"""Admin panel handlers (phase 1: read-only statistics).

Do NOT import anything from handlers.user_handlers here. That import would
register the user handlers (including the catch-all fallback) before these
ones, and /admin would be swallowed by the fallback.
"""
import html
import logging

from sqlmodel import Session
from telebot import types

from database.admin_queries import get_course_enrollment_counts, get_overview_stats
from database.db import engine
from loader import bot

logger = logging.getLogger(__name__)

ADMIN_ERROR_TEXT = "❌ خطا در خواندن اطلاعات. جزئیات در لاگ ثبت شد."

CB_STATS = "admin:stats"
CB_COURSES = "admin:courses"


def _admin_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("📊 آمار کلی", callback_data=CB_STATS),
        types.InlineKeyboardButton("📚 ثبت‌نام‌ها به تفکیک دوره", callback_data=CB_COURSES),
    )
    return keyboard


@bot.message_handler(commands=["admin"], is_admin=True)
def admin_panel(message: types.Message):
    bot.send_message(
        message.chat.id,
        "🛠 پنل ادمین\nیکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=_admin_keyboard(),
    )


@bot.callback_query_handler(func=lambda call: call.data == CB_STATS, is_admin=True)
def admin_stats(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    try:
        with Session(engine) as session:
            stats = get_overview_stats(session)
    except Exception:
        logger.exception("Admin stats failed")
        bot.send_message(call.message.chat.id, ADMIN_ERROR_TEXT)
        return

    bot.send_message(
        call.message.chat.id,
        "📊 <b>آمار کلی</b>\n"
        f"👤 کاربران: {stats.users}\n"
        f"📚 دوره‌ها: {stats.courses}\n"
        f"📝 ثبت‌نام‌ها: {stats.enrollments}",
        parse_mode="HTML",
    )


@bot.callback_query_handler(func=lambda call: call.data == CB_COURSES, is_admin=True)
def admin_courses(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    try:
        with Session(engine) as session:
            rows = get_course_enrollment_counts(session)
    except Exception:
        logger.exception("Admin course counts failed")
        bot.send_message(call.message.chat.id, ADMIN_ERROR_TEXT)
        return

    if not rows:
        bot.send_message(call.message.chat.id, "📭 هنوز دوره‌ای ثبت نشده است.")
        return

    lines = []
    for row in rows:
        if row.capacity is None:
            usage = f"{row.enrolled} (بدون محدودیت)"
        else:
            usage = f"{row.enrolled}/{row.capacity}"
        lines.append(f"• {html.escape(row.title)}: {usage}")

    bot.send_message(
        call.message.chat.id,
        "📚 <b>ثبت‌نام‌ها به تفکیک دوره</b>\n" + "\n".join(lines),
        parse_mode="HTML",
    )