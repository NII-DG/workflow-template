'''prepare_unit_from_s3.ipynbから呼び出されるモジュール'''
import os
import json
import traceback
from urllib  import parse
from json.decoder import JSONDecodeError

from IPython.display import display, clear_output, Javascript
import panel as pn
from datalad import api
from datalad.support.exceptions import IncompleteResultsError

from ..utils.git import annex_util, git_module
from ..utils.path import path, validate
from ..utils.message import message, display as display_util
from ..utils.gin import sync
from ..utils.common import common
from ..utils.aws import s3
from ..utils.except_class import DidNotFinishError, UnexpectedError
from ..utils.params import ex_pkg_info

# 辞書のキー
S3_OBJECT_URL = 's3_object_url'
DEST_FILE_PATH = 'dest_file_path'
EX_PKG_NAME = 'ex_pkg_name'


def input_url_path():
    """S3オブジェクトURLと格納先パスをユーザから取得し、検証を行う

    Exception:
        FileNotFoundError: 実験パッケージ名を記録したjsonファイルが存在しない場合
        KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
    """


    def on_click_callback(event) -> None:


        done_button.name = message.get('from_repo_s3', 'processing')
        done_button.button_type = 'primary'
        common.delete_file(path.UNIT_S3_JSON_PATH)

        input_url = str(columns[0].value_input)
        input_path = str(columns[1].value_input)
        err_msg = ""

        # URLの検証
        if len(input_url)<=0:
            done_button.button_type = 'warning'
            done_button.name = message.get('from_repo_s3', 'empty_url')
            return

        err_msg = s3.access_s3_url(input_url)
        if len(err_msg) > 0:
            done_button.button_type = 'warning'
            done_button.name = err_msg
            return

        experiment_title = ex_pkg_info.exec_get_ex_title()

        # 格納先パスの検証
        err_msg = validate.validate_input_path([(input_path, input_url)], experiment_title)
        if len(err_msg) > 0:
            done_button.button_type = 'warning'
            done_button.name = err_msg
            return

        data = dict()
        data[S3_OBJECT_URL] = parse.unquote(input_url)
        data[DEST_FILE_PATH] = path.create_experiments_with_subpath(experiment_title, input_path)

        os.makedirs(path.RF_FORM_DATA_DIR, exist_ok=True)
        with open(path.UNIT_S3_JSON_PATH, mode='w') as f:
            json.dump(data, f, indent=4)

        done_button.name = message.get('from_repo_s3', 'done_input')
        done_button.button_type = 'success'


    common.delete_file(path.UNIT_S3_JSON_PATH)

    # 入力フォーム表示
    pn.extension()
    columns = pn.Column()
    columns.append(pn.widgets.TextInput(
        name = message.get('from_repo_s3', 'object_url'),
        placeholder = message.get('from_repo_s3', 'enter_object_url'),
        width = 700)
    )
    columns.append(pn.widgets.TextInput(
        name = message.get('from_repo_s3', 'file_path'),
        placeholder = message.get('from_repo_s3', 'enter_a_file_path'),
        width = 700)
    )
    done_button = pn.widgets.Button(
        name= message.get('from_repo_s3', 'end_input'),
        button_type= "default",
        width = 300
    )
    done_button.on_click(on_click_callback)
    columns.append(done_button)

    display(columns)


def prepare_addurls_data():
    """リポジトリへのリンク登録のためのcsvファイルを作成する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
    """
    try:
        with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
            dic = json.load(f)
            input_url = dic[S3_OBJECT_URL]
            dest_file_path = dic[DEST_FILE_PATH]
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except (KeyError, JSONDecodeError):
        display_util.display_err(message.get('from_repo_s3', 'unexpected'))
        display_util.display_log(traceback.format_exc())
        raise
    else:
        annex_util.create_csv({dest_file_path: input_url})


def add_url():
    """リポジトリに取得データのS3オブジェクトURLと格納先パスを登録する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        IncompleteResultsError: addurlsに失敗した場合
    """

    try:
        annex_util.addurl(path.ADDURLS_CSV_PATH)
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except IncompleteResultsError:
        display_util.display_err(message.get('from_repo_s3', 'create_link_fail'))
        raise
    display_util.display_info(message.get('from_repo_s3', 'create_link_success'))


