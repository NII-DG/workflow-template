import pytest

from requests.exceptions import RequestException

from nb_libs.utils.gin.ssh import (
    create_key,
    upload_ssh_key,
    trust_gin,
    config_GIN,
    write_GIN_config,
    __SSH_KEY_PATH as SSH_KEY_PATH,
    __SSH_PUB_KEY_PATH as SSH_PUB_KEY_PATH,
    __SSH_CONFIG as SSH_CONFIG,
)

from tests.unit_tests.common.utils import MockResponse, FileUtil


def test_create_key(mocker, prepare_ssh_key):
    # pytest -v -s tests/unit_tests/nb_libs/utils/gin/test_ssh.py::test_create_key

    ssh_key = FileUtil(SSH_KEY_PATH)
    ssh_pub_key = FileUtil(SSH_PUB_KEY_PATH)

    mock_disp_info = mocker.patch('nb_libs.utils.message.display.display_info')
    mock_disp_warn = mocker.patch('nb_libs.utils.message.display.display_warm')

    # キーが存在しない
    ssh_key.delete()
    ssh_pub_key.delete()
    create_key()
    assert ssh_key.exists()
    assert ssh_pub_key.exists()
    assert mock_disp_info.call_count == 1
    assert mock_disp_warn.call_count == 0

    mock_disp_info.reset_mock()
    mock_disp_warn.reset_mock()

    # キーが存在する
    create_key()
    assert mock_disp_info.call_count == 0
    assert mock_disp_warn.call_count == 1


def test_upload_ssh_key(mocker, create_ssh_pub_key):
    # pytest -v -s tests/unit_tests/nb_libs/utils/gin/test_ssh.py::test_upload_ssh_key

    mock_disp_info = mocker.patch('nb_libs.utils.message.display.display_info')
    mock_disp_warn = mocker.patch('nb_libs.utils.message.display.display_warm')
    mock_disp_err = mocker.patch('nb_libs.utils.message.display.display_err')

    mocker.patch('nb_libs.utils.params.token.get_ginfork_token', return_value='test_token')

    # 正常ケース
    res = MockResponse(201)
    mock_obj = mocker.patch('nb_libs.utils.gin.api.upload_key', return_value=res)
    upload_ssh_key()
    mock_obj.assert_called_with('https', 'test.gin-domain', 'test_token', 'test_key')
    assert mock_disp_info.call_count == 1
    assert mock_disp_warn.call_count == 0
    assert mock_disp_err.call_count == 0

    mock_disp_info.reset_mock()
    mock_disp_warn.reset_mock()
    mock_disp_err.reset_mock()

    # 公開鍵登録済み
    res = MockResponse(200, {'message': 'Key content has been used as non-deploy key'})
    mocker.patch('nb_libs.utils.gin.api.upload_key', return_value=res)
    upload_ssh_key()
    assert mock_disp_info.call_count == 0
    assert mock_disp_warn.call_count == 1
    assert mock_disp_err.call_count == 0

    mock_disp_info.reset_mock()
    mock_disp_warn.reset_mock()
    mock_disp_err.reset_mock()

    # 登録失敗
    res = MockResponse(400, {'message': ''})
    mocker.patch('nb_libs.utils.gin.api.upload_key', return_value=res)
    with pytest.raises(RequestException):
        upload_ssh_key()
    assert mock_disp_info.call_count == 0
    assert mock_disp_warn.call_count == 0
    assert mock_disp_err.call_count == 1

    mock_disp_info.reset_mock()
    mock_disp_warn.reset_mock()
    mock_disp_err.reset_mock()

    # 予期せぬエラー
    res = MockResponse(500)
    mocker.patch('nb_libs.utils.gin.api.upload_key', return_value=res)
    with pytest.raises(Exception):
        upload_ssh_key()
    assert mock_disp_info.call_count == 0
    assert mock_disp_warn.call_count == 0
    assert mock_disp_err.call_count == 1


def test_trust_gin(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/gin/test_ssh.py::test_trust_gin

    mock_obj = mocker.patch('nb_libs.utils.gin.ssh.config_GIN')
    trust_gin()
    mock_obj.assert_called_with(ginHttp='https://test.gin-domain')


def test_config_GIN():
    # pytest -v -s tests/unit_tests/nb_libs/utils/gin/test_ssh.py::test_config_GIN

    config_file = FileUtil(SSH_CONFIG)

    # 設定ファイルなし
    config_file.delete()
    config_GIN('https://test.gin-domain')
    data = config_file.read()
    expected = '\n'.join([
        '',
        'host test.gin-domain',
        '\tStrictHostKeyChecking no',
        '\tUserKnownHostsFile=/dev/null',
        '',
    ])
    assert data == expected

    # 設定ファイルあり 設定なし
    input = '\n'.join([
        '',
        'host test2.gin-domain',
        '\tStrictHostKeyChecking no',
        '\tUserKnownHostsFile=/dev/null',
        '',
    ])
    config_file.create(input)
    config_GIN('https://test.gin-domain')
    data = config_file.read()
    expected = '\n'.join([
        '',
        'host test2.gin-domain',
        '\tStrictHostKeyChecking no',
        '\tUserKnownHostsFile=/dev/null',
        '',
        'host test.gin-domain',
        '\tStrictHostKeyChecking no',
        '\tUserKnownHostsFile=/dev/null',
        '',
    ])
    assert data == expected

    # 設定ファイルあり 設定あり
    input = '\n'.join([
        '',
        'host test.gin-domain',
        '\tStrictHostKeyChecking no',
        '\tUserKnownHostsFile=/dev/null',
        '',
        'host test2.gin-domain',
        '\tStrictHostKeyChecking no',
        '\tUserKnownHostsFile=/dev/null',
        '',
    ])
    config_file.create(input)
    config_GIN('https://test.gin-domain')
    data = config_file.read()
    assert data == input


def test_write_GIN_config(delete_config):
    # pytest -v -s tests/unit_tests/nb_libs/utils/gin/test_ssh.py::test_write_GIN_config

    write_GIN_config('w', 'test_domain')

    config = FileUtil(SSH_CONFIG)
    assert config.exists()
    data = config.read()
    assert data == '\nhost test_domain\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile=/dev/null\n'