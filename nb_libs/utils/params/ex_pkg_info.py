import os
import json

from ..path import path
from ..common import common
from ..message import message as msg_mod, display as msg_display
from ..except_class import DGTaskError


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


def exec_get_ex_title():
    '''現在実験中の実験パッケージ名を取得する

    Arg:
        なし

    Return:
        現在実験中の実験パッケージ名

    Raise:
        DGTaskError: 実験フローのセットアップが完了していない場合
    '''
    experiment_title = get_current_experiment_title()
    if experiment_title is None:
        msg_display.display_err(msg_mod.get('experiment_error', 'experiment_setup_unfinished'))
        raise DGTaskError
    return experiment_title


def set_current_experiment_title(title):
    """現在実験中の実験パッケージ名を設定する

    Args:
        title: 実験中の実験パッケージ名

    Raises:
        FileNotFoundError: ファイルが存在しない場合
    """
    title_dict = {"ex_pkg_name":title}
    common.create_json_file(FILE_PATH, title_dict)


def exist_file()->bool:
    """ex_pkg_info.jsonファイルの存在確認

    Returns:
        bool: [True : 存在する, False : 存在しない]
    """
    return os.path.exists(FILE_PATH)
