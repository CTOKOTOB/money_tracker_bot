from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import datetime
import db.database as db

router = Router()

class ReportDetailState(StatesGroup):
    choosing_category = State()
    choosing_year = State()
    choosing_month = State()

# 📌 Русские месяцы
MONTHS_RU = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]

@router.message(F.text == "/report_detail")
async def cmd_report_detail(message: Message, state: FSMContext):
    categories = await db.get_user_categories(message.from_user.id)
    if not categories:
        await message.answer("У вас нет категорий.")
        return

    buttons = [
        [InlineKeyboardButton(text=cat["name"], callback_data=f"cat_{cat['id']}")]
        for cat in categories
    ]
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_report_detail")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer("Выберите категорию для отчета:", reply_markup=kb)
    await state.set_state(ReportDetailState.choosing_category)

@router.callback_query(F.data.startswith("cat_"))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    if await state.get_state() != ReportDetailState.choosing_category:
        return

    category_id = int(callback.data.split("_")[1])
    await state.update_data(category_id=category_id)

    years = await db.get_available_years_for_category(callback.from_user.id, category_id)
    if not years:
        await callback.message.edit_text("❌ Нет трат по выбранной категории.")
        await state.clear()
        return

    buttons = [[InlineKeyboardButton(text=str(y), callback_data=f"year_{y}")] for y in years]
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_report_detail")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(ReportDetailState.choosing_year)
    await callback.message.edit_text("Выберите год:", reply_markup=kb)

@router.callback_query(F.data.startswith("year_"))
async def choose_year(callback: CallbackQuery, state: FSMContext):
    if await state.get_state() != ReportDetailState.choosing_year:
        return

    year = int(callback.data.split("_")[1])
    await state.update_data(year=year)

    buttons = [
        [InlineKeyboardButton(text=MONTHS_RU[i], callback_data=f"month_{i+1}")]
        for i in range(12)
    ]
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_report_detail")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(ReportDetailState.choosing_month)
    await callback.message.edit_text("Выберите месяц:", reply_markup=kb)

@router.callback_query(F.data.startswith("month_"))
async def choose_month(callback: CallbackQuery, state: FSMContext):
    if await state.get_state() != ReportDetailState.choosing_month:
        return

    month = int(callback.data.split("_")[1])
    data = await state.get_data()
    category_id = data["category_id"]
    year = data["year"]

    expenses = await db.get_detailed_category_expenses(
        telegram_id=callback.from_user.id,
        category_id=category_id,
        year=year,
        month=month
    )

    if not expenses:
        await callback.message.edit_text("Нет расходов по выбранной категории в этом месяце.")
    else:
        lines = []
        total = 0
        for record in expenses:
            dt = record["created_at"]
            amount = record["amount"]
            description = record["description"] or ""
            total += amount
            lines.append(f"{dt.day:02d}.{dt.month:02d}: {amount:.2f} ₽ — {description}")

        response = "\n".join(lines)
        response += f"\n\n🧾 Всего: {total:.2f} ₽"
        await callback.message.edit_text(response)

    await state.clear()

@router.callback_query(F.data == "cancel_report_detail")
async def cancel_report_detail(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Отчёт по категории отменён.")
