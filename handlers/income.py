from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from db.database import add_benefit

router = Router()

class IncomeStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_description = State()

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[{"text": "❌ Отмена"}]],
    resize_keyboard=True
)

@router.message(Command("add_income"))
async def cmd_add_income(message: Message, state: FSMContext):
    await message.answer("Введите сумму дохода:", reply_markup=cancel_keyboard)
    await state.set_state(IncomeStates.waiting_for_amount)

@router.message(IncomeStates.waiting_for_amount, F.text.casefold() == "отмена")
@router.message(IncomeStates.waiting_for_description, F.text.casefold() == "отмена")
async def cancel_income(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добавление дохода отменено.", reply_markup=ReplyKeyboardRemove())

@router.message(IncomeStates.waiting_for_amount)
async def process_income_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError()
    except ValueError:
        await message.answer("Пожалуйста, введите корректное положительное число.")
        return

    await state.update_data(amount=amount)
    await state.set_state(IncomeStates.waiting_for_description)
    await message.answer("Описание:", reply_markup=cancel_keyboard)

@router.message(IncomeStates.waiting_for_description)
async def process_income_description(message: Message, state: FSMContext):
    description = message.text.strip()
    data = await state.get_data()
    amount = data.get("amount")
    user_id = message.from_user.id

    await add_benefit(user_id, amount, description)
    await message.answer(f"Доход {amount:.2f} ₽ с описанием '{description}' добавлен!", reply_markup=ReplyKeyboardRemove())
    await state.clear()
