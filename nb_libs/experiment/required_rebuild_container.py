import os
import json
import requests
import traceback

import panel as pn
from IPython.display import clear_output, display

from ..utils.common import common
from ..utils.form import prepare as pre
from ..utils.message import message as msg_mod, display as msg_display
from ..utils.params import ex_pkg_info, token
from ..utils.git import git_module
from ..utils.gin import sync, ssh, container
from ..utils.path import path as p
from ..utils.flow import module as flow
from ..utils.except_class import DidNotFinishError, Unauthorized, DGTaskError


FILE_PATH = os.path.join(p.RF_FORM_DATA_DIR, 'required_rebuild_container.json')


# ----- tmp_file handling -----
def set_params(ex_pkg_name:str):
    params_dict = {
    "ex_pkg_name" : ex_pkg_name,
    }
    common.create_json_file(FILE_PATH, params_dict)


def get_pkg_name()->str:
    with open(FILE_PATH, mode='r') as f:
            params = json.load(f)
    return params["ex_pkg_name"]


def delete_tmp_file():
    """ファイルがあれば消す"""
    common.delete_file(FILE_PATH)


def preparation_completed():
    """事前準備が完了しているかどうかを確認"""
    if not (os.path.isfile(FILE_PATH)):
        msg_display.display_err(msg_mod.get('setup_sync', 'not_entered'))
        raise DidNotFinishError


# ----- for cell -----
def display_forms():
    delete_tmp_file()
    initial_forms()


def del_build_token():
    """不要なGIN-forkトークンの削除"""
    preparation_completed()
    url = git_module.get_remote_url()

    try:
        # delete build token(only private)
        token.del_build_token_by_remote_origin_url(url)
    except requests.exceptions.RequestException:
        msg_display.display_err(msg_mod.get('build_token', 'connection_error'))
        raise
    except Exception:
        raise


def datalad_create():
    """ローカルをdataladデータセット化する"""
    preparation_completed()
    sync.datalad_create(p.HOME_PATH)


def ssh_create_key():
    """SSH keyの作成"""
    preparation_completed()
    ssh.create_key()


def upload_ssh_key():
    """GIN-frokへ公開鍵の登録"""
    preparation_completed()
    ssh.upload_ssh_key()


def ssh_trust_gin():
    """SSHホスト（=GIN）を信頼する設定"""
    preparation_completed()
    ssh.trust_gin()


def prepare_sync():
    """同期するコンテンツの制限"""
    preparation_completed()
    sync.prepare_sync()


def setup_sibling():
    """siblingを設定する"""
    preparation_completed()
    sync.setup_sibling()


def add_container():
    """GIN-forkの実行環境一覧へ追加"""
    preparation_completed()
    experiment_title = get_pkg_name()
    ex_pkg_info.set_current_experiment_title(experiment_title)
    container.add_container(experiment_title)


def finished_setup():
    """実験フローの『初期セットアップ』に済を付与する。"""
    preparation_completed()
    flow.put_mark_experiment()


def get_pkg_data():
    preparation_completed()
    experiment_title = ex_pkg_info.exec_get_ex_title()
    sync.datalad_get(p.create_experiments_with_subpath(experiment_title))
    clear_output()
    msg = msg_mod.get('git', 'success_get_data')
    msg_display.display_info(msg)



def syncs_config() -> tuple[list[str], str]:
    """同期のためにファイルとメッセージの設定"""
    preparation_completed()
    # get experiment title
    experiment_title = ex_pkg_info.exec_get_ex_title()
    # set parameter
    nb_path = os.path.join(p.EXP_DIR_PATH, 'required_rebuild_container.ipynb')
    git_path = [nb_path]
    commit_message = msg_mod.get('commit_message', 'required_rebuild_container').format(experiment_title)
    # delete temporarily file
    delete_tmp_file()
    return git_path, commit_message


# ----- utils -----
def submit_init_callback(input_forms, error_message, submit_button):
    """Processing method after click on submit button"""
    def callback(event):
        delete_tmp_file()
        user_name = input_forms[0].value
        password = input_forms[1].value
        experiment_title = input_forms[2].value

        # validate value for forms
        if not pre.validate_user_auth(user_name, password, submit_button):
            return
        if not pre.validate_select_default(experiment_title, msg_mod.get('setup_package','select_default_error'), submit_button):
            return

        try:
            pre.setup_local(user_name, password)
            set_params(experiment_title)

        except Unauthorized:
            submit_button.button_type = 'warning'
            submit_button.name =  msg_mod.get('user_auth','unauthorized')
            return
        except requests.exceptions.RequestException as e:
            submit_button.button_type = 'danger'
            submit_button.name =  msg_mod.get('DEFAULT','connection_error')
            error_message.value = 'ERROR : {}'.format(traceback.format_exception_only(type(e), e)[0].rstrip('\\n'))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        except Exception as e:
            submit_button.button_type = 'danger'
            submit_button.name =  msg_mod.get('DEFAULT','unexpected')
            error_message.value = 'ERROR : {}'.format(traceback.format_exception_only(type(e), e)[0].rstrip('\\n'))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        else:
            submit_button.button_type = 'success'
            submit_button.name =  msg_mod.get('setup_package','success')
            return
    return callback


def initial_forms():
    pn.extension()

    # form of user name and password
    input_forms = pre.create_user_auth_forms()
    # selectbox of experimental packages
    ex_pkg_select = pre.create_select(name=msg_mod.get('setup_package', 'package_name_title'), options=get_experiment_titles())
    input_forms.append(ex_pkg_select)

    # Instance for exception messages
    error_message = pre.layout_error_text()

    button = pre.create_button(name=msg_mod.get('DEFAULT','end_input'))

    # Define processing after clicking the submit button
    button.on_click(submit_init_callback(input_forms, error_message, button))

    clear_output()
    # Columnを利用すると値を取れない場合がある
    for form in input_forms:
        display(form)
    display(button)
    display(error_message)


def get_experiment_titles()->list[str]:
    """リポジトリに存在する全ての実験パッケージ名を取得する

    Raises:
        DGTaskError: リポジトリに実験パッケージが存在しない

    Returns:
        list[str]: 実験パッケージ名
    """
    experiments_path = p.EXPERIMENTS_PATH
    ex_pkg_list = list[str]()
    if os.path.isdir(experiments_path):
        for data_name in os.listdir(experiments_path):
            data_path = os.path.join(experiments_path, data_name)
            if os.path.isdir(data_path):
                ex_pkg_list.append(data_name)
    if len(ex_pkg_list) <= 0:
        msg_display.display_err(msg_mod.get('setup_package', 'not_exist_pkg_error'))
        raise DGTaskError
    return ex_pkg_list
