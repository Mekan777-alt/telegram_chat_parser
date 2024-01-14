from aiogram.utils import executor
from config import dp, db, client
import logging
import bot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


async def on_startup(dp):
    db.create_tables()
    print("Aiogram Bot has been started")


async def on_shutdown(dp):
    print("Aiogram Bot has been stopped")


if __name__ == "__main__":
    client.start()
    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup)
