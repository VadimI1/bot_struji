import asyncio
import os

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from telebot import types
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from aiogram.dispatcher.filters.state import State, StatesGroup
from pathlib import Path

from bd import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent

#load_dotenv(BASE_DIR /"Test/bot_struji/.env")
load_dotenv()

bot = Bot(token=os.environ.get('TOKEN'))
# Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    # Но явное лучше неявного =]
dp = Dispatcher(bot, storage=MemoryStorage())

class SG(StatesGroup):
    prom_code = State()
    info = State()
    promcode_inf = State()
    promcode_editing = State()
    users_editing = State()
    new_promocode = State()
    name = State()
    phone = State()

markup_user = ReplyKeyboardMarkup()
markup_admin = ReplyKeyboardMarkup()

btn1 = KeyboardButton("Ввести промокод")
btn2 = KeyboardButton("Мой баланс")
btn3 = KeyboardButton("Информация о боте")


btn4 = KeyboardButton("Добавить новый промокод")
btn5 = KeyboardButton("Рассылка информации")
btn6 = KeyboardButton("Просмотр промокодов")
btn7 = KeyboardButton("Редактировать промокод")
btn8 = KeyboardButton("Просмотр пользователей")
btn9 = KeyboardButton("Редактировать пользователя")
btn10 = KeyboardButton("Закрыть сезон")

markup_user.add(btn1, btn2, btn3)
markup_admin.add(btn4, btn5, btn6,btn7, btn8, btn9, btn10)

promcode_info, promcode_ed = '', ''

@dp.message_handler(commands=['start'])
async def start_bot(message):
    bd = bd_connect(os.environ.get('HOST'), os.environ.get('USERS'), os.environ.get('PASSWORD'),
                    os.environ.get('DB_NAME'))
    id = bd.sql_execute_get(
        f"SELECT \"ID\" FROM \"Пользователи\" WHERE \"id_messages\" = '{message.from_user.id}'")
    if not id:#проверка есть ли пользователь в БД
        await bot.send_message(message.chat.id, 'Введите ваше имя',
                               reply_markup=markup_user)
        await SG.name.set()

    bd.bd_close()

@dp.message_handler(state=SG.name)
async def set_name(message: types.Message, state: FSMContext):
    global name
    name = message.text
    await state.finish()
    await bot.send_message(message.chat.id, 'Введите ваш номер телефона')
    await SG.phone.set()

@dp.message_handler(state=SG.phone)
async def set_phone(message: types.Message, state: FSMContext):
    global phone
    phone = message.text
    await state.finish()
    keyboard = InlineKeyboardMarkup()  # наша клавиатура
    key_yes = InlineKeyboardButton(text='Да', callback_data='yes_registration')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = InlineKeyboardButton(text='Нет', callback_data='no_registration')
    keyboard.add(key_no)
    question = f'Ваше имя: {name}\nВаш номер телефона: {phone}?'
    await bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

@dp.message_handler(commands=['admin'])
async def start_bot(message):
    bd = bd_connect(os.environ.get('HOST'), os.environ.get('USERS'), os.environ.get('PASSWORD'),
                    os.environ.get('DB_NAME'))
    id = bd.sql_execute_get(
        f"SELECT \"ID\", \"Статус\" FROM \"Пользователи\" WHERE \"id_messages\" = '{message.from_user.id}'")
    bd.bd_close()
    if id:
        if id[0][1]:#проверка есть ли пользователь в БД
            await bot.send_message(message.chat.id, "Режим администратора включен.", reply_markup=markup_admin)
        else:
            await bot.send_message(message.chat.id, "У вас нет прав администратора.", reply_markup=markup_user)
    else:
        await bot.send_message(message.chat.id, "Напишите \"/start\" для регистрации.", reply_markup=markup_user)


