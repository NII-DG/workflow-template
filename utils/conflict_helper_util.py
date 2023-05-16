import os
from .git import git_module
import shutil
import sys
sys.path.append('../')
from except_class import rename_err, action_err

# annex conflict options
HEAD_REMAIN = 'HEADのファイルを残す'
REMOTE_REMAIN = 'Remoteのファイルを残す'
BOTH_REMAIN = '両方残す'



def get_value_BOTH_REMAIN()->str:
    return BOTH_REMAIN

def get_value_REMOTE_REMAIN()->str:
    return REMOTE_REMAIN

def get_value_HEAD_REMAIN()->str:
    return HEAD_REMAIN

def get_annex_conflict_options()-> list[str]:
    return [HEAD_REMAIN, REMOTE_REMAIN, BOTH_REMAIN]

def is_both_remain(target : dict) -> bool:
    if target['action'] == BOTH_REMAIN:
        return True
    else:
        return False

def is_more_than_both_remain(target : dict) -> bool:
    for k in target:
        if target[k]['action'] == BOTH_REMAIN:
            return True
    return False

# Path
TMP_CONFLICT_DIR = '.tmp/conflict'

def get_TMP_CONFLICT_DIR()->str:
    return TMP_CONFLICT_DIR

# TODO : verify file name
def verify_resolve_file_name(file_name:str)->bool:
    return False

def rename_file(base_filepath, future_name)->str:
    os.chdir(os.environ['HOME'])
    dirname = os.path.dirname(base_filepath)
    future_name_filepath = f'{dirname}/{future_name}'

    # os.rename(base_filepath, future_name_filepath)
    git_module.git_mv(base_filepath, future_name_filepath)
    return future_name_filepath

def delete_file(file_path):
    os.chdir(os.environ['HOME'])
    os.remove(file_path)

def copy_local_content_to_tmp(target_path:str):
    tmp_dir = get_TMP_CONFLICT_DIR()
    hash = git_module.get_local_object_hash_by_path(target_path)
    to_copy_file_path = '{}/{}'.format(tmp_dir, target_path)
    os.chdir(os.environ['HOME'])
    make_dir(os.path.dirname(to_copy_file_path))
    os.system('git cat-file -p {} > {}'.format(hash, to_copy_file_path))

def make_dir(target_dir:str):
    os.chdir(os.environ['HOME'])
    os.makedirs(target_dir, exist_ok=True)

def copy_tmp_to_working(target_path:str):
    os.chdir(os.environ['HOME'])
    tmp_dir = get_TMP_CONFLICT_DIR()
    src_path = '{}/{}'.format(tmp_dir, target_path)
    shutil.copy2(src_path, target_path)

def copy_and_delete_tmpdir(target_paths:list[str]):
    tmp_dir = get_TMP_CONFLICT_DIR()
    for path in target_paths:
        copy_tmp_to_working(path)
    os.chdir(os.environ['HOME'])
    shutil.rmtree(tmp_dir)

def check_annex_resolve_info(info : dict[str, dict]) -> bool:
    """If annex resolve info has action and action is BOTH_REMAIN, check that it has rename data.

    Args:
        info (dict[str, dict]): [description]

    Returns:
        bool: [description]
    """
    both_info = list[dict]()
    for k, v in info.items():
        action = v.get('action')
        if action == None:
            raise action_err.ActionError()
        else:
            if action == BOTH_REMAIN:
                both_info.append(v)

    for v in both_info:
        rename_info = v.get('rename')
        if rename_info == None:
            raise rename_err.RenameError()
    return True
