from aiogram import Router, F
from aiogram.types import (
    Message, KeyboardButton, ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from db.database import get_db_pool

router = Router()

class AddCategoryState(StatesGroup):
    waiting_for_name = State()

class AddExpenseState(StatesGroup):
    waiting_for_category = State()
    waiting_for_amount = State()
    waiting_for_description = State()

class ConfirmDeleteState(StatesGroup):
    waiting_for_confirmation = State()

@router.message(Command("add_category"))
async def cmd_add_category(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅ Назад")]],
        resize_keyboard=True
    )
    await message.answer("Введите название новой категории:", reply_markup=markup)
    await state.set_state(AddCategoryState.waiting_for_name)

@router.message(AddCategoryState.waiting_for_name, F.text.lower() == "⬅ назад")
async def cancel_add_category(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добавление категории отменено.", reply_markup=ReplyKeyboardRemove())

@router.message(AddCategoryState.waiting_for_name)
async def process_category_name(message: Message, state: FSMContext):
    category_name = message.text.strip()
    pool = get_db_pool()

    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id FROM app.users WHERE telegram_id = $1", message.from_user.id)
        if not user:
            await message.answer("Сначала используйте /start")
            return
        user_id = user["id"]

        await conn.execute(
            "INSERT INTO app.categories (user_id, name) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            user_id, category_name
        )

    await message.answer(f"Категория «{category_name}» добавлена ✅", reply_markup=ReplyKeyboardRemove())
    await state.clear()

# --- /add_expense ---

@router.message(Command("add_expense"))
async def cmd_add_expense(message: Message, state: FSMContext):
    pool = get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id FROM app.users WHERE telegram_id = $1", message.from_user.id)
        if not user:
            await message.answer("Сначала используйте /start")
            return
        user_id = user["id"]

        categories = await conn.fetch(
            "SELECT id, name FROM app.categories WHERE user_id = $1 ORDER BY name", user_id
        )

        if not categories:
            await message.answer("У вас ещё нет категорий. Добавьте через /add_category")
            return

        buttons = [[KeyboardButton(text=cat["name"])] for cat in categories]
        markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

        await state.set_data({
            "user_id": user_id,
            "categories": {cat["name"]: cat["id"] for cat in categories}
        })

        await message.answer("Выберите категорию:", reply_markup=markup)
        await state.set_state(AddExpenseState.waiting_for_category)



@router.message(AddExpenseState.waiting_for_category)
async def process_expense_category(message: Message, state: FSMContext):
    data = await state.get_data()
    category_name = message.text.strip()

    if category_name not in data["categories"]:
        await message.answer("Такой категории нет. Выберите из списка.")
        return

    await state.update_data(category_id=data["categories"][category_name])

    # Клавиатура с кнопкой Отмена
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅ Отмена")]],
        resize_keyboard=True
    )

    await message.answer("Введите сумму траты в рублях:", reply_markup=markup)
    await state.set_state(AddExpenseState.waiting_for_amount)


@router.message(AddExpenseState.waiting_for_amount, F.text.lower() == "⬅ отмена")
async def cancel_expense_amount(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добавление траты отменено.", reply_markup=ReplyKeyboardRemove())


@router.message(AddExpenseState.waiting_for_amount)
async def process_expense_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите положительное число или нажмите ⬅ Отмена.")
        return

    await state.update_data(amount=amount)

    # Клавиатура с кнопкой "Пропустить"
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅ Пропустить"), KeyboardButton(text="⬅ Отмена")]],
        resize_keyboard=True
    )

    await message.answer("Введите описание траты (например, «Обед», «Такси»):", reply_markup=markup)
    await state.set_state(AddExpenseState.waiting_for_description)


@router.message(AddExpenseState.waiting_for_description, F.text.lower() == "⬅ отмена")
async def cancel_expense_description(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добавление траты отменено.", reply_markup=ReplyKeyboardRemove())

@router.message(AddExpenseState.waiting_for_description, F.text.lower() == "⬅ пропустить")
async def skip_expense_description(message: Message, state: FSMContext):
    await save_expense_and_finish(message, state, description="")

@router.message(AddExpenseState.waiting_for_description)
async def process_expense_description(message: Message, state: FSMContext):
    description = message.text.strip()
    await save_expense_and_finish(message, state, description)

async def save_expense_and_finish(message: Message, state: FSMContext, description: str):
    data = await state.get_data()
    pool = get_db_pool()

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO app.expenses (user_id, category_id, amount, description, created_at)
            VALUES ($1, $2, $3, $4, now())
            """,
            data["user_id"], data["category_id"], data["amount"], description
        )

    await message.answer(
        f"Добавлена трата: {data['amount']:.2f}₽"
        + (f" — {description}" if description else ""),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(Command("delete_last"))
async def cmd_delete_last_expense(message: Message, state: FSMContext):
    pool = get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id FROM app.users WHERE telegram_id = $1", message.from_user.id)
        if not user:
            await message.answer("Сначала используйте /start")
            return

        expense = await conn.fetchrow("""
            SELECT id, amount, created_at FROM app.expenses
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT 1
        """, user["id"])

        if not expense:
            await message.answer("У вас ещё нет трат.")
            return

        await state.set_data({"expense_id": expense["id"]})
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")]
            ],
            resize_keyboard=True
        )
        await message.answer(
            f"Удалить последнюю трату на {expense['amount']}₽ от {expense['created_at']:%Y-%m-%d %H:%M}?",
            reply_markup=markup
        )
        await state.set_state(ConfirmDeleteState.waiting_for_confirmation)

@router.message(ConfirmDeleteState.waiting_for_confirmation, F.text.in_(["✅ Да", "❌ Нет"]))
async def confirm_delete_expense(message: Message, state: FSMContext):
    if message.text == "✅ Да":
        data = await state.get_data()
        pool = get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM app.expenses WHERE id = $1", data["expense_id"])
        await message.answer("Последняя трата удалена ✅", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Удаление отменено.", reply_markup=ReplyKeyboardRemove())
    await state.clear()
