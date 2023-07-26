import csv
from datalad import api
from datalad.support.exceptions import IncompleteResultsError
from ..path import path
from ..gin import sync
from ..git import git_module
from ..message import message, display
from ..except_class import DidNotFinishError, AddurlsError

def create_csv(who_link_dict: dict):
    '''datalad addurlで用いるcsvファイルを作成する

        Args: 
            who_link_dict(dict): {who1: link1, who2: link2, ...}の形式の辞書
    '''
    with open(path.ADDURLS_CSV_PATH, mode='w') as f:
        writer = csv.writer(f)
        writer = csv.DictWriter(f, ['who','link'])
        writer.writeheader()
        for who, link in who_link_dict.items():
            writer.writerow({'who': who, 'link':link})

def annex_to_git(annex_file_paths:list, experiment_title:str):
    ''' sourceフォルダ配下のファイルをannex管理からgit管理に変更する

        Args:
            annex_file_paths(list): パスのリスト

            experiment_title(str): 実験パッケージ名
    '''
    source_file_paths = []
    for annex_file_path in annex_file_paths:
        if annex_file_path.startswith(path.create_experiments_with_subpath(experiment_title, 'source/')):
            source_file_paths.append(annex_file_path)

    if len(source_file_paths) > 0:
        # Make path str for git or annex command
        source_file_path_list = list()
        for source_file_path in source_file_paths:
            source_file_path_list.append('"{}"'.format(source_file_path))

        git_file_paths = ' '.join(source_file_path_list)

        # Make the data stored in the source folder the target of git management.
        # Temporary lock on annex content
        git_module.git_annex_lock(path.HOME_PATH)
        # Unlock only the paths under the source folder.
        git_module.git_annex_unlock(git_file_paths)
        git_module.git_add(git_file_paths)
        git_module.git_commmit(message.get('from_repo_s3', 'annex_to_git'))
        git_module.git_annex_remove_metadata(git_file_paths)
        git_module.git_annex_unannex(git_file_paths)

    # Attach sdDatePablished metadata to data stored in folders other than the source folder.
    annex_file_paths = list(set(annex_file_paths) - set(source_file_paths))
    for annex_file_path in annex_file_paths:
        sync.register_metadata_for_downloaded_annexdata(file_path=annex_file_path)

def addurl():
    """datalad addurlsを実行する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合

        AddurlsError: addurlsに失敗した場合

    """
    result = ''
    try:
        api.addurls(save=False, fast=True, urlfile= path.ADDURLS_CSV_PATH, urlformat='{link}', filenameformat='{who}')
    except FileNotFoundError as e:
        display.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e
    except IncompleteResultsError as e:
        display.display_err(message.get('from_repo_s3', 'create_link_fail'))
        raise AddurlsError() from e
    