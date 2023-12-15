import os
import pytest

from nb_libs.utils.path.path import HOME_PATH, SYS_PATH, EXPERIMENTS_PATH

from .common.utils import DirUtil

TEST_DIR = os.path.join(HOME_PATH, 'unit_test')


@pytest.fixture(scope='session', autouse=True)
def prepare_unit_test():
    # 前処理

    dir_home = DirUtil(HOME_PATH)
    dir_sys = DirUtil(SYS_PATH)
    dir_experiments = DirUtil(EXPERIMENTS_PATH)
    dir_test = DirUtil(TEST_DIR)

    # フォルダ作成
    dir_home.create()
    dir_sys.create()
    dir_experiments.create()
    dir_test.create()

    yield
    # 後処理

    # フォルダ削除
    dir_test.delete()
    dir_experiments.delete()
    dir_sys.delete()