@dp.message_handler(content_types=['text'])
async def text_message(message):
    bd = bd_connect(os.environ.get('HOST'), os.environ.get('USERS'), os.environ.get('PASSWORD'),
                    os.environ.get('DB_NAME'))

    id = bd.sql_execute_get(f"SELECT \"Статус\", \"Баланс\" FROM \"Пользователи\" WHERE \"id_messages\" = '{message.from_user.id}'")
    if id:
        if "Ввести промокод" in message.text:
            await bot.send_message(message.chat.id, "Введите промокод или слово \"Отмена\" для отмены ввода промокода.", reply_markup=markup_user)
            await SG.prom_code.set()
        elif "Мой баланс" in message.text:
            await bot.send_message(message.chat.id,
                                   f"Ваш баланс составляет: {id[0][1]}", reply_markup=markup_user)
        elif "Информация о боте" in message.text:
            await bot.send_message(message.chat.id,
                                   f"test", reply_markup=markup_user)

        elif "Рассылка информации" in message.text and id[0][0]:
            await bot.send_message(message.chat.id,f"Введите сообщение для рассылки или слово \"Отмена\" для отмены рассылки.", reply_markup=markup_admin)
            await SG.info.set()
        elif "Просмотр промокодов" in message.text and id[0][0]:
            promotional_codes = bd.sql_execute_get(f"SELECT \"Промокод\", \"Баллы\", \"Статус\" FROM \"Промокоды\"")
            for promotional_code in promotional_codes:
                await bot.send_message(message.chat.id, promotional_code,
                                       reply_markup=markup_admin)
        elif "Редактировать промокод" in message.text and id[0][0]:
            await bot.send_message(message.chat.id,
                                   f"Введите промокод для редактирования или слово \"Отмена\" для отмены редактирования.",
                                   reply_markup=markup_admin)
            await SG.promcode_inf.set()
        elif "Просмотр пользователей" in message.text and id[0][0]:
            users = bd.sql_execute_get(f"SELECT \"id_messages\", \"Имя\", \"Номер телефона\", \"Использованные промокоды\", \"Баланс\", \"Статус\" FROM \"Пользователи\"")
            for user in users:
                await bot.send_message(message.chat.id, user,
                                       reply_markup=markup_admin)
        elif "Редактировать пользователя" in message.text and id[0][0]:
            await bot.send_message(message.chat.id,
                                   f"Введите id пользователя и новый баланс для редактирования через пробел или слово \"Отмена\" для отмены редактирования.",
                                   reply_markup=markup_admin)
            await SG.users_editing.set()
        elif "Закрыть сезон" in message.text and id[0][0]:
            keyboard = InlineKeyboardMarkup()  # наша клавиатура
            key_yes = InlineKeyboardButton(text='Да', callback_data='yes_delete')  # кнопка «Да»
            keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
            key_no = InlineKeyboardButton(text='Нет', callback_data='no_delete')
            keyboard.add(key_no)
            await bot.send_message(message.from_user.id, text=f"Вы уверены что хотите закрыть сезон?"
                                   , reply_markup=keyboard)
        elif "Добавить новый промокод" in message.text and id[0][0]:
            await bot.send_message(message.chat.id,
                                   f"Введите новый промокод в формате (промокод, баллы) "
                                   f"через пробел или слово \"Отмена\" для отмены создания нового промокода.",
                                   reply_markup=markup_admin)
            await SG.new_promocode.set()
    else:
        await bot.send_message(message.chat.id, "Напишите \"/start\" для регистрации.", reply_markup=markup_user)
    bd.bd_close()

@dp.message_handler(state=SG.new_promocode)
async def create_promocode(message: types.Message, state: FSMContext):
    global promocod_new
    promocod_new = message.text
    await state.finish()
    keyboard = InlineKeyboardMarkup()  # наша клавиатура
    key_yes = InlineKeyboardButton(text='Да', callback_data='yes_new_prom')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = InlineKeyboardButton(text='Нет', callback_data='no_new_prom')
    keyboard.add(key_no)
    await bot.send_message(message.from_user.id, text=f"Данные нового промокода:\n"
                                                      f"{promocod_new}"
                           , reply_markup=keyboard)
    promocod_new = promocod_new.split("\n")

