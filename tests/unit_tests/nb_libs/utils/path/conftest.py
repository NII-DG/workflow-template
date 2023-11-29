import os
import pathlib
import pytest

from nb_libs.utils.path.path import EXPERIMENTS_PATH


@pytest.fixture()
def create_duplicate_file():
    # 重複ファイル作成
    path_duplicate = os.path.join(EXPERIMENTS_PATH, 'new_package/input_data/dir/duplicate.txt')
    file_duplicate = pathlib.Path(path_duplicate)
    file_duplicate.parents[0].mkdir(parents=True, exist_ok=True)
    file_duplicate.touch()

    yield path_duplicate

    # 重複ファイル削除
    file_duplicate.unlink(True)
