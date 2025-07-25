from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
from db import database as db

router = Router()

# Русские месяцы (номер → название)
RUS_MONTHS = {
    1: "Январь", 2: "Февраль", 3: "Март",
    4: "Апрель", 5: "Май", 6: "Июнь",
    7: "Июль", 8: "Август", 9: "Сентябрь",
    10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}


def get_month_selector_keyboard(months_count=6) -> InlineKeyboardMarkup:
    now = datetime.now()
    buttons = []

    for i in range(months_count):
        month_date = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        text = f"{RUS_MONTHS[month_date.month]} {month_date.year}"
        callback_data = f"report_{month_date.year}_{month_date.month}"
        buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))

    # Разбиваем на строки по 3 кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        buttons[i:i + 3] for i in range(0, len(buttons), 3)
    ])
    # Добавляем кнопку Отмена
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="report_cancel")
    ])
    return keyboard


@router.message(F.text == "/report")
async def cmd_report(message: Message):
    kb = get_month_selector_keyboard()
    await message.answer("Выберите месяц для отчета:", reply_markup=kb)


@router.callback_query(F.data.startswith("report_"))
async def process_report_month(callback: CallbackQuery):
    data = callback.data
    if data == "report_cancel":
        await callback.message.edit_text("Отчет отменён ❌")
        await callback.answer()
        return

    # Пример: report_2024_7
    _, year, month = data.split("_")
    year, month = int(year), int(month)

    telegram_id = callback.from_user.id

    # Получаем доходы и расходы
    benefits = await db.get_monthly_benefits_report(telegram_id, year, month)
    expenses = await db.get_monthly_expenses_report(telegram_id, year, month)

    # Формируем текст отчета
    lines = [f"📅 Отчет за {RUS_MONTHS[month]} {year}"]

    if benefits:
        lines.append("\n💰 Доходы:")
        for row in benefits:
            day = int(row["day"])
            amount = float(row["total_amount"])
            lines.append(f"{day:02d}: {amount:.2f} ₽")
    else:
        lines.append("\n💰 Доходы: отсутствуют")

    if expenses:
        lines.append("\n💸 Расходы по категориям:")
        for row in expenses:
            cat = row["category_name"]
            amount = float(row["total_amount"])
            lines.append(f"{cat}: {amount:.2f} ₽")
    else:
        lines.append("\n💸 Расходы: отсутствуют")

    await callback.message.edit_text("\n".join(lines))
    await callback.answer()
