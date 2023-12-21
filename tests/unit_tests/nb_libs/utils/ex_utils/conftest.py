import os
import pytest

from nb_libs.utils.path.path import HOME_PATH

from tests.unit_tests.conftest import TEST_DIR
from tests.unit_tests.common.utils import FileUtil, DirUtil


@pytest.fixture()
def prepare_dmp_json():
    dmp_file = FileUtil(os.path.join(HOME_PATH, 'dmp.json'))

    yield dmp_file.path

    # ファイル削除
    dmp_file.delete()


@pytest.fixture()
def prepare_save_json():
    save_file = FileUtil(os.path.join(HOME_PATH, 'save.json'))
    save_file.delete()

    yield save_file.path

    # ファイル削除
    save_file.delete()


@pytest.fixture()
def prepare_package():
    work_dir = DirUtil(os.path.join(TEST_DIR, 'test_package'))
    work_dir.delete()
    work_dir.create()
    exp_dir = DirUtil(os.path.join(work_dir.path, 'test_exp'))
    exp_dir.create()

    yield exp_dir.path

    # フォルダ削除
    work_dir.delete()
