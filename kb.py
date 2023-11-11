from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import json
from user import Timetable

with open("questions.json", "r", encoding='UTF-8') as f:
    question_list = json.load(f)
print(question_list)


def get_question_list_kb(uid):
    qlist_kb = InlineKeyboardMarkup(row_width=1)
    for q in question_list.keys():
        qlist_kb.insert(InlineKeyboardButton(text=q, callback_data="answer|" + q))
    return qlist_kb


def get_Timetable_kb(day="0"):
    kb = InlineKeyboardMarkup(row_width=1)
    if day == '0':
        for key in Timetable.keys():
            flag = False
            print(Timetable)
            for value in Timetable[key].values():
                if value == "Свободно":
                    flag = True
            if flag:
                kb.insert(InlineKeyboardButton(text=key, callback_data="day|" + str(key)))
    else:
        for key in Timetable[day].keys():
            if Timetable[day][key] == "Свободно":
                kb.insert(InlineKeyboardButton(text=key, callback_data="time|" + str(key) + "|" + str(day)))
    return kb

def get_admin_kb(uid):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.insert(InlineKeyboardButton(text="Одобрить", callback_data="acp|" + str(uid)))
    kb.insert(InlineKeyboardButton(text="Отказать", callback_data="dec|" + str(uid)))

    return kb
