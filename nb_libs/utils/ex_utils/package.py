import os
import glob

from ..common import common
from ..path import path as p


PACKAGE_PATH = os.path.join(p.DATA_PATH, 'PACKAGE')
SCHEME_PATH = os.path.join(PACKAGE_PATH, 'scheme')
BASE_PATH = os.path.join(PACKAGE_PATH, 'base')


def create_ex_package(dataset_structure:str, experiment_path:str):
    """実験パッケージを作成する

    Args:
        dataset_structure(str): データセット構造種別
        experiment_path(str): ディレクトリのパス
    """
    dst = experiment_path
    srcs = [os.path.join(SCHEME_PATH, dataset_structure), BASE_PATH]
    for src in srcs:
        common.cp_dir(src, dst)


def create_param_folder(param_folder_path:str):
    """パラメータ実験フォルダを作成する

    Args:
        param_folder_path (str): パラメータ実験フォルダまでのパス
    """
    dst = param_folder_path
    src = os.path.join(SCHEME_PATH, 'for_parameters', 'parameter')
    common.cp_dir(src, dst)


def create_syncs_path(experiment_path:str)-> tuple[list[str], list[str], list[str]]:
    """実験パッケージ配下のファイルパスを同期種別毎に返す

    Args:
        experiment_path (str): 実験パッケージまでの絶対パス

    Returns:
        tuple[list[str], list[str], list[str]]: gitとgit-annex管理するファイルのパス
    """

    #**************************************************#
    #* Generate a list of folder paths to be managed by Git-annex. #
    #**************************************************#
    dirlist=[]
    annexed_save_path=[]

    # Recursively search under the experimental package to obtain a list of absolute directory paths.
    for root, dirs, files in os.walk(top=experiment_path):
        for dir in dirs:
            dirPath = os.path.join(root, dir)
            dirlist.append( dirPath )

    # Add directory paths containing the string "output_data" that are not included under input_data to annexed_save_path.
    output_data_path = [ s for s in dirlist if 'output_data' in s ]
    for output_data in output_data_path:
        if  "input_data" not in output_data:
            annexed_save_path.append( output_data )

    # Add the input_data directory to annexed_save_path.
    annexed_save_path.append( experiment_path + '/input_data'  )

    # Generate a list of file paths to which metadata is to be assigned.
    gitannex_files = []
    for path in annexed_save_path:
        gitannex_files += [p for p in glob.glob(path+'/**', recursive=True)
                if os.path.isfile(p)]

    #********************************************************#
    #* Generate a list of directory paths and file paths to be managed by Git. #
    #********************************************************#
    # Obtain a list of directories and files directly under the experimental package.
    files = os.listdir(experiment_path)

    # Delete Git-annex managed directories (input_data and output_data) from the retrieved list.
    dirs = [f for f in files if os.path.isdir(os.path.join(experiment_path, f))]

    if 'input_data' in dirs:
        dirs.remove('input_data')
    if 'output_data' in dirs:
        dirs.remove('output_data')

    for dirname in dirs:
        if dirname != 'ci' and dirname != 'source':
            full_param_dir = '{}/{}/params'.format(experiment_path, dirname)
            if os.path.isdir(full_param_dir):
                dirs.remove(dirname)
                ex_param_path = '{}/{}'.format(experiment_path, dirname)
                ex_param_path_childs = os.listdir(ex_param_path)
                for ex_param_path_child in ex_param_path_childs:
                    if ex_param_path_child != 'output_data':
                        dirs.append('{}/{}'.format(dirname,ex_param_path_child))

    # Obtain files directly under the experimental package.
    files = [f for f in files if os.path.isfile(os.path.join(experiment_path, f))]

    # Generate a list of folder paths and file paths to be managed by Git.
    files.extend(dirs)
    save_path = []
    for file in files:
        save_path.append(experiment_path + '/' + file)

    return save_path, annexed_save_path, gitannex_files
