'''prepare_from_local.ipynbから呼び出されるモジュール'''
import json
from IPython.display import display, Javascript
import panel as pn
from ..utils.path import path
from ..utils.message import message, display as display_util
from ..utils.common import common
from ..utils.except_class import DidNotFinishError
from ..utils.params import ex_pkg_info
from ..utils.form import prepare as pre
from ..utils.ex_utils import package


# 辞書のキー
COMMIT_MESSAGE = 'commit_message'


def submit_message_callback(input_form:pn.widgets.TextInput, submit_button:pn.widgets.Button):
    '''入力された格納先を検証し、ファイルに記録する

        Args:
            input_form: 入力フォーム
            submit_button: 入力完了ボタン
    '''


    def callback(event):

        common.delete_file(path.FROM_LOCAL_JSON_PATH)

        commit_message = input_form.value
        err_msg = pre.validate_commit_message(commit_message)

        if len(err_msg) > 0:
            submit_button.button_type = 'warning'
            submit_button.name = err_msg
            return

        from_local_dict = {COMMIT_MESSAGE: commit_message}
        with open(path.FROM_LOCAL_JSON_PATH, 'w') as f:
            json.dump(from_local_dict, f, indent=4)

        submit_button.button_type = "success"
        submit_button.name = message.get('from_repo_s3', 'done_input')


    return callback


def input_message():
    '''データの格納先を入力するフォームを出力する'''

    common.delete_file(path.FROM_LOCAL_JSON_PATH)

    pn.extension()

    input_form = pn.widgets.TextInput(
        name = message.get('from_repo_s3', 'log_message'),
        placeholder = message.get('from_repo_s3', 'enter_log_message'),
        width = 700
    )

    submit_button = pn.widgets.Button(name= message.get('from_repo_s3', 'end_input'), button_type= "primary", width=300)
    submit_button.on_click(submit_message_callback(input_form, submit_button))

    display(input_form, submit_button)


def prepare_sync() -> dict:
    '''同期の準備を行う

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
    git_path.append(path.EXP_DIR_PATH + path.PREPARE_FROM_LOCAL)

    try:
        with open(path.FROM_LOCAL_JSON_PATH, 'r') as f:
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

    common.delete_file(path.FROM_LOCAL_JSON_PATH)

    return sync_repo_args
