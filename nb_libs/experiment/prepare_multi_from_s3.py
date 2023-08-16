'''prepare_multi_from_s3.ipynbから呼び出されるモジュール'''
import os
import json
from json.decoder import JSONDecodeError

import boto3
from IPython.display import display, clear_output, Javascript
import panel as pn
from datalad import api
from botocore.exceptions import ClientError
from datalad.support.exceptions import IncompleteResultsError

from ..utils.git import annex_util, git_module
from ..utils.path import path, validate
from ..utils.message import message, display as display_util
from ..utils.gin import sync
from ..utils.common import common
from ..utils.except_class import DidNotFinishError, UnexpectedError
from ..utils.params import ex_pkg_info

# 辞書のキー
PATH_TO_URL = 'path_to_url'
EX_PKG_NAME = 'ex_pkg_name'
AWS_S3_INFO = 'aws_s3_info'
AWS_REGION_CODE = 'aws_region_code'
BUCKET = 'bucket'
PREFIX = 'prefix'
PATHS = 'paths'
SELECTED_PATHS = 'selected_paths'
LOCATION_CONSTRAINT = 'LocationConstraint'
CONTENTS = 'Contents'
KEY = 'Key'


def get_path_to_url_dict() -> dict:
    '''prepare_multi_from_s3.jsonを開いてデータを取得する

    Returns:
        jsonファイルの'path_to_url'の項目
    Exception:
        DidNotFinishError: ファイルが存在しない場合
        KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
    '''
    try:
        with open(path.MULTI_S3_JSON_PATH, mode='r') as f:
            return json.load(f)[PATH_TO_URL]
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except (KeyError, JSONDecodeError):
        display_util.display_err(message.get('from_repo_s3', 'unexpected'))
        raise


def get_multi_s3_dict() -> dict:
    '''prepare_multi_from_s3.jsonを開いてデータを取得する

    Returns:
        jsonファイル
    Exception:
        DidNotFinishError: ファイルが存在しない場合
        JSONDecodeError: jsonファイルの形式が想定通りでない場合
    '''
    try:
        with open(path.MULTI_S3_JSON_PATH, mode='r') as f:
            return json.load(f)
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError(message.get('from_repo_s3', 'did_not_finish')) from e


