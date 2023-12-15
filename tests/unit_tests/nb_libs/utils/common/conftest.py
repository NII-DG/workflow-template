import os
import pytest

from tests.unit_tests.conftest import TEST_DIR
from tests.unit_tests.common.utils import FileUtil, DirUtil


@pytest.fixture()
def create_file():

    # ファイル作成
    path_exist = FileUtil(os.path.join(TEST_DIR, 'exist.txt'))
    path_exist.create()
    path_not_exist = FileUtil(os.path.join(TEST_DIR, 'not_exist.txt'))

    yield {'exist': path_exist.path, 'not_exist': path_not_exist.path}

    # ファイル削除
    path_exist.delete()


@pytest.fixture()
def prepare_cp_dir():

    # フォルダ構成
    # src_dir                   dst_dir
    #   ├ dir1                   ├ dir1
    #   │   ├ file11.txt        │   ├ file11.txt
    #   │   └ file12.txt        │   │
    #   │                        │   └ file13.txt
    #   ├ dir2                   │
    #   │   └ file22.txt        │
    #   │                        ├ dir3
    #   │                        │   └ file33.txt
    #   ├ file01.txt             ├ file01.txt
    #   └ file02.txt             │
    #                             └ file03.txt

    work_dir = DirUtil(os.path.join(TEST_DIR, 'test_cp_dir'))
    work_dir.delete()
    work_dir.create()

    # コピー元ディレクトリ
    src_dir = DirUtil(os.path.join(work_dir.path, 'src_dir'))
    src_dir.create()
    src_file01 = FileUtil(os.path.join(src_dir.path, 'file01.txt'))
    src_file01.create('src_file01')
    src_file02 = FileUtil(os.path.join(src_dir.path, 'file02.txt'))
    src_file02.create('src_file02')

    src_dir1 = DirUtil(os.path.join(src_dir.path, 'dir1'))
    src_dir1.create()
    src_file11 = FileUtil(os.path.join(src_dir1.path, 'file11.txt'))
    src_file11.create('src_file11')
    src_file12 = FileUtil(os.path.join(src_dir1.path, 'file12.txt'))
    src_file12.create('src_file12')

    src_dir2 = DirUtil(os.path.join(src_dir.path, 'dir2'))
    src_dir2.create()
    src_file22 = FileUtil(os.path.join(src_dir2.path, 'file22.txt'))
    src_file22.create('src_file22')

    # コピー先ディレクトリ
    dst_dir = DirUtil(os.path.join(work_dir.path, 'dst_dir'))
    dst_dir.create()
    dst_file01 = FileUtil(os.path.join(dst_dir.path, 'file01.txt'))
    dst_file01.create('dst_file01')
    dst_file03 = FileUtil(os.path.join(dst_dir.path, 'file03.txt'))
    dst_file03.create('dst_file03')

    dst_dir1 = DirUtil(os.path.join(dst_dir.path, 'dir1'))
    dst_dir1.create()
    dst_file11 = FileUtil(os.path.join(dst_dir1.path, 'file11.txt'))
    dst_file11.create('dst_file11')
    dst_file13 = FileUtil(os.path.join(dst_dir1.path, 'file13.txt'))
    dst_file13.create('dst_file13')

    dst_dir3 = DirUtil(os.path.join(dst_dir.path, 'dir3'))
    dst_dir3.create()
    dst_file33 = FileUtil(os.path.join(dst_dir3.path, 'file33.txt'))
    dst_file33.create('dst_file33')

    yield {'src': src_dir.path, 'dst': dst_dir.path}

    # フォルダ削除
    work_dir.delete()


@pytest.fixture()
def prepare_cp_file():

    work_dir = DirUtil(os.path.join(TEST_DIR, 'test_cp_file'))
    work_dir.delete()
    work_dir.create()

    # コピー元ファイル
    src_dir = DirUtil(os.path.join(work_dir.path, 'src_dir'))
    src_dir.create()

    src_dir1 = DirUtil(os.path.join(src_dir.path, 'dir1'))
    src_dir1.create()
    src_file11 = FileUtil(os.path.join(src_dir1.path, 'file11.txt'))
    src_file11.create('src_file11')

    src_dir2 = DirUtil(os.path.join(src_dir.path, 'dir2'))
    src_dir2.create()
    src_file21 = FileUtil(os.path.join(src_dir2.path, 'file21.txt'))
    src_file21.create('src_file21')
    src_file22 = FileUtil(os.path.join(src_dir2.path, 'file22.txt'))
    src_file22.create('src_file22')

    # コピー先ファイル
    dst_dir = DirUtil(os.path.join(work_dir.path, 'dst_dir'))
    dst_dir.create()

    dst_dir2 = DirUtil(os.path.join(dst_dir.path, 'dir2'))
    dst_dir2.create()

    dst_file22 = FileUtil(os.path.join(dst_dir2.path, 'file22.txt'))
    dst_file22.create('dst_file22')

    yield {'src': src_dir.path, 'dst': dst_dir.path}

    # フォルダ削除
    work_dir.delete()


@pytest.fixture()
def prepare_create_json_file():

    work_dir = DirUtil(os.path.join(TEST_DIR, 'test_create_json_file'))
    work_dir.delete()
    work_dir.create()

    exist_file = FileUtil(os.path.join(work_dir.path, 'exist.json'))
    exist_file.create_json({'exist_key': 'exist_value'})

    yield work_dir.path

    # フォルダ削除
    work_dir.delete()


@pytest.fixture()
def prepare_read_json_file():

    file = FileUtil(os.path.join(TEST_DIR, 'test.json'))
    file.create_json({'test_key': 'test_value'})

    yield file.path

    # 重複ファイル削除
    file.delete()
