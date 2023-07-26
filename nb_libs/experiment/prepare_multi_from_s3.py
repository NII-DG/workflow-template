'''prepare_multi_from_s3.ipynbから呼び出されるモジュール'''
import os, json, urllib, traceback
from json.decoder import JSONDecodeError
from ipywidgets import Text, Button, Layout
from IPython.display import display, clear_output, Javascript
from datalad import api
from ..utils.git import annex_util, git_module
from ..utils.path import path
from ..utils.message import message, display as display_util
from ..utils.gin import sync
from ..utils.common import common
from ..utils.aws import s3
from ..utils.except_class import DidNotFinishError, UnexpectedError

PATH_TO_URL = 'path_to_url'
EX_PKG_NAME = 'ex_pkg_name'

def prepare_addurls_data():
    """リポジトリへのリンク登録のためのcsvファイルを作成する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合

        KeyError, JSONDecodeError: jsonファイルの形式が想定通りでない場合

    """
    try:
        with open(path.MULTI_S3_JSON_PATH, mode='r') as f:
            path_to_url_dict = json.load(f)
            
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except (KeyError, JSONDecodeError):
        display_util.display_err(message.get('from_repo_s3', 'unexpected'))
        display_util.display_log(traceback.format_exc())
        raise
    else:
        annex_util.create_csv(path_to_url_dict[PATH_TO_URL])

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
    try:
        with open(path.MULTI_S3_JSON_PATH, mode='r') as f:
            path_to_url_dict:dict = json.load(f)[PATH_TO_URL]
        annex_file_paths = list(path_to_url_dict.keys())
        git_module.git_annex_lock(path.HOME_PATH)
        sync.save_annex_and_register_metadata(gitannex_path=annex_file_paths, gitannex_files=[], message=message.get('from_repo_s3', 'data_from_s3'))
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
    try:
        # The data stored in the source folder is managed by git, but once committed in git annex to preserve the history.
        # *No metadata is assigned to the annexed file because the actual data has not yet been acquired.
        with open(path.PKG_INFO_JSON_PATH, mode='r') as f:
            experiment_title = json.load(f)[EX_PKG_NAME]
        with open(path.UNIT_S3_JSON_PATH, mode='r') as f:
            path_to_url_dict = json.load(f)[PATH_TO_URL]
        annex_file_paths = list(path_to_url_dict.keys())
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
    
    try:
        with open(path.PKG_INFO_JSON_PATH, mode='r') as f:
            experiment_title = json.load(f)[EX_PKG_NAME]
        with open(path.MULTI_S3_JSON_PATH, mode='r') as f:
            path_to_url_dict:dict = json.load(f)[PATH_TO_URL]
        
    except FileNotFoundError as e:
        display_util.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except (KeyError, JSONDecodeError):
        display_util.display_err(message.get('from_repo_s3', 'unexpected'))
        display_util.display_log(traceback.format_exc())
        raise

    annex_file_paths = list(path_to_url_dict.keys())
    git_file_paths = []

    for annex_file_path in annex_file_paths:
        if annex_file_path.startswith(path.create_experiments_with_subpath(experiment_title, 'source/')):
            git_file_paths.append(annex_file_path)

    annex_file_paths = list(set(annex_file_paths) - set(git_file_paths))
    git_file_paths.append(path.EXP_DIR_PATH + path.PREPARE_UNIT_FROM_S3)

    sync_repo_args = dict()
    sync_repo_args['git_path'] = git_file_paths
    sync_repo_args['gitannex_path'] = annex_file_paths
    sync_repo_args['gitannex_files'] = annex_file_paths
    sync_repo_args['get_paths'] = [path.create_experiments_with_subpath(experiment_title)]
    sync_repo_args['message'] = message.get('from_repo_s3', 'prepare_data').format(experiment_title)
    
    common.delete_file(path.MULTI_S3_JSON_PATH)
    common.delete_file(path.ADDURLS_CSV_PATH)
    
    return sync_repo_args