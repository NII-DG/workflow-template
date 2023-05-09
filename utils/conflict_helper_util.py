import os

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

# TODO : verify file name
def verify_resolve_file_name(file_name:str)->bool:
    return False

def rename_file(base_filepath, future_name)->str:
    os.chdir(os.environ['HOME'])
    print(f'base_filepath : {base_filepath}')
    print(f'future_name : {future_name}')
    dirname = os.path.dirname(base_filepath)
    print(f'dirname : {dirname}')
    future_name_filepath = f'{dirname}/{future_name}'
    print(f'future_name_filepath : {future_name_filepath}')
    os.rename(base_filepath, future_name_filepath)
    return future_name_filepath

def delete_file(file_path):
    print(f'delete file_path : {file_path}')
    os.chdir(os.environ['HOME'])
    os.remove(file_path)
