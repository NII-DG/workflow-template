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
    file_font = FileUtil(os.path.join(HOME_PATH, '.fonts', 'ipag.ttf'))
    if file_font.exists():
        return

    dir_font = DirUtil(os.path.join(HOME_PATH, '.fonts'))
    dir_font.create()
    dir_tmp = DirUtil(os.path.join(dir_font.path, 'tmp'))
    dir_tmp.create()

    # フォントファイルダウンロード
    file_name = 'fonts-ipafont-gothic_00303-18ubuntu1_all.deb'
    url = f'http://archive.ubuntu.com/ubuntu/pool/universe/f/fonts-ipafont/{file_name}'
    with contextlib.redirect_stdout(open(os.devnull, 'w')):     # 標準出力を一時的に無効化する
        deb_font = wget.download(url=url, out=dir_tmp.path)
    # deb形式の解凍
    file_ar = unix_ar.open(deb_font)
    tarball = file_ar.open('data.tar.xz')
    file_tar = tarfile.open(fileobj=tarball)
    file_tar.extractall(path=dir_tmp.path)
    # フォントファイルを配置
    file_font = FileUtil(os.path.join(dir_tmp.path, 'usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'))
    file_font.copy(os.path.join(dir_font.path, 'ipag.ttf'))
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

    # フォントファイルのダウンロード
    download_font_file()

    yield
    # 後処理

    # フォルダ削除
    dir_test.delete()
    dir_experiments.delete()
    dir_sys.delete()
