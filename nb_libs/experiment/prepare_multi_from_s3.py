'''prepare_multi_from_s3.ipynbから呼び出されるモジュール'''
import os, json, urllib, traceback, boto3
from json.decoder import JSONDecodeError
from ipywidgets import Text, Button, Layout, Password
from IPython.display import display, clear_output, Javascript
import panel as pn
pn.extension()
column = pn.Column()
from datalad import api
from ..utils.git import annex_util, git_module
from ..utils.path import path
from ..utils.message import message, display as display_util
from ..utils.gin import sync
from ..utils.common import common
from ..utils.aws import s3
from ..utils.except_class import DidNotFinishError, UnexpectedError

# 辞書のキー
PATH_TO_URL = 'path_to_url'
EX_PKG_NAME = 'ex_pkg_name'

AWS_S3_INFO = 'aws_s3_info'
AWS_REGION_CODE = 'aws_region_code'
BUCKET = 'bucket'
PREFIX = 'prefix'
PATHS = 'paths'

LOCATION_CONSTRAINT = 'LocationConstraint'
CONTENTS = 'Contents'
KEY = 'Key'

def get_experiment_title() -> str:
    '''ex_pkg_info.jsonを開いて実験パッケージ名を取得する

    Returns:
        str: 実験パッケージ名
    
    Exception:
        DidNotFinishError: ファイルが存在しない場合

        KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
    '''
    try:
        with open(path.PKG_INFO_JSON_PATH, mode='r') as f:
            return json.load(f)[EX_PKG_NAME]
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'not_finish_setup'))
        raise DidNotFinishError() from e
    except (KeyError, JSONDecodeError):
        display_util.display_err(message.get('from_repo_s3', 'unexpected'))
        raise

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

# あとで消す
# ここまで共通関数
#############################################################################################################################

def input_url_path():

    def on_click_callback(clicked_button: Button) -> None:

        common.delete_file(path.MULTI_S3_JSON_PATH)

        bucket_name = input_bucket_name.value
        prefix = input_prefix.value

        s3 = boto3.resource(
            's3',
            aws_access_key_id = input_aws_access_key_id.value,
            aws_secret_access_key = input_aws_secret_access_key.value,
        )
        bucket = s3.Bucket(bucket_name)

        response = bucket.meta.client.get_bucket_location(Bucket=bucket.name)
        aws_region = response[LOCATION_CONSTRAINT]
        
        
        if len(prefix)==0:
            response = bucket.meta.client.list_objects_v2(Bucket=bucket.name)
        else:
            response = bucket.meta.client.list_objects_v2(Bucket=bucket.name, Prefix=prefix)

        s3_contens_key_list = []
        if not CONTENTS in response:
            pass
        else:
            for content in response[CONTENTS]:
                if not content[KEY].endswith('/'):
                    s3_contens_key_list.append(content[KEY])

        aws_s3_info_dict = dict()
        data = dict()
        data[AWS_REGION_CODE] = aws_region
        data[BUCKET] = bucket_name
        data[PREFIX] = prefix
        data[PATHS] = s3_contens_key_list
        aws_s3_info_dict[AWS_S3_INFO] = data

        with open(path.MULTI_S3_JSON_PATH, mode='w') as f:
            json.dump(aws_s3_info_dict, f, indent=4)


        button.description='入力を受け付けました。'
        button.button_style='success'

    # テキストボックス
    style = {'description_width': 'initial'}
    input_aws_access_key_id = Password(
        description='*AWSアクセスキーID：',
        placeholder='Enter your AWS access key ID here...',
        layout=Layout(width='700px'),
        style=style
    )
    input_aws_secret_access_key = Password(
        description='*AWSシークレットアクセスキー：',
        placeholder='Enter your AWS secret key here...',
        layout=Layout(width='700px'),
        style=style
    )

    input_bucket_name = Text(
        description='*バケット名：',
        placeholder='Enter S3 bucket name here...',
        layout=Layout(width='700px'),
        style=style,
        value='test-data-rf'
    )
    input_prefix = Text(
        description='バケットの任意のフォルダパス：',
        placeholder='Enter bucket folder path here...',
        layout=Layout(width='700px'),
        style=style,
        value='pick_folder/'
    )

    common.delete_file(path.MULTI_S3_JSON_PATH)
    button = Button(description='入力を完了する', layout=Layout(width='200px'))
    button.on_click(on_click_callback)
    display(input_aws_access_key_id, input_aws_secret_access_key, input_bucket_name, input_prefix, button)



