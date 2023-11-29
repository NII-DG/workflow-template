from requests import HTTPError


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
