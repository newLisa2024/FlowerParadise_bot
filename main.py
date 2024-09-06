import aiohttp
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from config import TOKEN, API_PRODUCTS_URL, API_ORDERS_URL

logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Создание кнопок
button_start = KeyboardButton(text="/start")
button_catalog = KeyboardButton(text="/catalog")
button_order = KeyboardButton(text="/order")
button_order_history = KeyboardButton(text="/order_history")

# Создание клавиатуры (две строки по две кнопки)
keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [button_start, button_catalog],
    [button_order, button_order_history]
])

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Это бот для заказа цветов.", reply_markup=keyboard)

# Обработчик команды /catalog
@router.message(Command("catalog"))
async def send_catalog(message: types.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_PRODUCTS_URL) as response:
                if response.status == 200:
                    products = await response.json()
                    for product in products:
                        catalog_message = f"<b>{product['name']}</b>: {product['price']} руб.\n"
                        if product['image_url']:
                            await bot.send_photo(
                                chat_id=message.chat.id,
                                photo=product['image_url'],
                                caption=catalog_message,
                                parse_mode="HTML"
                            )
                        else:
                            await message.answer(catalog_message, parse_mode="HTML")
                else:
                    await message.answer(f"Ошибка при получении каталога: {response.status}", reply_markup=keyboard)
                    logging.error(f"Ошибка при получении каталога: {response.status}")
    except Exception as e:
        await message.answer(f"Ошибка при получении каталога: {str(e)}", reply_markup=keyboard)
        logging.error(f"Ошибка: {str(e)}")

# Обработчик команды /order
@router.message(Command("order"))
async def get_orders(message: types.Message):
    user_id = message.from_user.id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{API_ORDERS_URL}?user={user_id}', headers={'Authorization': f'Token {TOKEN}'}) as response:
                if response.status == 200:
                    orders = await response.json()
                    if orders:
                        for order in orders:
                            order_message = (
                                f"Заказ №{order['id']} на сумму {order['total_price']} руб.\n"
                                f"Статус: {order['status']}\n"
                                f"Адрес доставки: {order['delivery_address'] or 'не указан'}"
                            )
                            await message.answer(order_message, reply_markup=keyboard)
                    else:
                        await message.answer("У вас нет заказов.", reply_markup=keyboard)
                elif response.status == 404:
                    await message.answer("Заказы не найдены.", reply_markup=keyboard)
                else:
                    await message.answer(f"Ошибка при получении заказов: {response.status}", reply_markup=keyboard)
                    logging.error(f"Ошибка при получении заказов: {response.status}")
    except Exception as e:
        await message.answer(f"Ошибка при получении заказов: {str(e)}", reply_markup=keyboard)
        logging.error(f"Ошибка: {str(e)}")

# Обработчик команды /order_history
@router.message(Command("order_history"))
async def get_order_history(message: types.Message):
    user_id = message.from_user.id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{API_ORDERS_URL}?user={user_id}&status=completed', headers={'Authorization': f'Token {TOKEN}'}) as response:
                if response.status == 200:
                    orders = await response.json()
                    if orders:
                        for order in orders:
                            order_message = (
                                f"Заказ №{order['id']} на сумму {order['total_price']} руб.\n"
                                f"Статус: {order['status']}\n"
                                f"Адрес доставки: {order['delivery_address'] or 'не указан'}"
                            )
                            await message.answer(order_message, reply_markup=keyboard)
                    else:
                        await message.answer("У вас нет завершённых заказов.", reply_markup=keyboard)
                elif response.status == 404:
                    await message.answer("Завершённые заказы не найдены.", reply_markup=keyboard)
                else:
                    await message.answer(f"Ошибка при получении истории заказов: {response.status}", reply_markup=keyboard)
                    logging.error(f"Ошибка при получении истории заказов: {response.status}")
    except Exception as e:
        await message.answer(f"Ошибка при получении истории заказов: {str(e)}", reply_markup=keyboard)
        logging.error(f"Ошибка: {str(e)}")

# Обработчик команды /test_api для проверки соединения с сервером
@router.message(Command("test_api"))
async def test_api(message: types.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_PRODUCTS_URL) as response:  # Пример проверки одного из API
                if response.status == 200:
                    await message.answer("Подключение к серверу успешно!", reply_markup=keyboard)
                else:
                    await message.answer(f"Сервер вернул ошибку: {response.status}", reply_markup=keyboard)
                    logging.error(f"Ошибка соединения с сервером: {response.status}")
    except Exception as e:
        await message.answer(f"Ошибка при попытке подключения к серверу: {str(e)}", reply_markup=keyboard)
        logging.error(f"Ошибка: {str(e)}")

# Основная функция для запуска бота
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())





















