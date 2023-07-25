import csv
from ..path import path
from ..gin import sync
from ..message import message
import git_module

def create_csv(who_link_dict: dict):
    '''datalad addurlで用いるcsvファイルを作成する

        Arg: {who1: link1, who2: link2}の形式の辞書
    
    '''
    with open(path.ADDURLS_CSV_PATH, mode='w') as f:
        writer = csv.writer(f)
        writer = csv.DictWriter(f, ['who','link'])
        writer.writeheader()
        for who, link in who_link_dict.items():
            writer.writerow({'who': who, 'link':link})

def annex_to_git(datalad_get_paths, experiment_title):
    ''' git-annex to git

        Args:
            datalad_get_paths: 
            
            experiment_title: 実験パッケージ名
    
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

        # Temporary lock on annex content
        git_module.git_annex_lock(path.HOME_PATH)
        # Unlock only the paths under the source folder.
        git_module.git_annex_unlock(git_arg_path)
        git_module.git_add(git_arg_path)
        git_module.git_commmit(message.get('from_s3', 'annex_to_git'))
        git_module.git_annex_remove(git_arg_path)
        git_module.git_annex_unannex(git_arg_path)

    # Attach sdDatePablished metadata to data stored in folders other than the source folder.
    except_source_path = list(set(datalad_get_paths) - set(source_paths))
    for file_path in except_source_path:
        sync.register_metadata_for_downloaded_annexdata(file_path=file_path)