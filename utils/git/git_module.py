import json
import os
from ..common import common

import json
import os
from ..common import common
from datalad import api
import re

def exec_git_status():
    """execute 'git status' commands

    RETURN
    ---------------
    Returns output result

    EXCEPTION
    ---------------

    """
    os.chdir(os.environ['HOME'])
    stdout, stderr, rt = common.exec_subprocess('git status')
    result = stdout.decode('utf-8')
    return result

def exec_git_annex_whereis():
    os.chdir(os.environ['HOME'])
    stdout, stderr, rt = common.exec_subprocess('git annex whereis --json', False)
    result = stdout.decode('utf-8')
    return result

def git_annex_add(path:str):
    os.chdir(os.environ['HOME'])
    stdout, stderr, rt = common.exec_subprocess('git annex add {}'.format(path), False)
    result = stdout.decode('utf-8')
    return result

def git_add(path:str):
    os.chdir(os.environ['HOME'])
    stdout, stderr, rt = common.exec_subprocess('git add {}'.format(path), False)
    result = stdout.decode('utf-8')
    return result

def git_commmit(msg:str):
    os.chdir(os.environ['HOME'])
    stdout, stderr, rt = common.exec_subprocess('git commit -m "{}"'.format(msg), False)
    result = stdout.decode('utf-8')
    return result

def git_mv(src :str, dest : str):
    os.chdir(os.environ['HOME'])
    stdout, stderr, rt = common.exec_subprocess('git mv {} {}'.format(src, dest), False)
    result = stdout.decode('utf-8')
    return result

def git_ls_files(path:str):
    os.chdir(os.environ['HOME'])
    stdout, stderr, rt = common.exec_subprocess('git ls-files -s {}'.format(path), False)
    result = stdout.decode('utf-8')
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
            print(path_split)
            path = ''
            for p in path_split:
                if path ==  '':
                    path = p
                else:
                    path = '{} {}'.format(path, p)
            conflict_filepaths.append(path)
        elif is_not_staged and 'both added:' in l:
            path_split = l.split(' ')[7:]
            print(path_split)
            path = ''
            for p in path_split:
                if path ==  '':
                    path = p
                else:
                    path = '{} {}'.format(path, p)
            conflict_filepaths.append(path)
    return conflict_filepaths

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
            path = l.split(' ')[4]
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
            path = l.split(' ')[4]
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
