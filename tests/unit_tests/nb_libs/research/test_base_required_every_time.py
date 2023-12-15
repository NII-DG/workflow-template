import pytest
from requests.exceptions import RequestException

from nb_libs.research.base_required_every_time import (
    preparation_completed,
    del_build_token,
    datalad_create,
    ssh_create_key,
    upload_ssh_key,
    ssh_trust_gin,
    prepare_sync,
    setup_sibling,
    add_container,
    finished_setup,
    syncs_config,
)
from nb_libs.utils.except_class import DidNotFinishError
from nb_libs.utils.params import token, user_info

from tests.unit_tests.common.utils import UnitTestError, FileUtil

file_user = FileUtil(user_info.FILE_PATH)
file_token = FileUtil(token.FILE_PATH)


def test_preparation_completed(prepare_preparation_completed):
    # pytest -v -s tests/unit_tests/nb_libs/research/test_base_required_every_time.py::test_preparation_completed

    # 両方のファイルなし
    file_user.delete()
    file_token.delete()
    with pytest.raises(DidNotFinishError):
        preparation_completed()

    # ユーザーファイルあり/トークンファイルなし
    file_user.create()
    file_token.delete()
    with pytest.raises(DidNotFinishError):
        preparation_completed()

    # ユーザーファイルなし/トークンファイルあり
    file_user.delete()
    file_token.create()
    with pytest.raises(DidNotFinishError):
        preparation_completed()

    # 両方のファイルあり
    file_user.create()
    file_token.create()
    preparation_completed()


def test_del_build_token(mocker, prepare_preparation_completed):
    # pytest -v -s tests/unit_tests/nb_libs/research/test_base_required_every_time.py::test_del_build_token

    mocker.patch('nb_libs.utils.git.git_module.get_remote_url', return_value='http://dummy-url')
    mock_disp_err = mocker.patch('nb_libs.utils.message.display.display_err')

    # 事前準備未完了
    file_user.delete()
    file_token.delete()
    mocker.patch('nb_libs.utils.params.token.del_build_token_by_remote_origin_url')
    with pytest.raises(DidNotFinishError):
        del_build_token()

    mock_disp_err.reset_mock()

    # 事前準備完了
    file_user.create()
    file_token.create()
    del_build_token()
    assert mock_disp_err.call_count == 0

    mock_disp_err.reset_mock()

    # 削除失敗
    mocker.patch('nb_libs.utils.params.token.del_build_token_by_remote_origin_url', side_effect=RequestException())
    with pytest.raises(RequestException):
        del_build_token()
    assert mock_disp_err.call_count == 1

    mock_disp_err.reset_mock()

    # 削除失敗
    mocker.patch('nb_libs.utils.params.token.del_build_token_by_remote_origin_url', side_effect=UnitTestError())
    with pytest.raises(UnitTestError):
        del_build_token()
    assert mock_disp_err.call_count == 0


def test_datalad_create(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/research/test_base_required_every_time.py::test_datalad_create

    mocker.patch('nb_libs.research.base_required_every_time.preparation_completed')
    mocker.patch('nb_libs.utils.gin.sync.datalad_create')
    datalad_create()


def test_ssh_create_key(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/research/test_base_required_every_time.py::test_ssh_create_key

    mocker.patch('nb_libs.research.base_required_every_time.preparation_completed')
    mocker.patch('nb_libs.utils.gin.ssh.create_key')
    ssh_create_key()


def test_upload_ssh_key(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/research/test_base_required_every_time.py::test_upload_ssh_key

    mocker.patch('nb_libs.research.base_required_every_time.preparation_completed')
    mocker.patch('nb_libs.utils.gin.ssh.upload_ssh_key')
    upload_ssh_key()


def test_ssh_trust_gin(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/research/test_base_required_every_time.py::test_ssh_trust_gin

    mocker.patch('nb_libs.research.base_required_every_time.preparation_completed')
    mocker.patch('nb_libs.utils.gin.ssh.trust_gin')
    ssh_trust_gin()


def test_prepare_sync(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/research/test_base_required_every_time.py::test_prepare_sync

    mocker.patch('nb_libs.research.base_required_every_time.preparation_completed')
    mocker.patch('nb_libs.utils.gin.sync.prepare_sync')
    prepare_sync()


def test_setup_sibling(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/research/test_base_required_every_time.py::test_setup_sibling

    mocker.patch('nb_libs.research.base_required_every_time.preparation_completed')
    mocker.patch('nb_libs.utils.gin.sync.setup_sibling')
    mocker.patch('nb_libs.utils.gin.sync.push_annex_branch')
    setup_sibling()


def test_add_container(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/research/test_base_required_every_time.py::test_add_container

    mocker.patch('nb_libs.research.base_required_every_time.preparation_completed')
    mocker.patch('nb_libs.utils.gin.container.add_container')
    add_container()


def test_finished_setup(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/research/test_base_required_every_time.py::test_finished_setup

    mocker.patch('nb_libs.research.base_required_every_time.preparation_completed')
    mocker.patch('nb_libs.utils.flow.module.put_mark_research')
    finished_setup()


def test_syncs_config(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/research/test_base_required_every_time.py::test_syncs_config

    mocker.patch('nb_libs.research.base_required_every_time.preparation_completed')
    mocker.patch('nb_libs.utils.flow.module.put_mark_research')
    git_path, commit_message = syncs_config()
    assert len(git_path) == 3
    assert commit_message
