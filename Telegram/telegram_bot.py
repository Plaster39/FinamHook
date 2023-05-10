from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import uuid
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from Database import database

CHAT_ID = config.CHAT_ID
bot = Bot(token=config.TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


class AddSignalStates(StatesGroup) :
    waiting_for_params = State()


def create_menu_keyboard() :
    keyboard = InlineKeyboardMarkup(row_width=1)

    add_signal_button = InlineKeyboardButton("Добавить сигнал", callback_data="add")
    remove_signal_button = InlineKeyboardButton("Удалить сигнал", callback_data="rem")
    list_signals_button = InlineKeyboardButton("Список сигналов", callback_data="list")

    keyboard.add(add_signal_button, remove_signal_button, list_signals_button)

    return keyboard


async def on_startup(dp) :
    # keyboard = create_menu_keyboard()
    message_text = (
        "Привет! Я - ФинХукМастер  , и я помогу тебе соединить сигналами  TradingView с брокером Финам. Вот список доступных команд:\n\n"
        "/add  <инструмент> ; <тип позиции> ; <размер позиции> ; <тейк-профит> ;<стоп-лосс> ;. Например: /add DSKY;Buy;1;1%;1% \n"
        "/list - показать список всех активных сигналов.\n"
        "/rem <id> - удалить сигнал для инструмента. Например: /rem 1 \n\n"
        "Когда вы добавите сигнал, я предоставлю вам хук-текст. Вам нужно скопировать этот текст и вставить его в настройки "
        "уведомлений в TradingView. Вот как это сделать:\n\n"
        "1. Откройте настройки уведомлений в TradingView.\n"
        "2. Создайте новое уведомление или отредактируйте существующее.\n"
        "3. В разделе 'Действия' выберите 'Веб-хук'.\n"
        "4. Вставьте скопированный хук-текст в поле 'URL'.\n"
        "5. Сохраните настройки уведомления.\n\n"
        "Теперь вы будете получать уведомления от меня при активации сигнала на TradingView. Удачной торговли!"
    )

    await bot.send_message(chat_id=CHAT_ID, text=message_text)


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message) :
    welcome_text = "Бот запущен"
    keyboard = create_menu_keyboard()

    await bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=keyboard)


@dp.message_handler(commands=['help'])
async def on_help(message: types.Message) :
    help_text = (
        "/add <инструмент> ; <тип позиции> ; <размер позиции> ; <тейк-профит> ;<стоп-лосс> ; - добавить сигнал \n Например: /add DSKY;Buy;1;1%;1% \n"
        "/rem <id сигнала> - удалить сигнал\n"
        "/list - список всех сигналов\n"
    )
    await message.reply(help_text)


@dp.message_handler(commands=['add'])
async def on_add_signal(message: types.Message) :
    try :
        command, params = message.text.split(' ', 1)
        instrument, position_type, amount, take_profit, stop_loss = params.split(';')
        instrument = instrument.strip()
        position_type = position_type.strip()
        amount = float(amount.strip())
        take_profit = float(take_profit.strip().replace('%', ''))
        stop_loss = float(stop_loss.strip().replace('%', ''))

    except ValueError :
        await message.reply("Некорректный формат команды. Проверьте ввод.")
        return
    unique_token = str(uuid.uuid4())  # Генерируем уникальный токен

    database.add_signal(unique_token, instrument, take_profit, stop_loss, position_type, amount)
    await message.reply(f"Сигнал добавлен для инструмента {instrument}")


@dp.message_handler(commands=['rem'])
async def on_remove_signal(message: types.Message) :
    try :
        _, signal_id = message.text.split()
        signal_id = int(signal_id)
    except ValueError :
        await message.reply("Некорректный формат команды. Проверьте ввод.")
        return

    database.remove_signal(signal_id)
    await message.reply(f"Сигнал удален")


@dp.message_handler(commands=['list'])
async def on_list_signals(message: types.Message) :
    signals = database.get_signals()

    if not signals :
        await bot.send_message(chat_id=CHAT_ID, text="Список сигналов пуст.")
    else :
        result = []
        for signal in signals :
            signal_info = f"ID: {signal['id']}\n" \
                          f"Instrument: {signal['instrument']}\n" \
                          f"Position Type: {signal['position_type']}\n" \
                          f"Amount: {signal['amount']}\n" \
                          f"Take Profit: {signal['take_profit']}%\n" \
                          f"Stop Loss: {signal['stop_loss']}%\n" \
                          f"Unique Token: {signal['unique_token']}\n" \
                          f"Вставьте ниже текст в Хук Trandingview(Нужно указать SecurityBoard):\n" \
                          f"token={signal['unique_token']}\n" \
                          f"securityBoard=TQBR\n" \
                          f"instrument={signal['instrument']}\n" \
                          f"position={signal['position_type']}\n" \
                          f"current_price=price: {{close}}\n" \
                          f"----------"
            result.append(signal_info)

        await bot.send_message(chat_id=CHAT_ID, text='\n\n'.join(result))


async def send_message_to_user(text) :
    try :
        await bot.send_message(CHAT_ID, text)
    except Exception as e :
        print(f"Error while sending message to user: {e}")


def start_bot() :
    database.init_db()
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)  # измените здесь
