"""通信系のエラー"""


class RepositoryNotExist(Exception):
    """リモートリポジトリの情報が取得できない時のエラー"""
    pass


class UrlUpdateError(Exception):
    """HTTPとSSHのリモートURLが最新化できなかった時のエラー"""
    pass


class Unauthorized(Exception):
    """認証が通らなかった時のエラー"""
    pass