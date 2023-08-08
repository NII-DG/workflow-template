'''おもにprepare_from_local.py, save.pyから呼び出されるモジュール'''
import os, json
from IPython.display import display, Javascript
import panel as pn
from ..path import path
from ..message import message, display as display_util
from ..common import common
from ..except_class import DidNotFinishError
from ..params import ex_pkg_info
from ..form import prepare as pre
from . import package


# 辞書のキー
COMMIT_MESSAGE = 'commit_message'


def submit_message_callback(input_form:pn.widgets.TextInput, submit_button:pn.widgets.Button, json_file_path:str):
    '''入力された格納先を検証し、ファイルに記録する

        Args:
            input_form: 入力フォーム
            submit_button: 入力完了ボタン
            json_file_path (str): コミットメッセージを保存するjsonファイルのパス
    '''


    def callback(event):
        common.delete_file(json_file_path)

        commit_message = input_form.value
        err_msg = pre.validate_commit_message(commit_message)

        if len(err_msg) > 0:
            submit_button.button_type = 'warning'
            submit_button.name = err_msg
            return

        commit_message_dict = {COMMIT_MESSAGE: commit_message}
        with open(json_file_path, 'w') as f:
            json.dump(commit_message_dict, f, indent=4)

        submit_button.button_type = 'success'
        submit_button.name = message.get('from_repo_s3', 'done_input')


    return callback


def input_message(json_file_path:str):
    '''データの格納先を入力するフォームを出力する

        Args:
            json_file_path (str): コミットメッセージを保存するjsonファイルのパス
    '''
    common.delete_file(json_file_path)

    pn.extension()

    input_form = pn.widgets.TextInput(
        name = message.get('from_repo_s3', 'log_message'),
        placeholder = message.get('from_repo_s3', 'enter_log_message'),
        width = 700
    )

    submit_button = pn.widgets.Button(name= message.get('from_repo_s3', 'end_input'), button_type= "primary", width=300)
    submit_button.on_click(submit_message_callback(input_form, submit_button, json_file_path))

    display(input_form, submit_button)


def prepare_sync(json_file_path:str, notebook_file_path:str) -> dict:
    '''同期の準備を行う

    Args:
        json_file_path (str): コミットメッセージを保存するjsonファイルのパス
        notebook_file_path (str): 同期するノートブックのパス

    Raises:
        DGTaskError: 実験フローのセットアップが完了していない場合
        DidNotFinishError: jsonファイルが存在しない場合

    Returns:
        dict: syncs_with_repoの引数が入った辞書
    '''
    display(Javascript('IPython.notebook.save_checkpoint();'))
    experiment_title = ex_pkg_info.exec_get_ex_title()
    experiment_path = path.create_experiments_with_subpath(experiment_title)

    git_path, gitannex_path, gitannex_files = package.create_syncs_path(experiment_path)
    git_path.append(os.path.join(path.EXP_DIR_PATH, notebook_file_path))

    try:
        with open(json_file_path, 'r') as f:
            commit_message = json.load(f)[COMMIT_MESSAGE]
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError from e

    sync_repo_args = dict()
    sync_repo_args['git_path'] = git_path
    sync_repo_args['gitannex_path'] = gitannex_path
    sync_repo_args['gitannex_files'] = gitannex_files
    sync_repo_args['get_paths'] = [path.create_experiments_with_subpath(experiment_title)]
    sync_repo_args['message'] = message.get('commit_message', 'from_local').format(experiment_title, commit_message)

    common.delete_file(json_file_path)

    return sync_repo_args
