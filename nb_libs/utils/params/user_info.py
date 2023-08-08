""" .user_infoファイル操作クラス
"""

import os
import json
from ..path import path as p
from ..common import common


FILE_PATH = os.path.join(p.SYS_PATH, '.user_info.json')


def get_user_id():
    """$HOME/.user_infoからユーザーIDを取得する。

    RETURN
    -----------------
    user_id : str
        Description : ユーザーID
    """
    with open(FILE_PATH, 'r') as f:
        data = json.load(f)
    user_id = data['user_id']
    return user_id


def set_user_info(user_id):
    """
    ユーザー情報を.user_info.jsonに登録する。

    Parameters
    ---------------
    name : str
        Description : ユーザー名
    """

    user_info = {"user_id":user_id}
    common.create_json_file(FILE_PATH, user_info)