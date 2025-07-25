from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from db.database import delete_last_benefit, get_last_benefit_for_user

router = Router()

class DeleteIncomeFSM(StatesGroup):
    waiting_for_confirmation = State()


@router.message(F.text == "/delete_last_income")
async def start_delete_income(message: Message, state: FSMContext):
    from_user = message.from_user
    try:
        benefit = await get_last_benefit_for_user(from_user.id)
        if not benefit:
            await message.answer("❗ У вас нет записей о доходах.")
            return

        await state.update_data(benefit_id=benefit["id"])
        await state.set_state(DeleteIncomeFSM.waiting_for_confirmation)

        amount = benefit["amount"]
        description = benefit["description"] or "Без описания"
        created = benefit["created_at"].strftime("%Y-%m-%d %H:%M")

        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")]
            ],
            resize_keyboard=True
        )

        await message.answer(
            f"Вы точно хотите удалить последний доход?\n"
            f"💰 {amount} ₽\n📄 {description}\n🕒 {created}",
            reply_markup=markup
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(DeleteIncomeFSM.waiting_for_confirmation, F.text == "✅ Да")
async def confirm_deletion(message: Message, state: FSMContext):
    data = await state.get_data()
    benefit_id = data.get("benefit_id")

    try:
        deleted = await delete_last_benefit(message.from_user.id)
        if deleted:
            amount = deleted["amount"]
            await message.answer(
                f"✅ Доход на {amount} ₽ удалён.", reply_markup=ReplyKeyboardRemove()
            )
        else:
            await message.answer("❗ Нечего удалять.", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await message.answer(f"❌ Ошибка удаления: {e}", reply_markup=ReplyKeyboardRemove())
    finally:
        await state.clear()


@router.message(DeleteIncomeFSM.waiting_for_confirmation, F.text == "❌ Нет")
async def cancel_deletion(message: Message, state: FSMContext):
    await message.answer("❎ Отменено.", reply_markup=ReplyKeyboardRemove())
    await state.clear()
