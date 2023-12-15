import pytest

from nb_libs.utils.except_class.common_err import NoValueInDgFileError
from nb_libs.utils.params.param_json import (
    PARAM_FILE_PATH,
    get_params,
    get_gin_http,
    update_param_url,
    get_core_scheme_netloc
)

from tests.unit_tests.common.utils import MockResponse, FileUtil


def test_get_params():
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_param_json.py::test_get_params

    assert get_params()


def test_get_gin_http(backup_parameter_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_param_json.py::test_get_gin_http

    param_file = FileUtil(PARAM_FILE_PATH)

    # 正常ケース
    ret = get_gin_http()
    assert ret == 'https://test.gin-domain'

    # テスト用にパラメータファイルを修正
    params = param_file.read_json()
    params['siblings']['ginHttp'] = ''
    param_file.create_json(params)

    # 未設定のケース
    with pytest.raises(NoValueInDgFileError):
        get_gin_http()


def test_update_param_url(mocker, backup_parameter_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_param_json.py::test_update_param_url

    param_file = FileUtil(PARAM_FILE_PATH)
    url_remote = 'https://user:token@test.github-domain/test_dg/test_repo.git'

    # サーバー情報取得失敗
    res404 = MockResponse(404)
    mock_obj = mocker.patch('nb_libs.utils.gin.api.get_server_info', return_value=res404)
    with pytest.raises(Exception):
        update_param_url(url_remote)
    assert mock_obj.call_count == 6

    # 正常ケース
    res200 = MockResponse(200, {'http': 'https://test.update-domain/', 'ssh': 'git@test.update-domain:'})
    mocker.patch('nb_libs.utils.gin.api.get_server_info', return_value=res200)
    update_param_url(url_remote)
    params = param_file.read_json()
    assert params['siblings']['ginHttp'] == 'https://test.update-domain'
    assert params['siblings']['ginSsh'] == 'git@test.update-domain:'


def test_get_core_scheme_netloc():
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_param_json.py::test_get_core_scheme_netloc

    ret = get_core_scheme_netloc()
    assert ret[0] == 'https'
    assert ret[1] == 'test.dgcore-domain'
