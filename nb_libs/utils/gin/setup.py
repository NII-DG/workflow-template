"""ローカルの初期セットアップ用"""
import os
from ..common import common


def datalad(dir_path:str):
    """dataladのデータセット化する

    Args:
        path (str): データセット化するディレクトリのパス
    """
    if os.path.isdir(os.path.join(dir_path, ".datalad")):
        common.exec_subprocess(cmd=f'datalad create --force {dir_path}')






