import os
import shutil
from pathlib import Path
from ..path import path as p


PACKAGE_PATH = os.path.join(p.DATA_PATH, 'PACKAGE')
SCHEME_PATH = os.path.join(PACKAGE_PATH, 'scheme')
BASE_PATH = os.path.join(PACKAGE_PATH, 'base')


def create_ex_package(dataset_structure:str, experiment_path:str):
    """実験パッケージを作成する

    Args:
        dataset_structure(str): データセット構造種別
        experiment_path(str): ディレクトリのパス

    Note:
        指定したディレクトリがなければ作成される。
        ディレクトリに存在しないファイルのみ追加され、同じ名前のファイルが既にある場合、そのファイルは上書きされない
    """

    def f_exists(base, dst):
        base, dst = Path(base), Path(dst)
        def _ignore(path, names):   # サブディレクトリー毎に呼び出される
            names = set(names)
            rel = Path(path).relative_to(base)
            return {f.name for f in (dst/ rel).glob('*') if f.name in names}
        return _ignore

    dst = experiment_path
    srcs = [os.path.join(SCHEME_PATH, dataset_structure), BASE_PATH]
    for src in srcs:
        shutil.copytree(src, dst, ignore=f_exists(src, dst), dirs_exist_ok=True)


def rename_param_folder(experiment_path:str, parama_ex_name:str):
    """パラメータ実験用フォルダの名前をパラメータ実験名に書き変える"""
    if len(parama_ex_name) > 0:
        shutil.move(os.path.join(experiment_path, 'parameter'), os.path.join(experiment_path, parama_ex_name))