import contextlib
import os
import pytest
import tarfile
import unix_ar
import wget

from nb_libs.utils.path.path import HOME_PATH, SYS_PATH, EXPERIMENTS_PATH

from .common.utils import FileUtil, DirUtil

TEST_DIR = os.path.join(HOME_PATH, 'unit_test')


def download_font_file():
    dir_font = DirUtil(os.path.join(HOME_PATH, '.fonts'))
    dir_font.delete()
    dir_font.create()
    dir_tmp = DirUtil(os.path.join(dir_font.path, 'tmp'))
    dir_tmp.create()

    # フォントファイルダウンロード
    file_name = 'fonts-ipafont-gothic_00303-18ubuntu1_all.deb'
    url = f'http://archive.ubuntu.com/ubuntu/pool/universe/f/fonts-ipafont/{file_name}'
    with contextlib.redirect_stdout(open(os.devnull, 'w')):     # 標準出力を一時的に無効化する
        font_deb = wget.download(url=url, out=dir_tmp.path)
    # deb形式の解凍
    ar_file = unix_ar.open(font_deb)
    tarball = ar_file.open('data.tar.xz')
    tar_file = tarfile.open(fileobj=tarball)
    tar_file.extractall(path=dir_tmp.path)
    # フォントファイルを配置
    font_file = FileUtil(os.path.join(dir_tmp.path, 'usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'))
    font_file.copy(os.path.join(dir_font.path, 'ipag.ttf'))
    dir_tmp.delete()


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

    download_font_file()

    yield
    # 後処理

    # フォルダ削除
    dir_test.delete()
    dir_experiments.delete()
    dir_sys.delete()
