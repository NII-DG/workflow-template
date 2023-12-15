import os
import pytest

from nb_libs.utils.path.path import EXPERIMENTS_PATH

from tests.unit_tests.common.utils import DirUtil


@pytest.fixture()
def create_package_dir():
    dir_package = DirUtil(os.path.join(EXPERIMENTS_PATH, 'package_exist'))

    # フォルダ作成
    dir_package.delete()
    dir_package.create()

    yield dir_package.path

    # フォルダ削除
    dir_package.delete()
