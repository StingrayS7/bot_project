from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import  ReplyKeyboardBuilder
from quiz_def import get_question, get_quiz_index, update_quiz_index, new_quiz, get_correct_answer_stat, update_incorrect_quiz_statistics, update_correct_quiz_statistics, get_incorrect_answer_stat
 
from aiogram import types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import text

router = Router()


@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    
    
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
   
    current_correct_answer = await get_correct_answer_stat(callback.from_user.id)

    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = text.quiz_data[current_question_index]['correct_option']
    await callback.message.answer(f"Верно! Правильный ответ: {text.quiz_data[current_question_index]['options'][correct_option]}")
    
    # Обновление номера текущего вопроса в базе данных
    current_correct_answer += 1
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)
    await update_correct_quiz_statistics(callback.from_user.id, current_correct_answer)


    if current_question_index < len(text.quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_incorrect_answer = await get_incorrect_answer_stat(callback.from_user.id)

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = text.quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f"Неправильно. Правильный ответ: {text.quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_incorrect_answer += 1
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)
    await update_incorrect_quiz_statistics(callback.from_user.id, current_incorrect_answer)


    if current_question_index < len(text.quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

# Хэндлер на команду /quiz
@router.message(F.text=="Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

# Хэндлер на команду /statistics
@router.message(Command('statistics'))
async def get_quiz_statistics(message: types.Message):
    user_id = message.from_user.id
    current_resulsts_cor = await get_correct_answer_stat(user_id)
    current_resulsts_incor = await get_incorrect_answer_stat(user_id)
    await message.answer('Ваша последняя статистика' 
                         f'\nПравильных ответов: {current_resulsts_cor}'
                         f'\nНеправильных ответов: {current_resulsts_incor}')