import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from collections import defaultdict
import json

is_registered = defaultdict(bool)
Timetable = dict()
users = dict()
users["awaiting_name"] = dict()
users["awaiting_question"] = dict()
users["real_names"] = dict()
users["last_kb"] = dict()
users["accepted"] = dict()


async def register(uid, name):
    is_registered[uid] = True
    users["awaiting_name"][uid] = False
    users["real_names"][uid] = name
    users["last_kb"][uid] = 0
    users["accepted"][uid] = False
    users["awaiting_question"][uid] = "0"


def save():
    tmp_dict = dict()
    for key in users.keys():
        tmp = json.dumps(users[key])
        tmp_dict[key] = tmp
    with open("users.json", "w+") as f:
        json.dump(tmp_dict, f)
