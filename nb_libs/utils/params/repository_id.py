""" .repository_idファイル操作クラス
"""

import os
from ..path import path as p


file_path = os.path.join(p.HOME_PATH, '.repository_id')


def get_repo_id()->str:
    """$HOME/.repository_idからリポジトリIDを取得する。

    RETURN
    -----------------
    repo_id : str
        Description : リポジトリID
    """
    with open(file_path, 'r') as f:
        repo_id = f.read()
    return repo_id
