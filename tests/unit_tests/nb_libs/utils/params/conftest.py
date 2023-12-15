import pytest

from nb_libs.utils.params.ex_pkg_info import FILE_PATH as EX_PKG_INFO_FILE_PATH
from nb_libs.utils.params.param_json import PARAM_FILE_PATH
from nb_libs.utils.params.repository_id import FILE_PATH as REPO_ID_FILE_PATH
from nb_libs.utils.params.token import FILE_PATH as TOKEN_FILE_PATH
from nb_libs.utils.params.user_info import FILE_PATH as USER_INFO_FILE_PATH

from tests.unit_tests.common.utils import FileUtil


@pytest.fixture()
def prepare_ex_pkg_info_file():
    yield

    # ファイル削除
    ex_pkg_info = FileUtil(EX_PKG_INFO_FILE_PATH)
    ex_pkg_info.delete()


@pytest.fixture()
def backup_parameter_file():
    # パラメータファイルのバックアップ作成
    param_file = FileUtil(PARAM_FILE_PATH)
    backup = param_file.copy(PARAM_FILE_PATH + '.bk')

    yield

    # パラメータファイルをもとに戻す
    backup.move(PARAM_FILE_PATH)


@pytest.fixture()
def prepare_repo_id_file():
    yield

    # ファイル削除
    repo_id = FileUtil(REPO_ID_FILE_PATH)
    repo_id.delete()


@pytest.fixture()
def prepare_token_file():
    yield

    # ファイル削除
    token_info = FileUtil(TOKEN_FILE_PATH)
    token_info.delete()


@pytest.fixture()
def prepare_user_info_file():
    yield

    # ファイル削除
    user_info = FileUtil(USER_INFO_FILE_PATH)
    user_info.delete()
