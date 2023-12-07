import os
import pytest
import shutil

from nb_libs.utils.path.path import HOME_PATH, SYS_PATH, EXPERIMENTS_PATH

TEST_DIR = os.path.join(HOME_PATH, 'unit_test')


@pytest.fixture(scope='session', autouse=True)
def prepare_unit_test():
    # 前処理

    # フォルダ作成
    os.makedirs(HOME_PATH, exist_ok=True)
    os.makedirs(SYS_PATH, exist_ok=True)
    os.makedirs(EXPERIMENTS_PATH, exist_ok=True)
    os.makedirs(TEST_DIR, exist_ok=True)

    yield
    # 後処理

    # フォルダ削除
    shutil.rmtree(SYS_PATH)
    shutil.rmtree(EXPERIMENTS_PATH)
    shutil.rmtree(TEST_DIR)
