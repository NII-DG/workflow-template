import os
import pytest
import shutil

from tests.integration_tests.common.exe_env import create_res_env, delete_res_env, create_exp_env, delete_exp_env
from tests.integration_tests.common.path import SCREENSHOT_DIR
from tests.integration_tests.common.setting import init_setting

@pytest.fixture()
def prepare_res_env():
    """研究実行環境の準備"""

    # 研究実行環境作成
    create_res_env()

    yield

    # 研究実行環境削除
    delete_res_env()


@pytest.fixture()
def prepare_exp_env():
    """実験実行環境の準備"""

    # 実験実行環境作成
    create_exp_env()

    yield

    # 実験実行環境削除
    delete_exp_env()


@pytest.fixture(scope='session', autouse=True)
def prepare_integration_test():

    # テスト設定ファイルの初期化
    init_setting()

    # スクリーンショット保存用のフォルダ作成
    create_screenshot_dir()


def create_screenshot_dir():
    """スクリーンショット保存用のフォルダ作成"""
    common_dir = os.path.join(SCREENSHOT_DIR, 'common')
    research_dir = os.path.join(SCREENSHOT_DIR, 'research')
    experiment_dir = os.path.join(SCREENSHOT_DIR, 'experiment')

    # フォルダを削除し、前のデータが残っていない状態にする
    if os.path.exists(SCREENSHOT_DIR):
        shutil.rmtree(SCREENSHOT_DIR)

    # フォルダ作成
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(common_dir, exist_ok=True)
    os.makedirs(research_dir, exist_ok=True)
    os.makedirs(experiment_dir, exist_ok=True)