# def choose_get_data():
#     try:
#         with open(path.MULTI_S3_JSON_PATH, mode='r') as f:
#             multi_s3_dict:dict = json.load(f)
#     except:
#         pass

#     key_list = multi_s3_dict.keys()
#     if len(key_list) != 1 or set(key_list) != {AWS_S3_INFO}:
#         raise
    
#     s3_key_list = multi_s3_dict[AWS_S3_INFO][PATHS]

#     gui_list = []
#     Eliminate folders from the list of folders and files (paths) retrieved from the S3 bucket, display a GUI for file selection as a file list, and accept input.
#     for s3_key in s3_key_list:
#         if s3_key.endswith('/'):
#             pass
#         else:
#             gui_list.append(path)
#     def generate_dest_list(event):
#         done_button.button_type = "success"
#         done_button.name = "選択完了しました。次の処理にお進みください。"
#         global dest_list
#         dest_list = []
#         for i in range(len(column)):
#             if len(column[i].value) > 0:
#                 dest_list.append('### ' + column[i].name)
#             for index in range(len(column[i].value)):
#                 dest_list.append(pn.widgets.TextInput(name=column[i].value[index], placeholder='Enter a file path here...', width=700))
        
#     column.append(pn.widgets.MultiSelect(name = "S3ファイル", options=gui_list, size=len(gui_list), sizing_mode='stretch_width'))
#     done_button = pn.widgets.Button(name= "選択を完了する", button_type= "primary")
#     done_button.on_click(generate_dest_list)
#     column.append(done_button)
#     column


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

        AddurlsError: addurlsに失敗した場合
    """
    annex_util.addurl()
    display_util.display_info(message.get('from_repo_s3', 'create_link_success'))


def save_annex():
    """データ取得履歴を記録する
    
    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合

        KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合

        UnexpectedError: 想定外のエラーが発生した場合
    """

    path_to_url_dict = get_path_to_url_dict()
    annex_file_paths = list(path_to_url_dict.keys())
    try:
        git_module.git_annex_lock(path.HOME_PATH)
        sync.save_annex_and_register_metadata(gitannex_path=annex_file_paths, gitannex_files=[], message=message.get('from_repo_s3', 'data_from_s3'))

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
    try:
        # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
        # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
        experiment_title = get_experiment_title()
        path_to_url_dict = get_path_to_url_dict()
        annex_file_paths = list(path_to_url_dict.keys())
        # Obtain the actual data of the created link.
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
    
    experiment_title = get_experiment_title()
    path_to_url_dict = get_path_to_url_dict()
    annex_file_paths = list(path_to_url_dict.keys())
    git_file_paths = []

    for annex_file_path in annex_file_paths:
        if annex_file_path.startswith(path.create_experiments_with_subpath(experiment_title, 'source/')):
            git_file_paths.append(annex_file_path)

    annex_file_paths = list(set(annex_file_paths) - set(git_file_paths))
    git_file_paths.append(path.EXP_DIR_PATH + path.PREPARE_MULTI_FROM_S3)

    sync_repo_args = dict()
    sync_repo_args['git_path'] = git_file_paths
    sync_repo_args['gitannex_path'] = annex_file_paths
    sync_repo_args['gitannex_files'] = annex_file_paths
    sync_repo_args['get_paths'] = [path.create_experiments_with_subpath(experiment_title)]
    sync_repo_args['message'] = message.get('from_repo_s3', 'prepare_data').format(experiment_title)
    
    common.delete_file(path.MULTI_S3_JSON_PATH)
    common.delete_file(path.ADDURLS_CSV_PATH)
    
    return sync_repo_args