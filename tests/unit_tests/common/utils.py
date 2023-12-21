import json
import os
import pathlib
import shutil

from requests.exceptions import HTTPError


class MockResponse:
    """requestsモジュールのモック用レスポンスクラス"""

    def __init__(self, status_code=200, json={}):
        self.__status_code = status_code
        self.__json = json

    @property
    def status_code(self):
        return self.__status_code

    def json(self):
        return self.__json

    def raise_for_status(self):
        if self.__status_code >= 400:
            raise HTTPError('dummy message', response=self)


class UnitTestError(Exception):
    """テスト用の例外クラス"""
    pass


class FileUtil:
    """ファイル操作クラス"""

    path: str = None
    """ファイルパス"""

    def __init__(self, path: str):
        self.path = path

    def __str__(self) -> str:
        return self.path

    def exists(self) -> bool:
        return os.path.isfile(self.path)

    def create(self, data: str = None):
        self.create_parent()

        if data is None:
            pathlib.Path(self.path).touch()
        else:
            with open(self.path, mode='w') as f:
                f.write(data)

    def create_json(self, data: dict):
        self.create_parent()

        with open(self.path, mode='w') as f:
            json.dump(data, f, indent=4)

    def create_parent(self):
        dir_parent = DirUtil(pathlib.Path(self.path).parent)
        if not dir_parent.exists():
            dir_parent.create()

    def read(self) -> str:
        with open(self.path, mode='r') as f:
            return f.read()

    def read_json(self):
        with open(self.path, mode='r') as f:
            return json.load(f)

    def copy(self, new_path: str):
        shutil.copy2(self.path, new_path)
        return FileUtil(new_path)

    def move(self, new_path: str):
        shutil.move(self.path, new_path)
        return FileUtil(new_path)

    def delete(self):
        if self.exists():
            os.remove(self.path)


class DirUtil:
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self.path

    def exists(self):
        return os.path.isdir(self.path)

    def children(self):
        return os.listdir(self.path)

    def create(self):
        os.makedirs(self.path, exist_ok=True)

    def delete(self):
        if self.exists():
            shutil.rmtree(self.path)