@dp.message_handler(state=SG.users_editing)
async def edit_user(message: types.Message, state: FSMContext):
    global user_edit
    user_edit = message.text
    await state.finish()
    if not "Отмена" in user_edit:
        user_edit = user_edit.split(" ")
        keyboard = InlineKeyboardMarkup()  # наша клавиатура
        key_yes = InlineKeyboardButton(text='Да', callback_data='yes_ed_user')  # кнопка «Да»
        keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
        key_no = InlineKeyboardButton(text='Нет', callback_data='no_ed_user')
        keyboard.add(key_no)
        await bot.send_message(message.from_user.id, text=f"Данные для изменения {user_edit[0]}: "
                                                          f"Новые баллы - {user_edit[1]}"
                               , reply_markup=keyboard)



@dp.message_handler(state=SG.promcode_inf)
async def promcode_status(message: types.Message, state: FSMContext):
    global promcode_info
    promcode_info = message.text
    await state.finish()
    if not "Отмена" in promcode_info:
        bd = bd_connect(os.environ.get('HOST'), os.environ.get('USERS'), os.environ.get('PASSWORD'),
                        os.environ.get('DB_NAME'))
        ids = bd.sql_execute_get(f"SELECT * FROM \"Промокоды\" WHERE \"Промокод\" = '{promcode_info}'")
        if ids:
            await bot.send_message(message.chat.id,
                                   f"Введите новую информацию о промокоде (промокод, баллы, статус"
                                   f"(True - промкод активен, False - промокод недействителен)) через пробел или слово \"Отмена\" для отмены рассылки.",
                                   reply_markup=markup_admin)
            await SG.promcode_editing.set()
        else:
            await bot.send_message(message.chat.id,f"Данного промокода нет в системе.", reply_markup=markup_admin)
        bd.bd_close()

@dp.message_handler(state=SG.promcode_editing)
async def promcode_edit(message: types.Message, state: FSMContext):
    global promcode_info, promcode_ed
    promcode_ed = message.text
    await state.finish()
    if not "Отмена" in promcode_ed:
        promcode_ed = promcode_ed.split(" ")
        keyboard = InlineKeyboardMarkup()  # наша клавиатура
        key_yes = InlineKeyboardButton(text='Да', callback_data='yes_ed_prom')  # кнопка «Да»
        keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
        key_no = InlineKeyboardButton(text='Нет', callback_data='no_ed_prom')
        keyboard.add(key_no)
        await bot.send_message(message.from_user.id, text=f"Данные для изменения {promcode_info}: "
                                                          f"промокод - {promcode_ed[0]}, баллы - {promcode_ed[1]}, статус - {promcode_ed[2]}"
                               , reply_markup=keyboard)


@dp.message_handler(state=SG.info)
async def newsletter(message: types.Message, state: FSMContext):
    global info
    info = message.text
    await state.finish()
    if not "Отмена" in info:
        keyboard = InlineKeyboardMarkup()  # наша клавиатура
        key_yes = InlineKeyboardButton(text='Да', callback_data='yes_info')  # кнопка «Да»
        keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
        key_no = InlineKeyboardButton(text='Нет', callback_data='no_info')
        keyboard.add(key_no)
        await bot.send_message(message.from_user.id, text=f"Текс оповещения: {info}", reply_markup=keyboard)

