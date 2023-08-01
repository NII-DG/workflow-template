import subprocess
import re
import os
import shutil
from ..except_class import ExecCmdError
from natsort import natsorted


def get_AND_elements(list_a, list_b :list)->list:

    and_elements = set(list_a) & set(list_b)
    return list(and_elements)


def decode_exec_subprocess(cmd: str, raise_error=True):
    stdout, stderr, rt = exec_subprocess(cmd, raise_error)
    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')
    return stdout, stderr, rt


def exec_subprocess(cmd: str, raise_error=True):
    child = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()
    rt = child.returncode
    if rt != 0 and raise_error:
        raise ExecCmdError(f"command return code is not 0. got {rt}. stderr = {stderr}")

    return stdout, stderr, rt

def is_should_annex_content_path(file_path : str)->bool:
    path_factor = file_path.split('/')
    if path_factor[0] == 'experiments':
        if len(path_factor) >= 3 and (path_factor[2]=='input_data' or path_factor[2]=='output_data'):
            if len(path_factor) >= 4 and path_factor[3] == '.gitkeep':
                return False
            else:
                return True
        elif len(path_factor) >= 3 and (path_factor[2]=='source' or path_factor[2]=='ci'):
            return False
        elif len(path_factor) >= 3:
            if len(path_factor) >= 4 and path_factor[3] == 'output_data':
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def has_unicode_escape(text:str)->bool:
    pattern = r"\\u[0-9a-fA-F]{4}"
    match = re.search(pattern, text)
    if match:
        return True
    else:
        return False

def get_filepaths_from_dalalad_error(err_info: str):
    pattern = r"'\\t(.+?)\\n'"
    return re.findall(pattern, err_info)

def get_AND_dirpaths(paths:list[str])->list[str]:
    dirpaths = []
    for path in paths:
        dir = os.path.dirname(path)
        if dir in dirpaths:
            continue
        else:
            dirpaths.append(dir)
    return dirpaths

def sortFilePath(filepaths : list[str])->list[str]:
    # create file base info for sort
    file_path_root_ext = dict[str, dict[str, str]]()
    root_list = list[str]()
    ext_list = list[str]()
    for filepath in filepaths:
        root, ext = os.path.splitext(filepath)
        root_ext = {root : ext}
        file_path_root_ext[filepath] = root_ext
        if root not in root_list:
            root_list.append(root)
        if ext not in ext_list:
            ext_list.append(ext)
    root_list = natsorted(root_list)
    ext_list = natsorted(ext_list)

    # create
    file_paths_desc = list[str]()
    for root in reversed(root_list):
        group_file_path = list[str]()
        for filepath, root_ext in file_path_root_ext.items():
            for root_info in root_ext.keys():
                if root == root_info:
                    group_file_path.append(filepath)
        file_paths_desc.extend(natsorted(group_file_path,reverse=True))

    return list(reversed(file_paths_desc))


def convert_url_remove_user_token(url):
    pattern = r"(http[s]?://)([^:]+):([^@]+)@(.+)"
    match = re.search(pattern, url)
    if match:
        protocol = match.group(1)
        username = match.group(2)
        password = match.group(3)
        domain = match.group(4)

        # Generate URL without username and password
        # domain includes paths
        new_url = f"{protocol}{domain}"
        return new_url, password

    return url, ""  # Returns the original URL if it cannot be converted


def delete_file(file_path:str):
    '''ファイルが存在するか確認してから削除する
    '''
    if os.path.isfile(file_path):
        os.remove(file_path)


def cp_file(old_file_path, new_file_path):
    """新しいファイルの親フォルダが存在していない場合は作成してからコピーする"""
    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
    shutil.copy(old_file_path, new_file_path)