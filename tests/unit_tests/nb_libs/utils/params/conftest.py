import json
import os
import pytest
import shutil

from nb_libs.utils.params.ex_pkg_info import FILE_PATH as EX_PKG_INFO_FILE_PATH
from nb_libs.utils.params.param_json import PARAM_FILE_PATH
from nb_libs.utils.params.repository_id import FILE_PATH as REPO_ID_FILE_PATH
from nb_libs.utils.params.token import FILE_PATH as TOKEN_FILE_PATH
from nb_libs.utils.params.user_info import FILE_PATH as USER_INFO_FILE_PATH


@pytest.fixture()
def create_ex_pkg_info_file():
    # ファイル作成
    if os.path.exists(EX_PKG_INFO_FILE_PATH):
        os.remove(EX_PKG_INFO_FILE_PATH)
    ex_pkg_info = {'ex_pkg_name': 'test_package'}
    with open(EX_PKG_INFO_FILE_PATH, 'w') as f:
        json.dump(ex_pkg_info, f, indent=4)

    yield

    # ファイル削除
    if os.path.exists(EX_PKG_INFO_FILE_PATH):
        os.remove(EX_PKG_INFO_FILE_PATH)


@pytest.fixture()
def delete_ex_pkg_info_file():
    # ファイル削除
    if os.path.exists(EX_PKG_INFO_FILE_PATH):
        os.remove(EX_PKG_INFO_FILE_PATH)

    yield

    # ファイル削除
    if os.path.exists(EX_PKG_INFO_FILE_PATH):
        os.remove(EX_PKG_INFO_FILE_PATH)


@pytest.fixture()
def backup_parameter_file():
    # パラメータファイルのバックアップ作成
    shutil.copy2(PARAM_FILE_PATH, PARAM_FILE_PATH + '.bk')

    yield

    # パラメータファイルをもとに戻す
    shutil.move(PARAM_FILE_PATH + '.bk', PARAM_FILE_PATH)


@pytest.fixture()
def create_repo_id_file():
    # ファイル作成
    if os.path.exists(REPO_ID_FILE_PATH):
        os.remove(REPO_ID_FILE_PATH)
    repo_id = 'test_repo_id'
    with open(REPO_ID_FILE_PATH, 'w') as f:
        f.write(repo_id)

    yield

    # ファイル削除
    if os.path.exists(REPO_ID_FILE_PATH):
        os.remove(REPO_ID_FILE_PATH)


@pytest.fixture()
def create_token_file():
    # ファイル作成
    if os.path.exists(TOKEN_FILE_PATH):
        os.remove(TOKEN_FILE_PATH)
    token_info = {'ginfork_token': 'test_token'}
    with open(TOKEN_FILE_PATH, 'w') as f:
        json.dump(token_info, f, indent=4)

    yield

    # ファイル削除
    if os.path.exists(TOKEN_FILE_PATH):
        os.remove(TOKEN_FILE_PATH)


@pytest.fixture()
def delete_token_file():
    # ファイル削除
    if os.path.exists(TOKEN_FILE_PATH):
        os.remove(TOKEN_FILE_PATH)

    yield

    # ファイル削除
    if os.path.exists(TOKEN_FILE_PATH):
        os.remove(TOKEN_FILE_PATH)


@pytest.fixture()
def create_user_info_file():
    # ファイル作成
    if os.path.exists(USER_INFO_FILE_PATH):
        os.remove(USER_INFO_FILE_PATH)
    user_info = {'user_id': 'test_user_id'}
    with open(USER_INFO_FILE_PATH, 'w') as f:
        json.dump(user_info, f, indent=4)

    yield

    # ファイル削除
    if os.path.exists(USER_INFO_FILE_PATH):
        os.remove(USER_INFO_FILE_PATH)


@pytest.fixture()
def delete_user_info_file():
    # ファイル削除
    if os.path.exists(USER_INFO_FILE_PATH):
        os.remove(USER_INFO_FILE_PATH)

    yield

    # ファイル削除
    if os.path.exists(USER_INFO_FILE_PATH):
        os.remove(USER_INFO_FILE_PATH)
