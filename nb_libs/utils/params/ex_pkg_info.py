import os
import json
from ..path import path


FILE_PATH = os.path.join(path.SYS_PATH, 'ex_pkg_info.json')


def get_current_experiment_title():
    '''現在実験中の実験パッケージ名を取得する

    Arg:
        なし
    Return:
        現在実験中の実験パッケージ名 (初期設定が未完了の場合はNone)
    '''
    try:
        with open(FILE_PATH, mode='r') as f:
            return json.load(f)['ex_pkg_name']
    except Exception:
        return None


def set_current_experiment_title(title):
    """現在実験中の実験パッケージ名を設定する

    Args:
        title: 実験中の実験パッケージ名

    Raises:
        FileNotFoundError: ファイルが存在しない場合
    """
    title_dict = {"ex_pkg_name":title}
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    with open(FILE_PATH, 'w') as f:
        json.dump(title_dict, f, indent=4)


def exist_file()->bool:
    """ex_pkg_info.jsonファイルの存在確認

    Returns:
        bool: [True : 存在する, False : 存在しない]
    """
    return os.path.exists(FILE_PATH)