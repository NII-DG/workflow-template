""" .repository_idファイル操作クラス
"""

import os


def get_repo_id():
    """$HOME/.repository_idからリポジトリIDを取得する。
    RETURN
    -----------------
    repo_id : str
        Description : リポジトリID
    """
    os.chdir(os.environ['HOME'])
    file_path = '.repository_id'
    f = open(file_path, 'r')
    repo_id = f.read()
    f.close()
    return repo_id
