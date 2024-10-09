import os
import asyncio
from typing import Callable, Any, Awaitable, Union, List
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InputMediaPhoto, InputFile, ContentType as CT, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.dispatcher.middlewares.base import BaseMiddleware

API_TOKEN = '7711727581:AAEL8YB_328vTktLPYLoLYrL4fhj9ZxbXSI'
ADMIN_CHANNEL_ID = '-1002309097650'
PHOTO_SAVE_PATH = 'user_photo'
PAYMENT_ENABLED = False  # Set to True if payments are required

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()  # For state management
dp = Dispatcher(storage=storage)


# Middleware для обробки медіа-альбомів
class AlbumMiddleware(BaseMiddleware):
    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        self.latency = latency

    async def __call__(self, handler: Callable[[Message, dict], Awaitable[Any]], message: Message, data: dict):
        if not message.media_group_id:
            return await handler(message, data)

        try:
            self.album_data[message.media_group_id].append(message)
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            data['_is_last'] = True
            data["album"] = self.album_data[message.media_group_id]
            await handler(message, data)

        if message.media_group_id and data.get("_is_last"):
            del self.album_data[message.media_group_id]
            del data['_is_last']


dp.message.middleware(AlbumMiddleware())  # Регістрація middleware

class Form(StatesGroup):
    waiting_for_photos = State()


@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    if PAYMENT_ENABLED:
        await bot.send_invoice(
            message.chat.id,
            title="Avatar Generation Service",
            description="Pay 250 Telegram stars for avatar generation.",
            payload="avatar-generation",
            provider_token='',
            currency="XTR",
            prices=[types.LabeledPrice(label="Avatar Generation", amount=250)],
            start_parameter="avatar-generation",
            is_flexible=False
        )
    else:
        await message.answer(
            "Welcome! We offer avatar generation services.\n"
            "Price: 250 Telegram stars.\n"
            "Please send 5-10 photos to start."
        )
        await state.set_state(Form.waiting_for_photos)


@dp.message(F.content_type.in_([CT.PHOTO]))
async def handle_photos(message: Message, state: FSMContext, album: List[Message] = None):
    saved_photos = []

    if album:
        for i, msg in enumerate(album):
            file_info = await bot.get_file(msg.photo[-1].file_id)
            file_name = f"{message.from_user.id}_{i}.jpg"
            file_path = os.path.join(PHOTO_SAVE_PATH, file_name)

            if not os.path.exists(PHOTO_SAVE_PATH):
                os.makedirs(PHOTO_SAVE_PATH)

            # Завантаження фото
            await bot.download_file(file_info.file_path, file_path)
            saved_photos.append(file_name)
    else:
        # Якщо це одиничне фото, обробляємо його
        file_info = await bot.get_file(message.photo[-1].file_id)
        file_name = f"{message.from_user.id}_0.jpg"
        file_path = os.path.join(PHOTO_SAVE_PATH, file_name)

        if not os.path.exists(PHOTO_SAVE_PATH):
            os.makedirs(PHOTO_SAVE_PATH)

        await bot.download_file(file_info.file_path, file_path)
        saved_photos.append(file_name)

    # Надсилаємо повідомлення адміністратору
    await bot.send_message(
        ADMIN_CHANNEL_ID,
        f"User {message.from_user.username} has sent photos for avatar generation."
    )
    # Надсилаємо фото адміністратору
    for photo_name in saved_photos:
        photo_path = os.path.join(PHOTO_SAVE_PATH, photo_name)
        with open(photo_path, 'rb') as photo_file:
            input_file = FSInputFile(photo_path)  # Створюємо InputFile з файлу
            await bot.send_photo(ADMIN_CHANNEL_ID, input_file, caption=f'User {message.from_user.first_name} has sent photo to generate')
    await message.reply("Your photos have been successfully saved and sent to the admins.")
    await state.clear()


async def main():
    if not os.path.exists(PHOTO_SAVE_PATH):
        os.makedirs(PHOTO_SAVE_PATH)

    # Запускаємо бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
