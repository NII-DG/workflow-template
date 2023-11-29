import time

from nb_libs.utils.gin.api import (
    search_public_repo,
    search_repo,
    delete_access_token,
    create_token_for_launch,
    get_server_info,
    get_token_for_auth,
    create_token_for_auth,
    get_user_info,
    get_repo_info,
    upload_key,
    add_container,
    patch_container,
    delete_container,
    get_repo_metadata,
)

from tests.unit_tests.common.utils import MockResponse


def test_search_public_repo(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_search_public_repo

    mock_obj = mocker.patch('requests.get', return_value=MockResponse(200))
    res = search_public_repo('https', 'localhost', 'repo_id')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/repos/search'
    expected_param = {'id': 'repo_id'}
    mock_obj.assert_called_with(url=expected_url, params=expected_param)


def test_search_repo(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_search_repo

    mock_obj = mocker.patch('requests.get', return_value=MockResponse(200))
    res = search_repo('https', 'localhost', 'repo_id', 'user_id', 'token')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/repos/search/user'
    expected_param = {'id': 'repo_id', 'uid': 'user_id', 'token': 'token'}
    mock_obj.assert_called_with(url=expected_url, params=expected_param)


def test_delete_access_token(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_delete_access_token

    mock_obj = mocker.patch('requests.delete', return_value=MockResponse(200))
    res = delete_access_token('https', 'localhost', 'token')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/user/token/delete'
    expected_param = {'token': 'token'}
    mock_obj.assert_called_with(url=expected_url, params=expected_param)


def test_create_token_for_launch(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_create_token_for_launch

    mock_obj = mocker.patch('requests.post', return_value=MockResponse(200))
    res = create_token_for_launch('https', 'localhost', 'token')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/user/token/forlaunch'
    expected_param = {'token': 'token'}
    mock_obj.assert_called_with(url=expected_url, params=expected_param)


def test_get_server_info(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_get_server_info

    mock_obj = mocker.patch('requests.get', return_value=MockResponse(200))
    res = get_server_info('https', 'localhost')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/gin'
    mock_obj.assert_called_with(url=expected_url)


def test_get_token_for_auth(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_get_token_for_auth

    mock_obj = mocker.patch('requests.get', return_value=MockResponse(200))
    res = get_token_for_auth('https', 'localhost', 'user_name', 'password')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/users/user_name/tokens'
    expected_auth = ('user_name', 'password')
    mock_obj.assert_called_with(url=expected_url, auth=expected_auth)


def test_create_token_for_auth(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::teset_create_token_for_auth

    mock_obj = mocker.patch('requests.post', return_value=MockResponse(200))
    res = create_token_for_auth('https', 'localhost', 'user_name', 'password')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/users/user_name/tokens'
    expected_auth = ('user_name', 'password')
    expected_data = {'name': 'system-generated'}
    mock_obj.assert_called_with(url=expected_url, data=expected_data, auth=expected_auth)


def test_get_user_info(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_get_user_info

    mock_obj = mocker.patch('requests.get', return_value=MockResponse(200))
    res = get_user_info('https', 'localhost', 'token')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/user'
    expected_param = {'token': 'token'}
    mock_obj.assert_called_with(url=expected_url, params=expected_param)


def test_get_repo_info(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_get_repo_info

    mock_obj = mocker.patch('requests.get', return_value=MockResponse(200))
    res = get_repo_info('https', 'localhost', 'user_name', 'repo_name', 'token')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/repos/user_name/repo_name'
    expected_param = {'token': 'token'}
    mock_obj.assert_called_with(url=expected_url, params=expected_param)


def test_upload_key(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_upload_key

    mock_obj = mocker.patch('requests.post', return_value=MockResponse(200))
    time_now = time.time()
    mocker.patch('time.time', return_value=time_now)
    res = upload_key('https', 'localhost', 'token', 'pubkey')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/user/keys'
    expected_param = {'token': 'token'}
    expected_data = {
        'title': 'system-generated-' + str(time_now),
        'key': 'pubkey'
    }
    mock_obj.assert_called_with(url=expected_url, params=expected_param, data=expected_data)


def test_add_container(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_add_container

    mock_obj = mocker.patch('requests.post', return_value=MockResponse(200))

    res = add_container('https', 'localhost', 'token', 'repo_id', 'user_id', 'server_name', 'ipynb_url')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/container'
    expected_param = {'token': 'token'}
    expected_data = {
        'repo_id': 'repo_id',
        'user_id': 'user_id',
        'server_name': 'server_name',
        'url': 'ipynb_url',
    }
    mock_obj.assert_called_with(url=expected_url, params=expected_param, data=expected_data)

    res = add_container('https', 'localhost', 'token', 'repo_id', 'user_id', 'server_name', 'ipynb_url', 'pkg_title')
    assert res.status_code == 200

    expected_data = {
        'repo_id': 'repo_id',
        'user_id': 'user_id',
        'server_name': 'server_name',
        'url': 'ipynb_url',
        'experiment_package': 'pkg_title',
    }
    mock_obj.assert_called_with(url=expected_url, params=expected_param, data=expected_data)


def test_patch_container(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_patch_container

    mock_obj = mocker.patch('requests.patch', return_value=MockResponse(200))
    res = patch_container('https', 'localhost', 'token', 'server_name', 'user_id')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/container'
    expected_param = {
        'token': 'token',
        'server_name': 'server_name',
        'user_id': 'user_id',
    }
    mock_obj.assert_called_with(url=expected_url, params=expected_param)


def test_delete_container(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_delete_container

    mock_obj = mocker.patch('requests.delete', return_value=MockResponse(200))
    res = delete_container('https', 'localhost', 'token', 'server_name', 'user_id')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/container'
    expected_param = {
        'token': 'token',
        'server_name': 'server_name',
        'user_id': 'user_id',
    }
    mock_obj.assert_called_with(url=expected_url, params=expected_param)


def test_get_repo_metadata(mocker):
    # pytest -v -s tests/nb_libs/utils/gin/test_api.py::test_get_repo_metadata

    mock_obj = mocker.patch('requests.get', return_value=MockResponse(200))
    res = get_repo_metadata('https', 'localhost', 'token', 'repo_id', 'branch')
    assert res.status_code == 200

    expected_url = 'https://localhost/api/v1/repos/repo_id/branch/metadata'
    expected_param = {'token': 'token'}
    mock_obj.assert_called_with(url=expected_url, params=expected_param)
