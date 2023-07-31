'''prepare_from_repository.ipynbから呼び出されるモジュール'''
import os, json, shutil, git
from json.decoder import JSONDecodeError
from ipywidgets import Text, Button, Layout
from IPython.display import display, clear_output, Javascript
import panel as pn
from datalad import datalad_api
from urllib import parse
from http import HTTPStatus
from ..utils.git import annex_util, git_module
from ..utils.path import path, validate
from ..utils.message import message, display as display_util
from ..utils.gin import sync
from ..utils.gin import api as gin_api
from ..utils.common import common
from ..utils.except_class import DidNotFinishError, UnexpectedError
from ..utils.params import param_json

# 辞書のキー
# PATH_TO_URL = 'path_to_url'
# EX_PKG_NAME = 'ex_pkg_name'
# AWS_S3_INFO = 'aws_s3_info'
# AWS_REGION_CODE = 'aws_region_code'
# BUCKET = 'bucket'
# PREFIX = 'prefix'
# PATHS = 'paths'
# SELECTED_PATHS = 'selected_paths'
# LOCATION_CONSTRAINT = 'LocationConstraint'
# CONTENTS = 'Contents'
# KEY = 'Key'
GINFORK_TOKEN = 'ginfork_token'
PRIVATE = 'private'
DATASET_STRUCTURE = "datasetStructure"

def input_repository():


    def on_click_callback(clicked_button: Button) -> None:
        common.delete_file(path.FROM_REPO_JSON_PATH)

        clone_url = text.value
        repo_name = clone_url.split('/')[-1].replace('.git', '')
        repo_owner = clone_url.split('/')[-2]
        with open (path.TOKEN_JSON_PATH, 'r') as f:
            token = json.load(f)[GINFORK_TOKEN]

        pr = parse.urlparse(param_json.get_gin_http())
        response = gin_api.get_repo_info(pr.scheme, pr.netloc, repo_owner, repo_name, token)

        if response.status_code == HTTPStatus.OK:
            pass

        elif response.status_code == HTTPStatus.NOT_FOUND:
            pass

        else:
            pass

        if response[PRIVATE] == True:
            return

        os.makedirs(path.TMP_DIR, exist_ok=True)

        if os.path.exists(path.GET_REPO_PATH):
            shutil.rmtree(path.GET_REPO_PATH)
        os.mkdir(path.GET_REPO_PATH)

        options = ['-b master', '--depth 1', '--filter=blob:none']
        git.Repo.clone_from(
            url=clone_url,
            to_path=os.path.join(path.GET_REPO_PATH, repo_name),
            multi_options=options
        )


        with open (os.path.join(path.GET_REPO_PATH, repo_name), 'r') as f:
            dataset_structure = json.load()[DATASET_STRUCTURE]


        clear_output()
        display_util.display_info("入力完了しました")
        display_util.display_msg('URL: '+ clone_url)


    common.delete_file(path.FROM_REPO_JSON_PATH)

    # リポジトリ名入力フォーム
    text = Text(
        description='URL：',
        placeholder='https://dg.nii.ac.jp/user/repository_title.git',
        layout=Layout(width='500px')
    )
    button = Button(description='入力完了')
    button.on_click(on_click_callback)
    text.on_submit(on_click_callback)
    display_util.display_info("URLを入力してください。<br>入力完了後、「入力完了ボタン」または「Enterキー」を押下してください。")
    display(text, button)







# def prepare_addurls_data():
#     """リポジトリへのリンク登録のためのcsvファイルを作成する

#     Exception:
#         DidNotFinishError: .tmp内のファイルが存在しない場合
#         KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
#     """
#     try:
#         with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
#             dic = json.load(f)
#             input_url = dic[S3_OBJECT_URL]
#             dest_file_path = dic[DEST_FILE_PATH]
#     except FileNotFoundError as e:
#         display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
#         raise DidNotFinishError() from e
#     except (KeyError, JSONDecodeError):
#         display_util.display_err(message.get('from_repo_s3', 'unexpected'))
#         raise
#     else:
#         annex_util.create_csv({dest_file_path: input_url})


# def add_url():
#     """リポジトリに取得データのS3オブジェクトURLと格納先パスを登録する

#     Exception:
#         DidNotFinishError: .tmp内のファイルが存在しない場合
#         AddurlsError: addurlsに失敗した場合
#     """
#     annex_util.addurl()
#     display_util.display_info(message.get('from_repo_s3', 'create_link_success'))


