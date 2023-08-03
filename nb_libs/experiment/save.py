'''save.ipynbから呼び出されるモジュール'''
from ..utils.path import path
from ..utils.ex_utils import save_util


def input_message():
    '''データの格納先を入力するフォームを出力する'''

    save_util.input_message(path.SAVE_JSON_PATH)


def prepare_sync() -> dict:
    '''同期の準備を行う

    Raises:
        DGTaskError: 実験フローのセットアップが完了していない場合
        DidNotFinishError: jsonファイルが存在しない場合

    Returns:
        dict: syncs_with_repoの引数が入った辞書
    '''

    return save_util.prepare_sync(path.SAVE_JSON_PATH, path.SAVE)
