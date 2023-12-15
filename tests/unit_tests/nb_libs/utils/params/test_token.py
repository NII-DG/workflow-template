import pytest

from nb_libs.utils.params.token import (
    FILE_PATH,
    set_ginfork_token,
    get_ginfork_token,
    del_build_token_by_remote_origin_url,
)

from tests.unit_tests.common.utils import MockResponse, FileUtil


def test_set_ginfork_token(prepare_token_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_token.py::test_set_ginfork_token

    # ファイル削除
    token_info = FileUtil(FILE_PATH)
    token_info.delete()

    set_ginfork_token('test_token')
    assert token_info.exists()
    data = token_info.read_json()
    assert data['ginfork_token'] == 'test_token'


def test_get_ginfork_token(prepare_token_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_token.py::test_get_ginfork_token

    # ファイル作成
    token_info = FileUtil(FILE_PATH)
    token_info.create_json({'ginfork_token': 'test_token'})

    ret = get_ginfork_token()
    assert ret == 'test_token'


def test_del_build_token_by_remote_origin_url(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_token.py::test_del_build_token_by_remote_origin_url

    url_private = 'https://user:token@test.github-domain/test_user/test_repo.git'
    url_public = 'https://test.github-domain/test_user/test_repo.git'

    # 正常ケース
    res200 = MockResponse(200)
    mocker.patch('nb_libs.utils.gin.api.delete_access_token', return_value=res200)
    del_build_token_by_remote_origin_url(url_private)
    del_build_token_by_remote_origin_url(url_private, display_msg=False)

    # 認証失敗
    res401 = MockResponse(401)
    mocker.patch('nb_libs.utils.gin.api.delete_access_token', return_value=res401)
    del_build_token_by_remote_origin_url(url_private)
    del_build_token_by_remote_origin_url(url_private, display_msg=False)

    # 処理できない
    res422 = MockResponse(422)
    mocker.patch('nb_libs.utils.gin.api.delete_access_token', return_value=res422)
    del_build_token_by_remote_origin_url(url_private)
    del_build_token_by_remote_origin_url(url_private, display_msg=False)

    # 予期せぬエラー
    res500 = MockResponse(500)
    mocker.patch('nb_libs.utils.gin.api.delete_access_token', return_value=res500)
    with pytest.raises(Exception):
        del_build_token_by_remote_origin_url(url_private)
    del_build_token_by_remote_origin_url(url_private, display_msg=False)

    # パブリックリポジトリ
    del_build_token_by_remote_origin_url(url_public)
