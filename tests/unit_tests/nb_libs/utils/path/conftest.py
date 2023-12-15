import os
import pytest

from nb_libs.utils.path.path import EXPERIMENTS_PATH

from tests.unit_tests.common.utils import FileUtil


@pytest.fixture()
def create_duplicate_file():
    # 重複ファイル作成
    file_duplicate = FileUtil(os.path.join(EXPERIMENTS_PATH, 'new_package/input_data/dir/duplicate.txt'))
    file_duplicate.create()

    yield file_duplicate.path

    # 重複ファイル削除
    file_duplicate.delete()