# def save_annex():
#     """データ取得履歴を記録する

#     Exception:
#         DidNotFinishError: .tmp内のファイルが存在しない場合
#         KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
#         UnexpectedError: 想定外のエラーが発生した場合
#     """
#     try:
#         with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
#             dest_file_path = json.load(f)[DEST_FILE_PATH]
#         # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
#         # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
#         annex_file_paths = [dest_file_path]
#         git_module.git_annex_lock(path.HOME_PATH)
#         sync.save_annex_and_register_metadata(gitannex_path=annex_file_paths, gitannex_files=[], message=message.get('from_repo_s3', 'data_from_s3'))
#     except FileNotFoundError as e:
#         display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
#         raise DidNotFinishError() from e
#     except (KeyError, JSONDecodeError):
#         display_util.display_err(message.get('from_repo_s3', 'unexpected'))
#         raise
#     except Exception as e:
#         display_util.display_err(message.get('from_repo_s3', 'process_fail'))
#         raise UnexpectedError() from e
#     else:
#         clear_output()
#         display_util.display_info(message.get('from_repo_s3', 'process_success'))


# def get_data():
#     """取得データの実データをダウンロードする

#     Exception:
#         DidNotFinishError: .tmp内のファイルが存在しない場合
#         KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合
#         UnexpectedError: 想定外のエラーが発生した場合
#     """
#     try:
#         # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
#         # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
#         with open(path.PKG_INFO_JSON_PATH, mode='r') as f:
#             experiment_title = json.load(f)[EX_PKG_NAME]
#         with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
#             dest_file_path = json.load(f)[DEST_FILE_PATH]

#         annex_file_paths = [dest_file_path]
#         # Obtain the actual data of the created link.
#         api.get(path=annex_file_paths)
#         annex_util.annex_to_git(annex_file_paths, experiment_title)
#     except FileNotFoundError as e:
#         display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
#         raise DidNotFinishError() from e
#     except (KeyError, JSONDecodeError):
#         display_util.display_err(message.get('from_repo_s3', 'unexpected'))
#         raise
#     except Exception as e:
#         display_util.display_err(message.get('from_repo_s3', 'process_fail'))
#         raise UnexpectedError() from e
#     else:
#         clear_output()
#         display_util.display_info(message.get('from_repo_s3', 'download_success'))


# def prepare_sync() -> dict:
#     """同期の準備を行う

#     Returns:
#         dict: syncs_with_repoの引数が入った辞書
#     Exception:
#         DidNotFinishError: jsonファイルの形式が想定通りでない場合
#         KeyError, JSONDecodeError: .tmp内のjsonファイルの形式が不正な場合
#     """

#     display(Javascript('IPython.notebook.save_checkpoint();'))

#     git_file_paths = []
#     try:
#         with open(path.PKG_INFO_JSON_PATH, mode='r') as f:
#             experiment_title = json.load(f)[EX_PKG_NAME]
#         with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
#             dest_file_path = json.load(f)[DEST_FILE_PATH]
#     except FileNotFoundError as e:
#         display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
#         raise DidNotFinishError() from e
#     except (KeyError, JSONDecodeError):
#         display_util.display_err(message.get('from_repo_s3', 'unexpected'))
#         raise

#     annex_file_paths = [dest_file_path]

#     if dest_file_path.startswith(path.create_experiments_with_subpath(experiment_title, 'source/')):
#         git_file_paths.append(dest_file_path)

#     annex_file_paths = list(set(annex_file_paths) - set(git_file_paths))
#     git_file_paths.append(path.EXP_DIR_PATH + path.PREPARE_UNIT_FROM_S3)

#     sync_repo_args = dict()
#     sync_repo_args['git_path'] = git_file_paths
#     sync_repo_args['gitannex_path'] = annex_file_paths
#     sync_repo_args['gitannex_files'] = annex_file_paths
#     sync_repo_args['get_paths'] = [path.create_experiments_with_subpath(experiment_title)]
#     sync_repo_args['message'] = message.get('from_repo_s3', 'prepare_data').format(experiment_title)

#     common.delete_file(path.UNIT_S3_JSON_PATH)
#     common.delete_file(path.ADDURLS_CSV_PATH)

#     return sync_repo_args