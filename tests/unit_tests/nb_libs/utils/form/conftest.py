import os
import pytest
import shutil

from nb_libs.utils.path.path import EXPERIMENTS_PATH


@pytest.fixture()
def create_package_dir():
    package_path = os.path.join(EXPERIMENTS_PATH, 'package_exist')

    # フォルダ作成
    if os.path.isdir(package_path):
        shutil.rmtree(package_path)
    os.makedirs(package_path)

    yield package_path

    # フォルダ削除
    if os.path.isdir(package_path):
        shutil.rmtree(package_path)