def save_annex():
    """データ取得履歴を記録する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
        UnexpectedError: 想定外のエラーが発生した場合
    """
    try:
        with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
            dest_file_path = json.load(f)[DEST_FILE_PATH]
        # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
        # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
        annex_file_paths = [dest_file_path]
        git_module.git_annex_lock(path.HOME_PATH)
        sync.save_annex_and_register_metadata(gitannex_path=annex_file_paths, gitannex_files=[], message=message.get('commit_message', 'data_from_s3'))
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except (KeyError, JSONDecodeError):
        display_util.display_err(message.get('from_repo_s3', 'unexpected'))
        display_util.display_log(traceback.format_exc())
        raise
    except Exception as e:
        display_util.display_err(message.get('from_repo_s3', 'process_fail'))
        display_util.display_log(traceback.format_exc())
        raise UnexpectedError() from e
    else:
        clear_output()
        display_util.display_info(message.get('from_repo_s3', 'process_success'))


def get_data():
    """取得データの実データをダウンロードする

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
        UnexpectedError: 想定外のエラーが発生した場合
    """
    experiment_title = ex_pkg_info.get_current_experiment_title()
    if experiment_title is None:
        display_util.display_err(message.get('from_repo_s3', 'not_finish_setup'))
        raise DidNotFinishError()

    try:
        # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
        # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
        with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
            dest_file_path = json.load(f)[DEST_FILE_PATH]

        annex_file_paths = [dest_file_path]
        # Obtain the actual data of the created link.
        api.get(path=annex_file_paths)
        annex_util.annex_to_git(annex_file_paths, experiment_title)
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except (KeyError, JSONDecodeError):
        display_util.display_err(message.get('from_repo_s3', 'unexpected'))
        display_util.display_log(traceback.format_exc())
        raise
    except Exception as e:
        display_util.display_err(message.get('from_repo_s3', 'process_fail'))
        display_util.display_log(traceback.format_exc())
        raise UnexpectedError() from e
    else:
        clear_output()
        display_util.display_info(message.get('from_repo_s3', 'download_success'))


def prepare_sync() -> dict:
    """同期の準備を行う

    Returns:
        dict: syncs_with_repoの引数が入った辞書
    Exception:
        DidNotFinishError: jsonファイルの形式が想定通りでない場合
        KeyError, JSONDecodeError: .tmp内のjsonファイルの形式が不正な場合
    """

    display(Javascript('IPython.notebook.save_checkpoint();'))

    git_file_paths = []
    experiment_title = ex_pkg_info.get_current_experiment_title()
    if experiment_title is None:
        display_util.display_err(message.get('from_repo_s3', 'not_finish_setup'))
        raise DidNotFinishError()
    try:
        with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
            dest_file_path = json.load(f)[DEST_FILE_PATH]
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except (KeyError, JSONDecodeError):
        display_util.display_err(message.get('from_repo_s3', 'unexpected'))
        display_util.display_log(traceback.format_exc())
        raise

    annex_file_paths = [dest_file_path]

    if dest_file_path.startswith(path.create_experiments_with_subpath(experiment_title, 'source/')):
        git_file_paths.append(dest_file_path)

    annex_file_paths = list(set(annex_file_paths) - set(git_file_paths))
    git_file_paths.append(os.path.join(path.EXP_DIR_PATH, path.PREPARE_UNIT_FROM_S3))

    sync_repo_args = dict()
    sync_repo_args['git_path'] = git_file_paths
    sync_repo_args['gitannex_path'] = annex_file_paths
    sync_repo_args['gitannex_files'] = annex_file_paths
    sync_repo_args['get_paths'] = [path.create_experiments_with_subpath(experiment_title)]
    sync_repo_args['message'] = message.get('commit_message', 'prepare_data').format(experiment_title)

    common.delete_file(path.UNIT_S3_JSON_PATH)
    common.delete_file(path.ADDURLS_CSV_PATH)

    return sync_repo_args
