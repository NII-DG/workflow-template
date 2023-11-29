import json
import os
import pytest
import shutil
from pathlib import Path

from tests.unit_tests.conftest import TEST_DIR


@pytest.fixture()
def create_file():

    # ファイル作成
    path_exist = os.path.join(TEST_DIR, 'exist.txt')
    path_not_exist = os.path.join(TEST_DIR, 'not_exist.txt')
    file_exist = Path(path_exist)
    file_exist.touch()

    yield {'exist': path_exist, 'not_exist': path_not_exist}

    # ファイル削除
    file_exist.unlink(True)


@pytest.fixture()
def prepare_cp_dir():

    work_dir = Path(os.path.join(TEST_DIR, 'test_cp_dir'))
    if os.path.isdir(work_dir):
        shutil.rmtree(work_dir)
    work_dir.mkdir()

    # コピー元ディレクトリ
    src_dir = Path(os.path.join(work_dir, 'src_dir'))
    src_dir.mkdir()
    src_file01 = Path(os.path.join(src_dir, 'file0_1.txt'))
    src_file01.touch()
    with src_file01.open(mode='w') as f:
        f.write('src_file01')
    src_file02 = Path(os.path.join(src_dir, 'file0_2.txt'))
    src_file02.touch()

    src_dir1 = Path(os.path.join(src_dir, 'dir1'))
    src_dir1.mkdir()
    src_file11 = Path(os.path.join(src_dir1, 'file1_1.txt'))
    src_file11.touch()
    with src_file11.open(mode='w') as f:
        f.write('src_file11')
    src_file12 = Path(os.path.join(src_dir1, 'file1_2.txt'))
    src_file12.touch()

    src_dir2 = Path(os.path.join(src_dir, 'dir2'))
    src_dir2.mkdir()
    src_file21 = Path(os.path.join(src_dir2, 'file2_1.txt'))
    src_file21.touch()

    # コピー先ディレクトリ
    dst_dir = Path(os.path.join(work_dir, 'dst_dir'))
    dst_dir.mkdir()
    dst_file01 = Path(os.path.join(dst_dir, 'file0_1.txt'))
    dst_file01.touch()
    with dst_file01.open(mode='w') as f:
        f.write('dst_file01')
    dst_file03 = Path(os.path.join(dst_dir, 'file0_3.txt'))
    dst_file03.touch()

    dst_dir1 = Path(os.path.join(dst_dir, 'dir1'))
    dst_dir1.mkdir()
    dst_file11 = Path(os.path.join(dst_dir1, 'file1_1.txt'))
    dst_file11.touch()
    with dst_file11.open(mode='w') as f:
        f.write('dst_file11')
    dst_file13 = Path(os.path.join(dst_dir1, 'file1_3.txt'))
    dst_file13.touch()

    dst_dir3 = Path(os.path.join(dst_dir, 'dir3'))
    dst_dir3.mkdir()
    dst_file31 = Path(os.path.join(dst_dir3, 'file3_1.txt'))
    dst_file31.touch()

    yield {'src': str(src_dir), 'dst': str(dst_dir)}

    # フォルダ削除
    shutil.rmtree(work_dir)


@pytest.fixture()
def prepare_cp_file():

    work_dir = Path(os.path.join(TEST_DIR, 'test_cp_file'))
    if os.path.isdir(work_dir):
        shutil.rmtree(work_dir)
    work_dir.mkdir()

    # コピー元ファイル
    src_dir = Path(os.path.join(work_dir, 'src_dir'))
    src_dir.mkdir()

    src_dir1 = Path(os.path.join(src_dir, 'dir1'))
    src_dir1.mkdir()
    src_file11 = Path(os.path.join(src_dir1, 'file1_1.txt'))
    src_file11.touch()

    src_dir2 = Path(os.path.join(src_dir, 'dir2'))
    src_dir2.mkdir()
    src_file21 = Path(os.path.join(src_dir2, 'file2_1.txt'))
    src_file21.touch()
    src_file22 = Path(os.path.join(src_dir2, 'file2_2.txt'))
    src_file22.touch()
    with src_file22.open(mode='w') as f:
        f.write('src_file22')

    # コピー先ファイル
    dst_dir = Path(os.path.join(work_dir, 'dst_dir'))
    dst_dir.mkdir()

    dst_dir2 = Path(os.path.join(dst_dir, 'dir2'))
    dst_dir2.mkdir()
    dst_file22 = Path(os.path.join(dst_dir2, 'file2_2.txt'))
    dst_file22.touch()
    with dst_file22.open(mode='w') as f:
        f.write('dst_file22')

    yield {'src': str(src_dir), 'dst': str(dst_dir)}

    # フォルダ削除
    shutil.rmtree(work_dir)


@pytest.fixture()
def prepare_create_json_file():

    work_dir = Path(os.path.join(TEST_DIR, 'test_create_json_file'))
    if os.path.isdir(work_dir):
        shutil.rmtree(work_dir)
    work_dir.mkdir()

    exist_file = Path(os.path.join(work_dir, 'exist.json'))
    exist_file.touch()
    with exist_file.open(mode='w') as f:
        json.dump({'exist_key': 'exist_value'}, f, indent=4)

    yield str(work_dir)

    # フォルダ削除
    shutil.rmtree(work_dir)


@pytest.fixture()
def prepare_read_json_file():

    file = Path(os.path.join(TEST_DIR, 'test.json'))
    file.touch()
    with file.open(mode='w') as f:
        json.dump({'test_key': 'test_value'}, f, indent=4)

    yield str(file)

    # 重複ファイル削除
    file.unlink(True)
