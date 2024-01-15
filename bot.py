import sqlite3
from config import db, dp, admin_user_id
from aiogram.dispatcher import FSMContext
from aiogram import types
from state.state import AddTrigger, DeleteTrigger


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id == admin_user_id:
        await set_default_commands(dp)
        await message.answer(f"Список команд ниже)", parse_mode=types.ParseMode.HTML)
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("list_triggers", "Список ключевых слов"),
        types.BotCommand("add_triggers", "Добавить ключевые слова"),
        types.BotCommand("delete_trigger", "Удалить ключевое слово")
    ])


@dp.message_handler(commands=['add_triggers'])
async def add_trigger(message: types.Message):
    user_id = str(message.from_user.id)

    if user_id == admin_user_id:
        await message.answer("Введите через запятую ключевый слова\n"
                             "Пример: нужен бот, лист, привет и т.д")
        await AddTrigger.add_trigger.set()
    else:
        await message.reply("У вас нет прав для выполнения этой команды.")


@dp.message_handler(state=AddTrigger.add_trigger)
async def trigger_set(message: types.Message, state: FSMContext):
    triggers = message.text.split(', ')
    for trigger in triggers:
        db.query("INSERT INTO triggers (trigger) VALUES (?)", (trigger,))
        await message.answer(f"Триггер {trigger} добавлен в базу")
    await state.finish()


@dp.message_handler(commands=['list_triggers'])
async def list_triggers(message: types.Message):
    triggers = db.fetchall("SELECT trigger FROM triggers")
    process_data = [item[0] for item in triggers]
    await message.answer(f"Список ключевых слов:\n"
                         f"{process_data}")


@dp.message_handler(commands=['delete_trigger'])
async def process_delete(message: types.Message):
    await message.answer("Введите слово которое хотите удалить")
    await DeleteTrigger.delete_trigger.set()


@dp.message_handler(state=DeleteTrigger.delete_trigger)
async def delete_trigger(message: types.Message, state: FSMContext):
    trigger = message.text
    try:
        result = db.fetchone("SELECT * FROM triggers WHERE trigger=?", (trigger,))
        if result:
            db.query("DELETE FROM triggers WHERE trigger=?", (trigger,))
            await message.answer(f"Ключевое слово {trigger} удаленно с базы")
            await state.finish()
        else:
            await message.answer(f"Ключевое слово {trigger} не найдено в базе данных")
            await message.answer("Введите слово которое хотите удалить")
    except sqlite3.Error as e:
        await message.answer(f"Произошла ошибка базы данных: {e}")
        await state.finish()
    except Exception as e:
        await message.answer(f"Произошла неизвестная ошибка: {e}")
        await state.finish()
