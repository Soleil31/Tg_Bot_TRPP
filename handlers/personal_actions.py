from aiogram import types
from dispatcher import dp
from aiogram.types import ReplyKeyboardMarkup   
import config
import re
from main import BotDB


@dp.message_handler(commands="start")
async def start(message: types.Message):
    if (not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)

    await message.bot.send_message(message.from_user.id, "Привет!")


@dp.message_handler(commands=("spent", "earned", "s", "e"), commands_prefix="/!")
async def start(message: types.Message):
    cmd_variants = (('/spent', '/s', '!spent', '!s'), ('/earned', '/e', '!earned', '!e'))
    """Определение типа операции"""
    operation = '-' if message.text.startswith(cmd_variants[0]) else '+'

    value = message.text
    for i in cmd_variants:
        for j in i:
            """Отбрасывание команды для сохранения только числа"""
            value = value.replace(j, '').strip()

    if (len(value)):
        """Число проходит через регулярное выражение чтобы спарсить суммы из ввода пользователя с учетом точки или 
        запятой """
        x = re.findall(r"\d+(?:.\d+)?", value)
        if (len(x)):
            value = float(x[0].replace(',', '.'))

            BotDB.add_record(message.from_user.id, operation, value)

            if (operation == '-'):
                await message.reply("✅ Запись о <u><b>расходе</b></u> успешно внесена!")
            else:
                await message.reply("✅ Запись о <u><b>доходе</b></u> успешно внесена!")
        else:
            await message.reply("Не удалось определить сумму!")
    else:
        await message.reply("Не введена сумма!")


@dp.message_handler(commands=("history", "h"), commands_prefix="/!")
async def start(message: types.Message):
    cmd_variants = ('/history', '/h', '!history', '!h')
    within_als = {
        "day": ('today', 'day', 'сегодня', 'день'),
        "month": ('month', 'месяц'),
        "year": ('year', 'год'),
    }

    cmd = message.text
    for r in cmd_variants:
        cmd = cmd.replace(r, '').strip()

    within = 'day'
    if (len(cmd)):
        for k in within_als:
            for als in within_als[k]:
                if (als == cmd):
                    within = k

    records = BotDB.get_records(message.from_user.id, within)

    if (len(records)):
        answer = f"🕘 История операций за {within_als[within][-1]}\n\n"

        for r in records:
            answer += "<b>" + ("➖ Расход" if not r[2] else "➕ Доход") + "</b>"
            answer += f" - {r[3]}"
            answer += f" <i>({r[4]})</i>\n"

        await message.reply(answer)
    else:
        await message.reply("Записей не обнаружено!")
