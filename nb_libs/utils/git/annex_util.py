import csv
from datalad import api
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

def annex_to_git(datalad_get_paths:list, experiment_title:str):
    ''' git-annex to git

        Args:
            datalad_get_paths(list): パスのリスト

            experiment_title(str): 実験パッケージ名
    '''
    source_paths = []
    for datalad_get_path in datalad_get_paths:
        if datalad_get_path.startswith(path.create_experiments_sub_path(experiment_title, 'source/')):
            source_paths.append(datalad_get_path)

    if len(source_paths) > 0:
        # Make path str for git or annex command
        src_list = list()
        for src_path in source_paths:
            src_list.append('"{}"'.format(src_path))

        git_arg_path = ' '.join(src_list)

        # Make the data stored in the source folder the target of git management.
        # Temporary lock on annex content
        git_module.git_annex_lock(path.HOME_PATH)
        # Unlock only the paths under the source folder.
        git_module.git_annex_unlock(git_arg_path)
        git_module.git_add(git_arg_path)
        git_module.git_commmit(message.get('from_repo_s3', 'annex_to_git'))
        git_module.git_annex_remove_metadata(git_arg_path)
        git_module.git_annex_unannex(git_arg_path)

    # Attach sdDatePablished metadata to data stored in folders other than the source folder.
    except_source_path = list(set(datalad_get_paths) - set(source_paths))
    for file_path in except_source_path:
        sync.register_metadata_for_downloaded_annexdata(file_path=file_path)

def addurl():
    """datalad addurlsを実行する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合
        AddurlsError: addurlsに失敗した場合

    """
    result = ''
    try:
        result = api.addurls(save=False, fast=True, urlfile= path.ADDURLS_CSV_PATH, urlformat='{link}', filenameformat='{who}')
    except FileNotFoundError as e:
        display.display_err(message.get('from_repo_s3', 'did_not_finish'))
        raise DidNotFinishError() from e

    for line in result:
        if 'addurls(error)' in line or 'addurls(impossible)' in line:
            display.display_err(message.get('from_repo_s3', 'create_link_fail'))
            raise AddurlsError()
    