import json
import os

DATA = {}


def get_credentials(key: str) -> dict:
    """認証情報の取得"""

    if not DATA:
        # 認証情報読み込み
        read_credentials()

    return DATA.get(key, {})


def read_credentials():
    """認証情報ファイルの読み込み"""

    file_path = os.getenv('CREDENTIAL_PATH')
    if not file_path:
        return
    if not os.path.isfile(file_path):
        return

    with open(file_path, mode='r') as f:
        global DATA
        DATA = json.load(f)