def input_aws_info():
    '''AWS接続情報を入力するフォームを表示する
    '''


    def on_click_callback(event) -> None:
        '''入力されたAWS接続情報の検証を行いファイルに記録する
        '''

        done_button.name = message.get('from_repo_s3', 'processing')
        done_button.button_type = 'primary'
        common.delete_file(path.MULTI_S3_JSON_PATH)

        access_key_id = columns[0].value_input
        secret_access_key = columns[1].value_input
        bucket_name = columns[2].value_input
        prefix = columns[3].value_input

        # 入力値検証
        err_msg = ""
        if len(access_key_id) == 0:
            err_msg = message.get('from_repo_s3', 'empty_access_key_id')
        elif len(secret_access_key) == 0:
            err_msg = message.get('from_repo_s3', 'empty_secret_access_key')
        elif len(bucket_name) == 0:
            err_msg = message.get('from_repo_s3', 'empty_bucket_name')

        if len(err_msg) > 0:
            done_button.name = err_msg
            done_button.button_type = 'warning'
            return

        # s3接続確認
        s3 = boto3.resource(
            's3',
            aws_access_key_id = access_key_id,
            aws_secret_access_key = secret_access_key
        )
        bucket = s3.Bucket(bucket_name)

        try:
            response = bucket.meta.client.get_bucket_location(Bucket=bucket_name)
        except ClientError as e:
            done_button.button_type = 'warning'
            if e.response['Error']['Code'] == 'NoSuchBucket':
                done_button.name = message.get('from_repo_s3', 'no_such_bucket')
            else:
                done_button.name = message.get('from_repo_s3', 'client_error')
            return

        aws_region = response[LOCATION_CONSTRAINT]

        if len(prefix)==0:
            response = bucket.meta.client.list_objects_v2(Bucket=bucket_name)
        else:
            response = bucket.meta.client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        if not CONTENTS in response:
            done_button.button_type ='warning'
            done_button.name = message.get('from_repo_s3', 'no_contents')
            return

        s3_contens_key_list = []
        for content in response[CONTENTS]:
            if not content[KEY].endswith('/'):
                s3_contens_key_list.append(content[KEY])

        aws_s3_info_dict = dict()
        aws_s3_info_dict[AWS_S3_INFO] = {
            AWS_REGION_CODE: aws_region,
            BUCKET: bucket_name,
            PREFIX: prefix,
            PATHS: s3_contens_key_list
        }

        os.makedirs(path.RF_FORM_DATA_DIR, exist_ok=True)
        with open(path.MULTI_S3_JSON_PATH, mode='w') as f:
            json.dump(aws_s3_info_dict, f, indent=4)

        done_button.name = message.get('from_repo_s3', 'done_input')
        done_button.button_type = 'success'

    common.delete_file(path.MULTI_S3_JSON_PATH)

    # 入力フォーム表示
    pn.extension()
    columns = pn.Column()
    columns.append(pn.widgets.PasswordInput(
        name = message.get('from_repo_s3', 'access_key_id'),
        placeholder = message.get('from_repo_s3', 'enter_access_key_id'),
        width = 700)
    )
    columns.append(pn.widgets.PasswordInput(
        name = message.get('from_repo_s3', 'secret_access_key'),
        placeholder = message.get('from_repo_s3', 'enter_secret_access_key'),
        width = 700)
    )
    columns.append(pn.widgets.TextInput(
        name = message.get('from_repo_s3', 'bucket_name'),
        placeholder = message.get('from_repo_s3', 'enter_bucket_name'),
        width = 700)
    )
    columns.append(pn.widgets.TextInput(
        name = message.get('from_repo_s3', 'folder_path'),
        placeholder = message.get('from_repo_s3', 'enter_folder_path'),
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


def choose_get_data():
    '''取得データを選択するフォームを表示する

    Exception:
        JSONDecodeError: jsonファイルの形式が想定通りでない場合
    '''


    def generate_dest_list(event):
        '''選択したデータをファイルに記録する
        '''

        try:
            s3_key_list = column[0].value
            if len(s3_key_list) == 0:
                done_button.button_type = "warning"
                done_button.name = message.get('from_repo_s3', 'data_not_selected')
                return
            multi_s3_dict = get_multi_s3_dict()
            multi_s3_dict[SELECTED_PATHS] = s3_key_list
            with open(path.MULTI_S3_JSON_PATH, mode='w') as f:
                json.dump(multi_s3_dict, f, indent=4)
        except Exception as e:
            done_button.button_type = "danger"
            done_button.name = str(e)
            return

        done_button.button_type = "success"
        done_button.name = message.get('from_repo_s3', 'done_choose')

    try:
        multi_s3_dict = get_multi_s3_dict()
    except DidNotFinishError:
        return

    keys = multi_s3_dict.keys()
    if len(keys) != 1 or set(keys) != {AWS_S3_INFO}:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        return
    content_key_list = multi_s3_dict[AWS_S3_INFO][PATHS]

    # 入力フォーム表示
    pn.extension()
    column = pn.Column()
    column.append(pn.widgets.MultiSelect(name = message.get('from_repo_s3', 's3_file'), options=content_key_list, size=len(content_key_list), sizing_mode='stretch_width'))
    done_button = pn.widgets.Button(name= message.get('from_repo_s3', 'end_choose'), button_type= "default")
    column.append(done_button)
    done_button.on_click(generate_dest_list)
    display(column)


def input_path():
    '''データの格納先を入力するフォームを出力する

    Exception:
        JSONDecodeError: jsonファイルの形式が想定通りでない場合
    '''
    def verify_input_text(event):
        '''入力された格納先を検証しファイルに記録する
        '''

        experiment_title = ex_pkg_info.get_current_experiment_title()
        if experiment_title is None:
            display_util.display_err(message.get('from_repo_s3', 'not_finish_setup'))
            return

        input_path_url_list = [(line.value_input, line.name) for line in column if 'TextInput' in str(type(line))]

        # 格納先パスの検証
        err_msg = validate.validate_input_path(input_path_url_list, experiment_title)
        if len(err_msg) > 0:
            done_button.button_type = "warning"
            done_button.name = err_msg
            return

        multi_s3_dict = get_multi_s3_dict()
        bucket_name = multi_s3_dict[AWS_S3_INFO][BUCKET]
        aws_region = multi_s3_dict[AWS_S3_INFO][AWS_REGION_CODE]

        path_to_url_dict = dict()
        for input_path, input_url in input_path_url_list:
            input_path = path.create_experiments_with_subpath(experiment_title, input_path)
            input_url = input_url.replace(" ", "+")
            input_url = 'https://{}.s3.{}.amazonaws.com/{}'.format(bucket_name, aws_region, input_url)
            path_to_url_dict[input_path] = input_url

        multi_s3_dict[PATH_TO_URL] = path_to_url_dict
        with open(path.MULTI_S3_JSON_PATH, mode='w') as f:
            json.dump(multi_s3_dict, f, indent=4)

        done_button.button_type = "success"
        done_button.name = message.get('from_repo_s3', 'done_input')


    try:
        multi_s3_dict = get_multi_s3_dict()
    except DidNotFinishError:
        return
    keys = multi_s3_dict.keys()
    if len(keys) != 2 or set(keys) != {AWS_S3_INFO, SELECTED_PATHS}:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        return

    selected_paths = multi_s3_dict[SELECTED_PATHS]

    # 入力フォーム表示
    column = pn.Column()
    column.append(message.get('from_repo_s3', 'h3_s3_file'))
    for selected_path in selected_paths:
        column.append(pn.widgets.TextInput(name=selected_path, placeholder=message.get('from_repo_s3', 'enter_a_file_path'), width=700))
    done_button = pn.widgets.Button(name= message.get('from_repo_s3', 'end_input'), button_type= "default")
    column.append(done_button)
    done_button.on_click(verify_input_text)
    display(column)


def prepare_addurls_data():
    """リポジトリへのリンク登録のためのcsvファイルを作成する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
    """
    annex_util.create_csv(get_path_to_url_dict())


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
    multi_s3_dict = get_multi_s3_dict()
    bucket_name = multi_s3_dict[AWS_S3_INFO][BUCKET]
    path_to_url_dict = multi_s3_dict[PATH_TO_URL]
    annex_file_paths = list(path_to_url_dict.keys())

    try:
        git_module.git_annex_lock(path.HOME_PATH)
        sync.save_annex_and_register_metadata(
            gitannex_path=annex_file_paths, gitannex_files=[], message=message.get('commit_message', 'data_from_s3_bucket').format(bucket_name))
    except Exception as e:
        display_util.display_err(message.get('from_repo_s3', 'process_fail'))
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

    path_to_url_dict = get_path_to_url_dict()
    annex_file_paths = list(path_to_url_dict.keys())
    try:
        api.get(path=annex_file_paths)
        annex_util.annex_to_git(annex_file_paths, experiment_title)
    except Exception as e:
        display_util.display_err(message.get('from_repo_s3', 'process_fail'))
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

    experiment_title = ex_pkg_info.get_current_experiment_title()
    if experiment_title is None:
        display_util.display_err(message.get('from_repo_s3', 'not_finish_setup'))
        raise DidNotFinishError()

    path_to_url_dict = get_path_to_url_dict()
    annex_file_paths = list(path_to_url_dict.keys())
    git_file_paths = []

    for annex_file_path in annex_file_paths:
        if annex_file_path.startswith(path.create_experiments_with_subpath(experiment_title, 'source/')):
            git_file_paths.append(annex_file_path)

    annex_file_paths = list(set(annex_file_paths) - set(git_file_paths))
    git_file_paths.append(os.path.join(path.EXP_DIR_PATH, path.PREPARE_MULTI_FROM_S3))

    sync_repo_args = dict()
    sync_repo_args['git_path'] = git_file_paths
    sync_repo_args['gitannex_path'] = annex_file_paths
    sync_repo_args['gitannex_files'] = annex_file_paths
    sync_repo_args['get_paths'] = [path.create_experiments_with_subpath(experiment_title)]
    sync_repo_args['message'] = message.get('commit_message', 'prepare_data').format(experiment_title)

    common.delete_file(path.MULTI_S3_JSON_PATH)
    common.delete_file(path.ADDURLS_CSV_PATH)

    return sync_repo_args
