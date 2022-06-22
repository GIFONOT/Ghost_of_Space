import csv
import pandas as pd
import json

global obj


def write(data, fileName):
    data = json.dumps(data)
    data = json.loads(str(data))
    with open(fileName, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def read(fileName):
    with open(fileName, "r", encoding="utf-8") as file:
        return json.load(file)


def sort_file(user):
    file = read('Scored.json')
    obj = file
    obj[user.Record] = {user.Name: user.Record}
    sorted_tuple = sorted(file.items(), key=lambda x: int(x[0]))
    obj = dict(sorted_tuple)
    return obj


class user:
    def __init__(self, Name, rec):
        self.Name = Name
        self.Record = rec


def write_rec(user):
    obj = sort_file(user)
    write(obj, 'Scored.json')


def giv_rec():
    file = read('Scored.json')
    obj = file
    return obj



print( giv_rec())
