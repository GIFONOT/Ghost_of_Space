import json
import os
import tempfile
from pathlib import Path
from Paths import SCORES_PATH


def write(data, fileName):
    destination = Path(fileName)
    temporary = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination.parent, delete=False) as file:
            temporary = file.name
            json.dump(data, file, indent=4, ensure_ascii=False)
        os.replace(temporary, destination)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def read(fileName):
    try:
        with open(fileName, encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def giv_rec():
    data = read(SCORES_PATH)
    if not isinstance(data, dict):
        raise ValueError('Invalid score file')
    for score, names in data.items():
        int(score)
        if not isinstance(names, dict) or not all(isinstance(name, str) for name in names):
            raise ValueError('Invalid score entry')
    return data


def sort_file(player):
    data = giv_rec()
    data.setdefault(str(player.Record), {})[player.Name] = player.Record
    return dict(sorted(data.items(), key=lambda item: int(item[0])))


class user:
    def __init__(self, Name, rec):
        self.Name = Name
        self.Record = rec


def write_rec(player):
    write(sort_file(player), SCORES_PATH)
