'''prepare_from_local.ipynbから呼び出されるモジュール'''
import os, json, shutil, git, glob
from json.decoder import JSONDecodeError
from ipywidgets import Text, Button, Layout
from IPython.display import display, clear_output, Javascript
import panel as pn
from datalad import api as datalad_api
from urllib import parse
from http import HTTPStatus
from requests.exceptions import RequestException
from datalad.support.exceptions import IncompleteResultsError
from ..utils.git import annex_util, git_module
from ..utils.path import path, validate
from ..utils.message import message, display as display_util
from ..utils.gin import api as gin_api, sync
from ..utils.common import common
from ..utils.except_class import DidNotFinishError, UnexpectedError
from ..utils.params import token, ex_pkg_info
from ..utils.form import prepare as pre
from ..utils.ex_utils import package


# 辞書のキー
# GINFORK_TOKEN = 'ginfork_token'
# DATASET_STRUCTURE = "datasetStructure"
# REPO_NAME = 'repo_name'
# PRIVATE = 'private'
# SSH_URL = 'ssh_url'
# HTML_URL = 'html_url'
# DATASET_STRUCTURE_TYPE = "dataset_structure"
# EX_PKG_INFO = 'ex_pkg_info'
# EX_PKG_NAME = 'ex_pkg_name'
# PARAM_EX_NAME = 'param_ex_name'
# SELECTED_DATA = 'selected_data'
# INPUT_DATA = 'input_data'
# SOURCE = 'source'
# OUTPUT_DATA = 'output_data'
# PATH_TO_URL = 'path_to_url'
# KEY = 'key'
# URLS = 'urls'
# WHEREIS = 'whereis'

COMMIT_MESSAGE = 'commit_message'


def submit_message_callback(input_form, submit_button):
    '''入力された格納先を検証し、ファイルに記録する
    '''

    def callback(event):

        commit_message = input_form.value

        if not pre.validate_commit_message(commit_message, submit_button):
            return

        from_local_dict = {COMMIT_MESSAGE: commit_message}
        with open(path.FROM_LOCAL_JSON_PATH, 'w') as f:
            json.dump(from_local_dict, f, indent=4)

        submit_button.button_type = "success"
        submit_button.name = message.get('from_repo_s3', 'done_input')

    return callback


def input_message():
    '''データの格納先を入力するフォームを出力する
    '''


    # 入力フォーム表示
    pn.extension()

    input_form = pn.widgets.TextInput(
        name = message.get('from_repo_s3', 'enter_log_message'),
        placeholder = message.get('from_repo_s3', 'enter_log_message'),
        width = 700
    )

    submit_button = pn.widgets.Button(name= message.get('from_repo_s3', 'end_input'), button_type= "primary", width=300)
    submit_button.on_click(submit_message_callback(input_form, submit_button))
    # error_message = pre.layout_error_text()

    display(input_form, submit_button)



def prepare_sync() -> dict:
    '''同期の準備を行う

    Raises:
        DidNotFinishError: _description_

    Returns:
        dict: syncs_with_repoの引数が入った辞書
    '''

    display(Javascript('IPython.notebook.save_checkpoint();'))
    experiment_title = ex_pkg_info.get_current_experiment_title()
    if experiment_title is None:
        raise

    experiment_path = path.create_experiments_with_subpath(experiment_title)

    save_path, annexed_save_path, gitannex_files = package.create_syncs_path(experiment_path)

    save_path.append(path.EXP_DIR_PATH + path.PREPARE_FROM_LOCAL)
    with open(path.FROM_LOCAL_JSON_PATH, 'r') as f:
        commit_message = json.load(f)[COMMIT_MESSAGE]

    sync_repo_args = dict()
    sync_repo_args['git_path'] = save_path
    sync_repo_args['gitannex_path'] = annexed_save_path
    sync_repo_args['gitannex_files'] = gitannex_files
    sync_repo_args['get_paths'] = [path.create_experiments_with_subpath(experiment_title)]
    sync_repo_args['message'] = message.get('commit_message', 'from_local').format(experiment_title, commit_message)

    common.delete_file(path.FROM_LOCAL_JSON_PATH)

    return sync_repo_args
