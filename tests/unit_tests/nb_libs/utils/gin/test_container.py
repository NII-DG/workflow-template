
import pytest
from requests import HTTPError
from nb_libs.utils.gin.container import add_container, patch_container, delete_container

from tests.unit_tests.common.utils import MockResponse, UnitTestError


def test_add_container(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/gin/test_container.py::test_add_container

    mocker.patch('nb_libs.utils.params.token.get_ginfork_token', return_value='token1')
    mocker.patch('nb_libs.utils.params.repository_id.get_repo_id', return_value='repo1')
    mocker.patch('nb_libs.utils.params.user_info.get_user_id', return_value='user1')

    mock_disp_info = mocker.patch('nb_libs.utils.message.display.display_info')
    mock_disp_warn = mocker.patch('nb_libs.utils.message.display.display_warm')
    mock_disp_err = mocker.patch('nb_libs.utils.message.display.display_err')

    res200 = MockResponse(200)
    mock_obj = mocker.patch('nb_libs.utils.gin.api.add_container', return_value=res200)

    # 正常ケース(research)
    add_container()
    mock_obj.assert_called_with(
        scheme='https',
        domain='test.gin-domain',
        token='token1',
        repo_id='repo1',
        user_id='user1',
        server_name='test_server',
        ipynb_url='https://test.binder-domain/test/notebooks/WORKFLOWS/notebooks/research/base_FLOW.ipynb',
    )
    assert mock_disp_info.call_count == 1

    mock_disp_info.reset_mock()
    mock_disp_warn.reset_mock()
    mock_disp_err.reset_mock()

    # 正常ケース(experiment)
    add_container('test_title')
    mock_obj.assert_called_with(
        scheme='https',
        domain='test.gin-domain',
        token='token1',
        repo_id='repo1',
        user_id='user1',
        server_name='test_server',
        ipynb_url='https://test.binder-domain/test/notebooks/WORKFLOWS/notebooks/experiment/experiment.ipynb',
        pkg_title='test_title',
    )
    assert mock_disp_info.call_count == 1

    mock_disp_info.reset_mock()
    mock_disp_warn.reset_mock()
    mock_disp_err.reset_mock()

    # コンテナがすでに存在する
    res1062 = MockResponse(400, json={'error': 'Error 1062: dummy message'})
    mocker.patch('nb_libs.utils.gin.api.add_container', return_value=res1062)
    add_container()
    assert mock_disp_warn.call_count == 1

    mock_disp_info.reset_mock()
    mock_disp_warn.reset_mock()
    mock_disp_err.reset_mock()

    # コンテナの追加に失敗
    res_unexpected = MockResponse(500, json={'error': 'Error 9999: Unexpected error'})
    mocker.patch('nb_libs.utils.gin.api.add_container', return_value=res_unexpected)
    with pytest.raises(HTTPError):
        add_container()
    assert mock_disp_err.call_count == 1

    mock_disp_info.reset_mock()
    mock_disp_warn.reset_mock()
    mock_disp_err.reset_mock()

    # 予期せぬエラー
    mocker.patch('nb_libs.utils.gin.api.add_container', side_effect=UnitTestError)
    with pytest.raises(UnitTestError):
        add_container()
    assert mock_disp_err.call_count == 1


def test_patch_container(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/gin/test_container.py::test_patch_container

    mocker.patch('nb_libs.utils.params.token.get_ginfork_token', return_value='token1')
    mocker.patch('nb_libs.utils.params.user_info.get_user_id', return_value='user1')

    mock_disp_err = mocker.patch('nb_libs.utils.message.display.display_err')

    # 正常ケース
    res200 = MockResponse(200)
    mock_obj = mocker.patch('nb_libs.utils.gin.api.patch_container', return_value=res200)
    patch_container()
    mock_obj.assert_called_with('https', 'test.gin-domain', 'token1', 'test_server', 'user1')

    mock_disp_err.reset_mock()

    # コンテナの更新に失敗
    res_unexpected = MockResponse(500)
    mocker.patch('nb_libs.utils.gin.api.patch_container', return_value=res_unexpected)
    with pytest.raises(HTTPError):
        patch_container()
    assert mock_disp_err.call_count == 1

    mock_disp_err.reset_mock()

    # 予期せぬエラー
    mocker.patch('nb_libs.utils.gin.api.patch_container', side_effect=UnitTestError)
    with pytest.raises(UnitTestError):
        patch_container()
    assert mock_disp_err.call_count == 1


def test_delete_container(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/gin/test_container.py::test_delete_container

    mocker.patch('nb_libs.utils.params.token.get_ginfork_token', return_value='token1')
    mocker.patch('nb_libs.utils.params.user_info.get_user_id', return_value='user1')

    mock_disp_info = mocker.patch('nb_libs.utils.message.display.display_info')
    mock_disp_err = mocker.patch('nb_libs.utils.message.display.display_err')
    mock_disp_msg = mocker.patch('nb_libs.utils.message.display.display_html_msg')

    # 正常ケース
    res200 = MockResponse(200)
    mock_obj = mocker.patch('nb_libs.utils.gin.api.delete_container', return_value=res200)
    delete_container()
    mock_obj.assert_called_with('https', 'test.gin-domain', 'token1', 'test_server', 'user1')
    assert mock_disp_info.call_count == 1
    assert mock_disp_msg.call_count == 1

    mock_disp_info.reset_mock()
    mock_disp_err.reset_mock()
    mock_disp_msg.reset_mock()

    # コンテナの削除に失敗
    res_unexpected = MockResponse(500)
    mocker.patch('nb_libs.utils.gin.api.delete_container', return_value=res_unexpected)
    with pytest.raises(HTTPError):
        delete_container()
    assert mock_disp_err.call_count == 1

    mock_disp_info.reset_mock()
    mock_disp_err.reset_mock()
    mock_disp_msg.reset_mock()

    # 予期せぬエラー
    mocker.patch('nb_libs.utils.gin.api.delete_container', side_effect=UnitTestError)
    with pytest.raises(UnitTestError):
        delete_container()
    assert mock_disp_err.call_count == 1