@dp.message_handler(state=SG.prom_code)
async def checking_promotional_code(message: types.Message, state: FSMContext):
    promotional_code_user = message.text
    await state.finish()
    if not "Отмена" in promotional_code_user:
        bd = bd_connect(os.environ.get('HOST'), os.environ.get('USERS'), os.environ.get('PASSWORD'),
                        os.environ.get('DB_NAME'))
        user = bd.sql_execute_get(f"SELECT \"Использованные промокоды\", \"Баланс\" FROM \"Пользователи\" WHERE "
                                              f"\"id_messages\" = '{message.from_user.id}'")
        promotional_code = bd.sql_execute_get(f"SELECT \"Статус\", \"Баллы\" FROM \"Промокоды\" WHERE "
                                              f"\"Промокод\" = '{promotional_code_user}'")

        if promotional_code:
            if promotional_code[0][0]:
                if user[0][0]:
                    bd.sql_execute(f"UPDATE \"Пользователи\" SET \"Баланс\" = {user[0][1] + promotional_code[0][1]}, "
                                   f"\"Использованные промокоды\" = '{user[0][0] + ' ' + promotional_code_user}' "
                                   f"WHERE \"id_messages\" = '{message.from_user.id}'")
                else:
                    bd.sql_execute(f"UPDATE \"Пользователи\" SET \"Баланс\" = {user[0][1] + promotional_code[0][1]}, "
                                   f"\"Использованные промокоды\" = '{promotional_code_user}' "
                                   f"WHERE \"id_messages\" = '{message.from_user.id}'")

                bd.sql_execute(f"UPDATE \"Промокоды\" SET \"Статус\" = {False} "
                               f"WHERE \"Промокод\" = '{promotional_code_user}'")
                await bot.send_message(message.chat.id, "Промокод успешно активирован.", reply_markup=markup_user)
            else:
                await bot.send_message(message.chat.id, "Данный промокод уже недействителен.", reply_markup=markup_user)
        else:
            await bot.send_message(message.chat.id, "Данного промокода нет в системе.", reply_markup=markup_user)
        bd.bd_close()

