import json
import os
from ..common import common
from datalad import api

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

def get_conflict_filepaths() -> list[str]:
    """Get conflict paths in repo

    Returns:
        list: conflict filepaths
    """
    result = exec_git_status()
    lines = result.split('\n')
    conflict_filepaths = list[str]()
    for l in lines:
        if 'both modified' in l:
            # get conflict filepath
            path = l.split(' ')[4]
            conflict_filepaths.append(path)
    return conflict_filepaths

def get_annex_content_file_paht_list():
    result = exec_git_annex_whereis()
    data_list = result.split("\n")
    print(data_list)
    annex_path_list = list[str]()
    data_list = data_list[:-1]
    for data in data_list:
        data_json = json.loads(data)
        annex_path_list.append(data_json['file'])
    return annex_path_list

def get_variant_info():
    api.
