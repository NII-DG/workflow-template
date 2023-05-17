import os
from .git import git_module
import shutil

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

def has_rename_annex_resolve_info_in_both_remain(info : dict[str, dict]) -> bool:
    """If annex resolve info has rename data.

    Args:
        info (dict[str, dict]): [description]

    Returns:
        bool: [description]
    """
    both_info = list[dict]()
    for k, v in info.items():
        action = v.get('action')
        if action == BOTH_REMAIN:
            both_info.append(v)

    for v in both_info:
        rename_info = v.get('rename')
        if rename_info == None:
            return False
    return True

def has_action_annex_resolve_info(info : dict[str, dict]) -> bool:
    """If annex resolve info has action.

    Args:
        info (dict[str, dict]): [description]

    Returns:
        bool: [description]
    """
    for k, v in info.items():
        action = v.get('action')
        if action == None:
            return False
    return True

def is_rf_notebook(filepath : str)->bool:
    return '.ipynb' in filepath and not (filepath.startswith('experiments/'))

def divide_rf_notebook_or_non_file(filepaths : list[str]) -> tuple[list[str], list[str]]:
    rf_notebook_filepaths = list[str]()
    non_rf_notebook_filepaths = list[str]()
    for path in filepaths:
        if is_rf_notebook(path):
            # only auto-resolve content path
            rf_notebook_filepaths.append(path)
        else:
            #  only custom-resolve content path by user
            non_rf_notebook_filepaths.append(path)
    return rf_notebook_filepaths, non_rf_notebook_filepaths

def verify_resolve_file_name(annex_rslv_info:dict[str, dict])->str:

    variant_names = list[str]()
    for v in annex_rslv_info.values():
        variant_names.append(v['HEAD'])
        variant_names.append(v['remote'])

    # excract creating file path list
    create_file_paths = list[str]()
    invalid_names = list[str]()
    has_slash_file_names = list[str]()
    for k, v in annex_rslv_info.items():
        action = v['action']
        if action == BOTH_REMAIN:
            dir = os.path.dirname(k)
            rename_info = v['rename']
            for rename_key, rename_value in rename_info.items():
                if rename_value in variant_names:
                    invalid_names.append(rename_value)
                elif '/' in rename_value:
                    has_slash_file_names.append(rename_value)
                else:
                    remote_path = '{}/{}'.format(dir, rename_value)
                    create_file_paths.append(remote_path)

        elif action == REMOTE_REMAIN or action == HEAD_REMAIN:
            create_file_paths.append(k)

    # Check for duplicate names
    duplicates_paths = list(set([x for x in create_file_paths if create_file_paths.count(x) > 1]))

    # Check for files with the same name already in the working directory.
    unique_file_paths = list(set(create_file_paths))

    existence_file_paths = list[str]()

    for path in unique_file_paths:
        if os.path.isfile(path):
            existence_file_paths.append(path)

    # Create a message
    msg = ''
    if len(duplicates_paths)>0 or len(invalid_names)>0 or len(existence_file_paths)>0 or len(has_slash_file_names):
        msg = msg + '不正な値が入力されました。再度、『3-3. ≪両方を残す≫が選択されたファイルに名前をつける。』を実行し正しいファイル名をしてください。<br>'
    if len(invalid_names)>0:
        msg = msg + 'バリアント名を指定されています。以下のバリアント名は指定しないでください。<br>'
        for invalid_name in invalid_names:
            msg = msg + '・ {}<br>'.format(invalid_name)

    if len(duplicates_paths)>0:
        msg = msg + '重複しているファイル名が指定されています。<br>'
        for duplicates_path in duplicates_paths:
            msg = msg + '・ {}<br>'.format(duplicates_path)

    if len(existence_file_paths)>0:
        msg = msg + '既に存在しているファイル名で指定されています。<br>'
        for existence_file_path in existence_file_paths:
            msg = msg + '・ {}<br>'.format(existence_file_path)

    if len(has_slash_file_names)>0:
        msg = msg + 'ファイル名のみ入力してください。(ディレクトリの変更はできません)<br>'
        for has_slash_file_name in has_slash_file_names:
             msg = msg + '・ {}<br>'.format(has_slash_file_name)

    return msg
