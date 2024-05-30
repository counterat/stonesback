from aiogram import Bot, Dispatcher, types 
from aiogram.utils import executor
import logging
from config import *
from aiogram.types import ParseMode
from templatemessages import messages as templatemessages
from inlinekeyboards import inline_keyboards
import re
# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем объект бота и диспетчера
bot = Bot(token=API_TOKEN_FOR_TGBOT)
dp = Dispatcher(bot)

def extract_username(link):
    # Регулярное выражение для извлечения имени пользователя из ссылки
    match = re.search(r'https://t\.me/([a-zA-Z0-9_]+)', link)
    if match:
        return match.group(1)
    else:
        return None
async def get_chat_title(link):
    username = extract_username(link)
    chat = await bot.get_chat(username)
    return chat.title

async def is_user_in_channel(user_id, channel):
    try:
        chat_member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return chat_member
    except Exception as ex:
        print(ex)

""" @dp.message_handler()
async def handler(message:types.Message):
    chat = await bot.get_chat(official_channel_id)
    await message.answer(f'{chat}')

    chat_member = await bot.get_chat_member(chat_id=official_channel_id, user_id=871704893)
    await message.answer(f'{chat_member}') """

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    referal_code = message.get_args()
    if  not referal_code:
        referal_code = ''
    return await message.answer(templatemessages['start_message'](message.from_user.id, message.from_user.first_name), parse_mode=ParseMode.MARKDOWN,
                          reply_markup=inline_keyboards['start_message'](referal_code))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)