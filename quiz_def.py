import text
import aiosqlite
import config
import text
from keyboards.for_quiz import generate_options_keyboard

async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = text.quiz_data[current_question_index]['correct_option']
    opts = text.quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{text.quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
     user_id = message.from_user.id
     current_question_index = 0
     current_val_correct_answer = 0
     current_val_incorrect_answer = 0
     await update_correct_quiz_statistics(user_id, current_val_correct_answer)
     await update_incorrect_quiz_statistics(user_id, current_val_incorrect_answer)
     await update_quiz_index(user_id, current_question_index)
     await get_question(message, user_id)


async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(config.DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(config.DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        # Сохраняем изменения
        await db.commit()
############################ 
async def update_incorrect_quiz_statistics(user_id, val_incorrect_answer):
    async with aiosqlite.connect(config.DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_statistics_incor (user_id, val_incorrect_answer) VALUES (?, ?)', (user_id, val_incorrect_answer))
        await db.commit()

async def update_correct_quiz_statistics(user_id, val_correct_answer):
    async with aiosqlite.connect(config.DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_statistics_cor (user_id, val_correct_answer) VALUES (?, ?)', (user_id, val_correct_answer))
        await db.commit()

#Получение статистики правильных ответов 
async def get_correct_answer_stat(user_id):
    async with aiosqlite.connect(config.DB_NAME) as db:
        async with db.execute('SELECT val_correct_answer FROM quiz_statistics_cor WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

#Получение статистики НЕправильных ответов            
async def get_incorrect_answer_stat(user_id):
    async with aiosqlite.connect(config.DB_NAME) as db:
        async with db.execute('SELECT val_incorrect_answer FROM quiz_statistics_incor WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

###########################

async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(config.DB_NAME) as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        # создаем таблицу статистики
        # await db.execute('''CREATE TABLE IF NOT EXISTS quiz_statistics (user_id INTEGER PRIMARY KEY, val_correct_answer INTEGER, val_incorrect_answer INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_statistics_cor (user_id INTEGER PRIMARY KEY, val_correct_answer INTEGER)''')
        
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_statistics_incor (user_id INTEGER PRIMARY KEY, val_incorrect_answer INTEGER)''')
        # Сохраняем изменения
        await db.commit()

