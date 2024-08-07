import asyncio
import logging
from aiogram import Bot, Dispatcher
import nest_asyncio
import config
from handlers import handlers
from quiz_def import create_table

nest_asyncio.apply()
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)



# Объект бота
bot = Bot(token=config.API_TOKEN)
# Диспетчер
dp = Dispatcher()
dp.include_router(handlers.router)

# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())