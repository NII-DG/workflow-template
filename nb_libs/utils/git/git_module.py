import json
import os
import re
from ..common import common
from ..path import path as p


def exec_git_status():
    """execute 'git status' commands

    RETURN
    ---------------
    Returns output result

    EXCEPTION
    ---------------

    """
    os.chdir(p.HOME_PATH)
    stdout, stderr, rt = common.exec_subprocess('git status')
    result = stdout.decode('utf-8')
    return result

def exec_git_branch():
    """execute 'git status' commands

    RETURN
    ---------------
    Returns output result

    EXCEPTION
    ---------------

    """
    os.chdir(p.HOME_PATH)
    stdout, stderr, rt = common.exec_subprocess('git branch --contains')
    result = stdout.decode('utf-8')
    return result

def exec_git_annex_whereis():
    os.chdir(p.HOME_PATH)
    stdout, stderr, rt = common.exec_subprocess('git annex whereis --json', False)
    result = stdout.decode('utf-8')
    return result

def git_annex_add(path:str):
    os.chdir(p.HOME_PATH)
    stdout, stderr, rt = common.exec_subprocess('git annex add "{}"'.format(path), False)
    result = stdout.decode('utf-8')
    return result

def git_add(path:str):
    os.chdir(p.HOME_PATH)
    stdout, stderr, rt = common.exec_subprocess('git add "{}"'.format(path), False)
    result = stdout.decode('utf-8')
    return result

def git_commmit(msg:str):
    os.chdir(p.HOME_PATH)
    stdout, stderr, rt = common.exec_subprocess('git commit -m "{}"'.format(msg), False)
    result = stdout.decode('utf-8')
    return result

def git_mv(src :str, dest : str):
    os.chdir(p.HOME_PATH)
    stdout, stderr, rt = common.exec_subprocess('git mv "{}" "{}"'.format(src, dest), False)
    result = stdout.decode('utf-8')
    return result

def git_ls_files(path:str):
    os.chdir(p.HOME_PATH)
    stdout, stderr, rt = common.exec_subprocess('git ls-files -s "{}"'.format(path), False)
    result = stdout.decode('utf-8')
    return result

def disable_encoding_git(exec_path=p.HOME_PATH):
    """Disable encoding of git output results

    Args:
        exec_path ([str], optional): [command execution path]. Defaults to p.HOME_PATH.
    """
    os.chdir(exec_path)
    common.exec_subprocess('git config --global core.quotepath false')

def enable_encoding_git(exec_path=p.HOME_PATH):
    """Enable encoding of git output results

    Args:
        exec_path ([str], optional): [command execution path]. Defaults to p.HOME_PATH.
    """
    os.chdir(exec_path)
    common.exec_subprocess('git config --global core.quotepath true')


def git_annex_lock(path:str):
    stdout, stderr, rt = common.exec_subprocess(f'git annex lock {path}')
    result = stdout.decode('utf-8')
    return result

def git_annex_unlock(path:str):
    stdout, stderr, rt = common.exec_subprocess(f'git annex unlock {path}')
    result = stdout.decode('utf-8')
    return result

def git_annex_remove_metadata(path:str):
    stdout, stderr, rt = common.exec_subprocess(f'git annex metadata --remove-all {path}')
    result = stdout.decode('utf-8')
    return result

def git_annex_unannex(path:str):
    stdout, stderr, rt = common.exec_subprocess(f'git annex unannex {path}')
    result = stdout.decode('utf-8')
    return result

def git_annex_resolvemerge(exec_path=p.HOME_PATH):
    os.chdir(exec_path)
    common.exec_subprocess('git annex resolvemerge')

def git_annex_untrust():
    stdout, stderr, rt = common.exec_subprocess(cmd='git annex untrust here')
    result = stdout.decode('utf-8')
    return result

def git_annex_trust():
    stdout, stderr, rt = common.exec_subprocess(cmd='git annex --force trust web')
    result = stdout.decode('utf-8')

def git_annex_whereis(path:str, exec_path:str):
    os.chdir(exec_path)
    stdout, stderr, rt = common.exec_subprocess(f'git annex whereis {path} --json')
    result = stdout.decode('utf-8')
    os.chdir(p.HOME_PATH)
    return result

def get_conflict_filepaths() -> list[str]:
    """Get conflict paths in Unmerged paths for commit from git status

    Returns:
        list: conflict filepaths
    """
    result = exec_git_status()
    lines = result.split('\n')
    conflict_filepaths = list[str]()
    is_not_staged = False
    for l in lines:
        if 'Unmerged paths:' in l:
            is_not_staged = True
            continue
        if is_not_staged and 'both modified:' in l:
            # get conflict filepath
            path_split = l.split(' ')[4:]
            path = ''
            for p in path_split:
                if path ==  '':
                    path = p
                else:
                    path = '{} {}'.format(path, p)
            conflict_filepaths.append(path)
        elif is_not_staged and 'both added:' in l:
            path_split = l.split(' ')[7:]
            path = ''
            for p in path_split:
                if path ==  '':
                    path = p
                else:
                    path = '{} {}'.format(path, p)
            conflict_filepaths.append(path)
    return conflict_filepaths

