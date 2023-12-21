import os
import panel as pn
import pytest

from nb_libs.utils.ex_utils.save_util import (
    submit_message_callback,
    input_message,
    prepare_sync,
)
from nb_libs.utils.except_class.common_err import DidNotFinishError
from nb_libs.utils.path.path import EXPERIMENTS_PATH, EXP_DIR_PATH

from tests.unit_tests.common.utils import FileUtil


def test_submit_message_callback(prepare_save_json):
    # pytest -v -s tests/unit_tests/nb_libs/utils/ex_utils/test_save_util.py::test_submit_message_callback

    save_file = FileUtil(prepare_save_json)

    pn.extension()

    # 正常ケース
    test_text = pn.widgets.TextInput(name='test_input')
    test_text.value = 'test_commit_message'
    test_button = pn.widgets.Button(name='test_button', button_type='default')
    test_button.on_click(submit_message_callback(test_text, test_button, save_file.path))
    test_button._process_event(None)    # クリックイベントを発生させる
    assert save_file.exists()
    data = save_file.read_json()
    assert data['commit_message'] == 'test_commit_message'
    assert test_button.button_type == 'success'
    assert test_button.name == '入力を完了しました。'

    save_file.delete()

    # エラーケース
    test_text = pn.widgets.TextInput(name='test_input')
    test_text.value = ''
    test_button = pn.widgets.Button(name='test_button', button_type='default')
    test_button.on_click(submit_message_callback(test_text, test_button, save_file.path))
    test_button._process_event(None)    # クリックイベントを発生させる
    assert not save_file.exists()
    assert test_button.button_type == 'warning'
    assert test_button.name == '作業のログメッセージが入力されていません。入力後、再度クリックしてください。'


def test_input_message(prepare_save_json):
    # pytest -v -s tests/unit_tests/nb_libs/utils/ex_utils/test_save_util.py::test_input_message

    save_file = FileUtil(prepare_save_json)

    # エラーが発生しなければOK
    input_message(save_file.path)


def test_prepare_sync(mocker, prepare_save_json):
    # pytest -v -s tests/unit_tests/nb_libs/utils/ex_utils/test_save_util.py::test_prepare_sync

    save_file = FileUtil(prepare_save_json)
    commit_message = 'test_commit_message'
    save_file.create_json({
        'commit_message': commit_message
    })

    # 正常ケース
    exp_title = 'test_title'
    mocker.patch('nb_libs.utils.params.ex_pkg_info.exec_get_ex_title', return_value=exp_title)
    git_path = ['test_git_path']
    gitannex_path = ['test_gitannex_path']
    gitannex_files = ['test_gitannex_files']
    mocker.patch('nb_libs.utils.ex_utils.package.create_syncs_path', return_value=(git_path, gitannex_path, gitannex_files))

    sync_repo_args = prepare_sync(save_file.path, 'test.ipynb')

    exp_path = os.path.join(EXPERIMENTS_PATH, exp_title)
    notebook_path = os.path.join(EXP_DIR_PATH, 'test.ipynb')
    assert sync_repo_args['git_path'] == ['test_git_path', notebook_path]
    assert sync_repo_args['gitannex_path'] == ['test_gitannex_path']
    assert sync_repo_args['gitannex_files'] == ['test_gitannex_files']
    assert sync_repo_args['get_paths'] == [exp_path]
    assert sync_repo_args['message'] == exp_title + '_' + commit_message

    # エラーケース
    save_file.delete()
    with pytest.raises(DidNotFinishError):
        prepare_sync(save_file.path, 'test.ipynb')
