import json
from contextlib import suppress
from json import JSONDecodeError
from typing import Optional


class StaticManager:
    _file_ids = {}
    _ids_file_name = "ids.json"

    @classmethod
    def _read_file(cls, f):
        try:
            cls._file_ids = json.load(f)
        except JSONDecodeError:
            pass

    @classmethod
    def load_file_ids(cls):
        with suppress(FileNotFoundError):
            with open(cls._ids_file_name, "r") as f:
                cls._read_file(f)

    @classmethod
    def get_file_id(cls, filename: str) -> Optional[str]:
        return cls._file_ids.get(filename)

    @classmethod
    def get_file(cls, filename: str) -> bytes:
        with open(filename, "rb") as f:
            return f.read()

    @classmethod
    def _save_file_id(cls, filename: str, file_id: str):
        cls._file_ids[filename] = file_id
        with open(cls._ids_file_name, "w") as f:
            json.dump(cls._file_ids, f)

    @classmethod
    def save(cls, filename: str, file_id: str):
        if filename not in cls._file_ids:
            cls._save_file_id(filename, file_id)


StaticManager.load_file_ids()