def get_modified_filepaths() -> list[str]:
    """Get delete file paths in Changes not staged for commit from git status

    Returns:
        list: delete filepaths
    """
    result = exec_git_status()
    lines = result.split('\n')
    delete_filepaths = list[str]()
    is_not_staged = False
    for l in lines:
        if 'Changes not staged for commit:' in l:
            is_not_staged = True
            continue
        if 'modified' in l and is_not_staged:
            # get conflict filepath
            ## ex : ['\tmodified:', '', '', 'WORKFLOWS/untitled.txt']
            path_split = l.split(' ')[3:]
            path = ''
            for p in path_split:
                if path == '':
                    path = p
                else:
                    path = '{} {}'.format(path, p)
            delete_filepaths.append(path)
    return delete_filepaths

def get_delete_filepaths() -> list[str]:
    """Get delete file paths in Changes not staged for commit from git status

    Returns:
        list: delete filepaths
    """
    result = exec_git_status()
    lines = result.split('\n')
    delete_filepaths = list[str]()
    is_not_staged = False
    for l in lines:
        if 'Changes not staged for commit:' in l:
            is_not_staged = True
            continue
        if 'deleted' in l and is_not_staged:
            # get conflict filepath
            path_split = l.split(' ')[4:]
            path = ''
            for p in path_split:
                if path == '':
                    path = p
                else:
                    path = '{} {}'.format(path, p)
            delete_filepaths.append(path)
    return delete_filepaths

def get_annex_content_file_paht_list()->list[str]:
    """Get git-annex content filepaths

    Returns:
        list: git-annex content filepaths
    """
    result = exec_git_annex_whereis()
    data_list = result.split("\n")
    annex_path_list = list[str]()
    data_list = data_list[:-1]
    for data in data_list:
        data_json = json.loads(data)
        annex_path_list.append(data_json['file'])
    return annex_path_list

def get_remote_annex_variant_path(conflict_paths : list[str])-> list[str]:
    """Get git-annex vatiants filepaths

    Returns:
        list: git-annex vatiants filepaths
    """
    result = exec_git_status()
    lines = result.split('\n')
    remote_variant_paths = list[str]()
    for l in lines:
        if 'new file' in l:
            # get conflict filepath
            path_split = l.split(' ')[4:]
            path = ''
            for p in path_split:
                if path == '':
                    path = p
                else:
                    path = '{} {}'.format(path, p)
            for conflict_path in conflict_paths:
                dirpath = os.path.dirname(conflict_path)
                filename_no_extension = os.path.splitext(os.path.basename(conflict_path))[0]
                target_path = '{}/{}.variant-'.format(dirpath, filename_no_extension)
                if path.startswith(target_path):
                    remote_variant_paths.append(path)
    return remote_variant_paths

def get_local_object_hash_by_path(target_path:str) -> str:
    """Obtain the object hash value of a specific file locally in the event of a conflict.

    Args:
        target_path (str): [File Path of Getting object hash]

    Returns:
        str: [object hash]

    Exsample:
        output of git ls-files
        100644 32fe2beffc6c2f6d1b3c92628c3478a538c37f3f 1	WORKFLOWS/EX-WORKFLOWS/save.ipynb
        100644 3e8e574a7145ac462e592d806b26a207d8fe0690 2	WORKFLOWS/EX-WORKFLOWS/save.ipynb
        100644 f3dfa3aae39cd7bdf959fa0b61704825c13dc44c 3	WORKFLOWS/EX-WORKFLOWS/save.ipynb

        result:
            3e8e574a7145ac462e592d806b26a207d8fe0690
    """
    result = git_ls_files(target_path)
    lines = result.split('\n')
    hash = ''
    for l in lines[:-1]:
        s_line = re.split('[ \t]', l)
        if s_line[2] == '2':
            hash = s_line[1]

    return hash


def get_multi_local_object_hash_by_path(target_paths:list[str]) -> list[str]:

    hash_list = list[str]()
    for paht in target_paths:
        hash = get_local_object_hash_by_path(paht)
        hash_list.append(hash)

    return hash_list


def is_conflict() -> bool:
    result = exec_git_status()
    lines = result.split('\n')
    for l in lines:
        if 'both modified:' in l or 'both added:' in l:
            return True
    return False


def get_remote_url():
    stdout, stderr, rt = common.exec_subprocess('git config --get remote.origin.url')
    raw_data = stdout.decode('utf-8')
    return raw_data.replace('\n', '')


def get_current_branch()->str:
    """現在のブランチを取得する。

    Returns:
        str: [ブランチ]
    """
    result = exec_git_branch()
    lines = result.split('\n')
    for l in lines:
        if '*' in l:
            # is current branch
            return l.replace('* ', '')
    return ''