@dp.callback_query_handler(lambda call: True)
async def callback_worker(call):
    global promcode_ed, user_edit
    if call.data == "yes_info": #call.data это callback_data, которую мы указали при объявлении кнопки
        bd = bd_connect(os.environ.get('HOST'), os.environ.get('USERS'), os.environ.get('PASSWORD'),
                        os.environ.get('DB_NAME'))
        ids = bd.sql_execute_get(f"SELECT \"id_messages\" FROM \"Пользователи\"")
        bd.bd_close()
        for id in ids:
            print(id)
            await bot.send_message(id[0], text=info)
        await bot.send_message(call.message.chat.id, "Рассылка завершена.", reply_markup=markup_admin)
    elif call.data == "no_info":
        await bot.send_message(call.message.chat.id, "Рассылка отменена.", reply_markup=markup_admin)

    elif call.data == "yes_ed_prom": #call.data это callback_data, которую мы указали при объявлении кнопки
        bd = bd_connect(os.environ.get('HOST'), os.environ.get('USERS'), os.environ.get('PASSWORD'),
                        os.environ.get('DB_NAME'))
        try:
            bd.sql_execute(f"UPDATE \"Промокоды\" SET \"Промокод\" = '{promcode_ed[0]}', \"Баллы\" = {promcode_ed[1]}, "
                           f"\"Статус\" = {promcode_ed[2]} "
                           f"WHERE \"Промокод\" = '{promcode_info}'")
            await bot.send_message(call.message.chat.id, f"Промокод успешно изменен.", reply_markup=markup_admin)
        except:
            await bot.send_message(call.message.chat.id, f"Неверно указаны данные для изменения промокода.",
                                   reply_markup=markup_admin)
        bd.bd_close()
    elif call.data == "no_ed_prom":
        await bot.send_message(call.message.chat.id, "Изменение промокода отменена.", reply_markup=markup_admin)

    elif call.data == "yes_ed_user": #call.data это callback_data, которую мы указали при объявлении кнопки

        try:
            bd = bd_connect(os.environ.get('HOST'), os.environ.get('USERS'), os.environ.get('PASSWORD'),
                            os.environ.get('DB_NAME'))
            ids = bd.sql_execute_get(f"SELECT * FROM \"Пользователи\" WHERE \"id_messages\" = '{user_edit[0]}'")
            if ids:
                bd.sql_execute(f"UPDATE \"Пользователи\" SET \"Баланс\" = {user_edit[1]} "
                               f"WHERE \"id_messages\" = '{user_edit[0]}'")
                await bot.send_message(call.message.chat.id, f"Данные успешно изменены.", reply_markup=markup_admin)
            else:
                await bot.send_message(call.message.chat.id, f"Данного пользователя нет в системе.",
                                       reply_markup=markup_admin)
        except:
            await bot.send_message(call.message.chat.id, f"Неверно указаны данные для изменения данных пользователя.",
                                   reply_markup=markup_admin)
    elif call.data == "no_ed_user":
        await bot.send_message(call.message.chat.id, "Изменения пользователя отменено.", reply_markup=markup_admin)

    elif call.data == "yes_delete": #call.data это callback_data, которую мы указали при объявлении кнопки

        bd = bd_connect(os.environ.get('HOST'), os.environ.get('USERS'), os.environ.get('PASSWORD'),
                        os.environ.get('DB_NAME'))
        bd.sql_execute(f"UPDATE \"Пользователи\" SET \"Баланс\" = {0}")
        bd.sql_execute(f"UPDATE \"Промокоды\" SET \"Статус\" = {False}")
        bd.bd_close()
        await bot.send_message(call.message.chat.id, "Сезон закрыт.", reply_markup=markup_admin)
    elif call.data == "no_delete":
        await bot.send_message(call.message.chat.id, "Закрытие сезона отменено.", reply_markup=markup_admin)

    elif call.data == "yes_new_prom": #call.data это callback_data, которую мы указали при объявлении кнопки
        bd = bd_connect(os.environ.get('HOST'), os.environ.get('USERS'), os.environ.get('PASSWORD'),
                        os.environ.get('DB_NAME'))
        try:
            for pr_nw in promocod_new:
                pr_nw = pr_nw.split(" ")
                ids = bd.sql_execute_get(f"SELECT \"ID\" FROM \"Промокоды\" WHERE \"Промокод\" = '{pr_nw[0]}'")
                if not ids:
                    bd.sql_execute( f"INSERT INTO \"Промокоды\" (\"Промокод\", \"Баллы\", \"Статус\") "
                    f"VALUES ('{pr_nw[0]}', {pr_nw[1]}, {True})")
                    await bot.send_message(call.message.chat.id, f"Промокод {pr_nw[0]} добавлен.", reply_markup=markup_admin)
                else:
                    await bot.send_message(call.message.chat.id, f"Промокод {pr_nw[0]} уже существует.", reply_markup=markup_admin)
        except:
            await bot.send_message(call.message.chat.id, f"Неверно указаны данные для добавления нового промокода.",
                                   reply_markup=markup_admin)
    elif call.data == "no_new_prom":
        await bot.send_message(call.message.chat.id, "Отмена добавления промокода.", reply_markup=markup_admin)


    elif call.data == "yes_registration": #call.data это callback_data, которую мы указали при объявлении кнопки
        bd = bd_connect(os.environ.get('HOST'), os.environ.get('USERS'), os.environ.get('PASSWORD'),
                        os.environ.get('DB_NAME'))
        bd.sql_execute(
            "INSERT INTO \"Пользователи\" (\"id_messages\", \"Имя\", \"Номер телефона\", \"Баланс\", \"Статус\") "
            f"VALUES ({call.message.chat.id}, '{name}', '{phone}', {0}, {False})")
        await bot.send_message(call.message.chat.id, "Регистрация прошла успешно.", reply_markup=markup_user)

    elif call.data == "no_registration":
        await bot.send_message(call.message.chat.id, "Отмена регистрации.", reply_markup=markup_user)


async def main():
    bd = bd_connect(os.environ.get('HOST'), os.environ.get('USERS'), os.environ.get('PASSWORD'),
                    os.environ.get('DB_NAME'))
    bd.setup()
    bd.bd_close()
    await dp.start_polling(bot)


asyncio.run(main())