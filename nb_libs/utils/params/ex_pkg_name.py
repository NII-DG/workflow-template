import json
from ..path import path

def get_current_experiment_title():
    '''現在実験中の実験パッケージ名を取得する

    Arg:
        なし
    Return:
        現在実験中の実験パッケージ名 (初期設定が未完了の場合はNone)
    '''
    try:
        with open(path.PKG_INFO_PATH, mode='r') as f:
            return json.load(f)['ex_pkg_name']
    except Exception:
        return None