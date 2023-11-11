import atexit
import os
import asyncio

import kb
from kb import question_list, get_question_list_kb, get_admin_kb
from user import register, users, is_registered, save, Timetable
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import CallbackQuery, InputFile, InputMediaPhoto, ContentType, MediaGroup
from dotenv import load_dotenv
from aiogram.dispatcher import filters

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
admin = int(os.getenv('ADMIN'))
dp = Dispatcher(bot, loop=asyncio.get_event_loop())


@dp.message_handler(commands=['start'])
async def on_command_start(message: types.Message):
    uid = int(message.from_user.id)
    await bot.send_message(uid, "Привет, я помогу вам получить ответы на базовые вопросы по психологии"
                                " и записаться на прием к квалифицированному специалисту")


@dp.message_handler(commands=['register'])
async def reg(message: types.Message):
    uid = int(message.chat.id)
    users["awaiting_name"][uid] = True
    await bot.send_message(uid, "Пожалуйста, отправьте Ваше ФИО следующим сообщением")


@dp.message_handler(commands="help")
async def help(message: types.Message):
    uid = int(message.chat.id)
    if not is_registered[uid]:
        await bot.send_message(uid, "Пожалуйста, пройдите процедуру регистрации")
        return
    mesg = await bot.send_message(uid, "Что Вас волнует?", reply_markup=get_question_list_kb(uid))
    users["last_kb"][uid] = mesg.message_id


@dp.callback_query_handler(text_startswith="answer|")
async def ans(call: types.CallbackQuery):
    uid = int(call.message.chat.id)
    await bot.send_message(uid, question_list[call.data.split('|')[1]])
    await bot.delete_message(uid, users["last_kb"][uid])


@dp.message_handler(commands="record")
async def record(message: types.Message):
    uid = int(message.chat.id)
    if not is_registered[uid]:
        await bot.send_message(uid, "Пожалуйста, пройдите процедуру регистрации")
        return
    if not users["accepted"][uid]:
        await bot.send_message(uid, "Пожалуйста, дождитесь проверки регистрации модератором")
        return
    await bot.send_message(uid, "Пожалуйста, выберете интересующее Вас время", reply_markup=kb.get_Timetable_kb())


@dp.callback_query_handler(text_startswith="day|")
async def recordtime(call: types.CallbackQuery):
    day = call.data.split("|")[1]
    await call.message.edit_reply_markup(kb.get_Timetable_kb(day))


@dp.callback_query_handler(text_startswith="time|")
async def recordtim(call: types.CallbackQuery):
    time, day = call.data.split("|")[1], call.data.split("|")[2]
    await call.message.delete_reply_markup()
    await bot.send_message(call.message.chat.id, "Для подтверждения записи, укажите, какие у вас жалобы в следующем сообщении")
    users["awaiting_question"] = f"{time}|{day}"


@dp.callback_query_handler(text_startswith="acp|")
async def accept(call: types.CallbackQuery):
    uid = int(call.data.split("|")[1])
    users["accepted"][uid] = True
    await bot.send_message(uid, "Ваша заявка на регистрацию одобрена. Теперь вы можете записаться на прием")
    await call.message.delete_reply_markup()


@dp.callback_query_handler(text_startswith="dec|")
async def accept(call: types.CallbackQuery):
    uid = call.data.split("|")[1]
    users["accepted"][uid] = False
    await bot.send_message(uid, "К сожалению, ваша заявка отклонена. Пройдите процедуру регистрации заново")
    await call.message.delete_reply_markup()


@dp.message_handler(text_startswith="/add_date")
async def add_date(message: types.message):
    uid = int(message.chat.id)
    if uid != admin:
        return
    command = message.text.split()
    if command[1] not in Timetable:
        Timetable[command[1]] = dict()
    Timetable[command[1]][command[2]] = "Свободно"


@dp.message_handler(commands='get_timetable')
async def get_timetable(message: types.Message):
    await bot.send_message(admin, str(Timetable))


@dp.message_handler(content_types=['text'])
async def proccesing_messages(message: types.Message):
    global users
    uid = int(message.chat.id)
    if users["awaiting_name"][uid]:
        users["awaiting_name"][uid] = False
        await dp.loop.create_task(register(uid, message.text))
        await bot.send_message(admin, f"{users['real_names'][uid]} запрашивает регистрацию", reply_markup=get_admin_kb(uid))
        await bot.send_message(uid, "Ваш запрос отправлен модератору")
        return
    if users["awaiting_question"] != "0":
        time, day = users["awaiting_question"].split("|")
        Timetable[day][time] = users["real_names"][uid] + ":" + message.text
        await bot.send_message(uid, f"Вы записаны на консультацию к психологу на {day} {time}. Будем ждать Вас по адресу проспект Ленина 33, 116 кабинет 😌")
        return

    await bot.send_message(uid, "Сообщение не распознано")


if __name__ == '__main__':
    atexit.register(save)
    executor.start_polling(dp)
