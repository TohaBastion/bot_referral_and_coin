import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot.models import User, CoinAccumulation
from asgiref.sync import sync_to_async
import asyncio

BOT_TOKEN = ''
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Старт бота
@dp.message(CommandStart())
async def start(message: types.Message):
    btn_ref = KeyboardButton(text='Ваше реферальне посилання')
    btn1 = KeyboardButton(text='Ваші реферали')
    btn2 = KeyboardButton(text='Почати накопичення монет')
    btn_row = [btn_ref, btn1, btn2]
    markup = ReplyKeyboardMarkup(keyboard=[btn_row], resize_keyboard=True)

    print(message.from_user.id)
    print(message.text)

    # Отримати аргументи з команди /start
    args = message.text.split()[1:]
    telegram_id = message.from_user.id
    referrer_id = args[0] if args else None
    print(f"Referrer ID: {referrer_id}")

    # Отримати або створити користувача
    user, created = await sync_to_async(User.objects.get_or_create)(
        telegram_id=telegram_id,
        defaults={'username': message.from_user.username}
    )

    # Якщо користувач новий і переданий реферальний ID
    if created and referrer_id:
        # Спробуємо знайти реферера
        try:
            referrer = await sync_to_async(User.objects.get)(telegram_id=referrer_id)
            # Додаємо реферала
            user.referral = referrer
            await sync_to_async(user.save)()  # Зберегти користувача з рефералом
            print(f"Реферал {referrer.username} успішно доданий.")
        except User.DoesNotExist:
            print("Реферал не знайдений.")

    await message.answer(
        f"Ласкаво просимо, {message.from_user.first_name}! Перевірте свої реферали або розпочніть накопичення",
        reply_markup=markup
    )


@dp.message()
async def handler(message: types.Message):
    if message.text == 'Ваше реферальне посилання':
        await get_my_ref_url(message)
    elif message.text == 'Ваші реферали':
        await show_referrals(message)
    elif message.text == 'Почати накопичення монет':
        await accumulate_coins(message)


async def get_my_ref_url(message: types.Message) -> None:
    if message.text == 'Ваше реферальне посилання':
        await message.answer(f'Ваш ID: {message.from_user.id}\nhttps://t.me/test_task_referral_bot?start={message.from_user.id}')

# Перегляд рефералів

async def show_referrals(message: types.Message) -> None:
    if message.text == 'Ваші реферали':
        print('Ваші рефрали')
        user = await sync_to_async(User.objects.get)(telegram_id=message.from_user.id)
        referrals = await sync_to_async(lambda: list(user.referrals.all()))()

        if referrals:
            referral_list = "\n".join([f"@{ref.username}" for ref in referrals])
            await message.answer(f"Твої реферали:\n{referral_list}")
        else:
            await message.answer("У тебе ще немає рефералів.")


# Накопичення монет

async def accumulate_coins(message: types.Message) -> None:
    if message.text == 'Почати накопичення монет':
        print('почати накопичення')
        user = await sync_to_async(User.objects.get)(telegram_id=message.from_user.id)
        print(user)

        # Запустити накопичування монет
        accumulation = await sync_to_async(CoinAccumulation.objects.create)(user=user)

        await message.answer("Накопичування монет почалось. Потрібно почекати 1 хвилину.")

        # Затримка на 1 хвилину
        await asyncio.sleep(60)

        # Завершити накопичення
        await sync_to_async(accumulation.stop_accumulation)()
        await message.answer("Потрібно зайти в застосунок та отримати монети.")


async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
