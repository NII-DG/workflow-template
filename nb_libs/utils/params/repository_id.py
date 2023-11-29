""" .repository_idファイル操作クラス
"""

import os
from ..path import path as p


FILE_PATH = os.path.join(p.HOME_PATH, '.repository_id')


def get_repo_id()->str:
    """$HOME/.repository_idからリポジトリIDを取得する。

    RETURN
    -----------------
    repo_id : str
        Description : リポジトリID
    """
    with open(FILE_PATH, 'r') as f:
        repo_id = f.read()
    return repo_id
