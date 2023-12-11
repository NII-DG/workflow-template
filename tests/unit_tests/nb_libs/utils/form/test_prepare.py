import os
import panel as pn
import pytest

from panel.widgets import TextInput, PasswordInput, Button, StaticText
from requests import HTTPError

from nb_libs.utils.form.prepare import (
    submit_user_auth_callback,
    validate_format_username,
    validate_format_input,
    validate_user_auth,
    validate_experiment_folder_name,
    validate_parameter_folder_name,
    validate_select_default,
    validate_commit_message,
    setup_local,
    initial_gin_user_auth,
    create_user_auth_forms,
    create_param_form,
    create_select,
    create_button,
    layout_error_text,
)
from nb_libs.utils.except_class import Unauthorized
from nb_libs.utils.path.path import EXPERIMENTS_PATH

from tests.unit_tests.common.utils import MockResponse, UnitTestError


def test_submit_user_auth_callback(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_submit_user_auth_callback

    pn.extension()
    error_message = StaticText()
    button = Button()

    # 正常ケース
    user_auth_forms = [TextInput(value='user_name'), PasswordInput(value='password')]
    button.on_click(submit_user_auth_callback(user_auth_forms, error_message, button))
    mocker.patch('nb_libs.utils.form.prepare.setup_local')
    button._process_event(None)     # クリックイベントを発生させる
    assert button.button_type == 'success'
    assert button.name == '認証が正常に完了しました。次の手順へお進みください。'

    # 入力不正(ユーザー名が空欄)
    user_auth_forms = [TextInput(value=''), PasswordInput(value='password')]
    button.on_click(submit_user_auth_callback(user_auth_forms, error_message, button))
    mocker.patch('nb_libs.utils.form.prepare.setup_local')
    button._process_event(None)     # クリックイベントを発生させる
    assert button.button_type == 'warning'
    assert button.name == 'ユーザー名が入力されていません。ユーザー名を入力し再度、ボタンをクリックしてください。'

    # 認証失敗
    user_auth_forms = [TextInput(value='user_name'), PasswordInput(value='password')]
    button.on_click(submit_user_auth_callback(user_auth_forms, error_message, button))
    mocker.patch('nb_libs.utils.form.prepare.setup_local', side_effect=Unauthorized())
    button._process_event(None)     # クリックイベントを発生させる
    assert button.button_type == 'warning'
    assert button.name == 'ユーザー名、またはパスワードが間違っています。再度、入力しボタンをクリックしてください。'

    # GIN-forkとの通信失敗
    mocker.patch('nb_libs.utils.form.prepare.setup_local', side_effect=HTTPError('test_message'))
    button._process_event(None)     # クリックイベントを発生させる
    assert button.button_type == 'danger'
    assert button.name == '現在、通信不良が発生しています。'
    assert error_message.value == 'ERROR : requests.exceptions.HTTPError: test_message'

    # 予期せぬエラー
    mocker.patch('nb_libs.utils.form.prepare.setup_local', side_effect=UnitTestError('test_message'))
    button._process_event(None)     # クリックイベントを発生させる
    assert button.button_type == 'danger'
    assert button.name == '想定外のエラーが発生しました。システム担当者にご連絡ください。'
    assert error_message.value == 'ERROR : tests.unit_tests.common.utils.UnitTestError: test_message'


def test_validate_format_username():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_validate_format_username

    # 使用可能な文字のみ
    user_name = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.'
    assert validate_format_username(user_name)

    # 文字数0
    user_name = ''
    assert not validate_format_username(user_name)

    # 使用不可能な文字あり
    user_name = 'a!'
    assert not validate_format_username(user_name)


def test_validate_format_input():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_validate_format_input

    # 使用可能な文字のみ(50文字以内)
    input_text = 'abcdefghijklmnopqrstuvwxyz'
    assert validate_format_input(input_text)
    input_text = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    assert validate_format_input(input_text)
    input_text = '0123456789-_.'
    assert validate_format_input(input_text)

    # 文字数0
    input_text = ''
    assert not validate_format_input(input_text)
    # 文字数1
    input_text = 'a'
    assert validate_format_input(input_text)
    # 文字数50
    input_text = ''.join(['a' for i in range(50)])
    assert len(input_text) == 50
    assert validate_format_input(input_text)
    # 文字数51
    input_text = ''.join(['a' for i in range(51)])
    assert len(input_text) == 51
    assert not validate_format_input(input_text)

    # 使用不可能な文字あり
    input_text = 'a!'
    assert not validate_format_input(input_text)


def test_validate_user_auth():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_validate_user_auth

    # チェックOK
    button = Button()
    assert validate_user_auth('user_name', 'password', button)

    # ユーザー名が空欄
    button = Button()
    assert not validate_user_auth('', 'password', button)
    assert button.button_type == 'warning'
    assert button.name == 'ユーザー名が入力されていません。ユーザー名を入力し再度、ボタンをクリックしてください。'

    # ユーザー名が不正
    button = Button()
    assert not validate_user_auth('a!', 'password', button)
    assert button.button_type == 'warning'
    assert button.name == 'ユーザー名は英数字および"-", "_", "."のみで入力し再度、ボタンをクリックしてください。'

    # パスワードが空欄
    button = Button()
    assert not validate_user_auth('user_name', '', button)
    assert button.button_type == 'warning'
    assert button.name == 'パスワードが入力されていません。パスワードを入力し再度、ボタンをクリックしてください。'


def test_validate_experiment_folder_name(create_package_dir):
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_validate_experiment_folder_name

    package_exist = create_package_dir
    package_not_exist = os.path.join(EXPERIMENTS_PATH, 'package_not_exist')

    # チェックOK
    button = Button()
    assert validate_experiment_folder_name('test_package', package_not_exist, '実験パッケージ名', button)

    # パッケージ名空欄
    button = Button()
    assert not validate_experiment_folder_name('', package_not_exist, '実験パッケージ名', button)
    assert button.button_type == 'warning'
    assert button.name == '実験パッケージ名が入力されていません。実験パッケージ名を入力し再度、ボタンをクリックしてください。'

    # パッケージ名不正
    button = Button()
    assert not validate_experiment_folder_name('a!', package_not_exist, '実験パッケージ名', button)
    assert button.button_type == 'warning'
    assert button.name == '実験パッケージ名は50文字以内, 半角英数字, および"-", "_", "."のみで入力してください。'

    # フォルダが存在する
    button = Button()
    assert not validate_experiment_folder_name('test_package', package_exist, '実験パッケージ名', button)
    assert button.button_type == 'warning'
    assert button.name == '実験パッケージ名:test_packageは既に存在しています。別名を入力してください。'


def test_validate_parameter_folder_name():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_validate_parameter_folder_name

    # チェックOK
    button = Button()
    assert validate_parameter_folder_name('test_parameter', 'test_package', button)

    # フォルダ名不正(パラメータ名空欄)
    button = Button()
    assert not validate_parameter_folder_name('', 'test_package', button)
    assert button.button_type == 'warning'
    assert button.name == 'パラメータ実験名が入力されていません。パラメータ実験名を入力し再度、ボタンをクリックしてください。'

    # パラメータ名とパッケージ名が同じ
    button = Button()
    assert not validate_parameter_folder_name('same_name', 'same_name', button)
    assert button.button_type == 'warning'
    assert button.name == '実験パッケージ名と同名のパラメータ実験名は作成できません。別名を入力してください。'

    # パラメータ名が「parameter」
    button = Button()
    assert not validate_parameter_folder_name('parameter', 'test_package', button)
    assert button.button_type == 'warning'
    assert button.name == 'パラメータ実験名として「parameter」は指定できません。別名を入力してください。'


def test_validate_select_default():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_validate_select_default

    button = Button()
    assert validate_select_default('selected_value', 'test_message', button)

    button = Button()
    assert not validate_select_default('--', 'test_message', button)
    assert button.button_type == 'warning'
    assert button.name == 'test_message'


def test_validate_commit_message():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_validate_commit_message

    # 文字数0
    message = ''
    assert validate_commit_message(message) == '作業のログメッセージが入力されていません。入力後、再度クリックしてください。'
    # 文字数1
    message = 'a'
    assert validate_commit_message(message) == ''
    # 文字数100
    message = ''.join(['a' for i in range(100)])
    assert len(message) == 100
    assert validate_commit_message(message) == ''
    # 文字数101
    message = ''.join(['a' for i in range(101)])
    assert len(message) == 101
    assert validate_commit_message(message) == '作業ログメッセージは100文字以内で入力してください。修正後、再度クリックしてください。'


def test_setup_local(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_setup_local

    token_setter = mocker.patch('nb_libs.utils.params.token.set_ginfork_token')
    user_info_setter = mocker.patch('nb_libs.utils.params.user_info.set_user_info')
    mocker.patch('nb_libs.utils.common.common.exec_subprocess')

    token_get = MockResponse(200, json=[{'sha1': 'test_token_get'}])
    token_get_no_token = MockResponse(200, json=[])
    token_create = MockResponse(201, json={'sha1': 'test_token_create'})
    user_info = MockResponse(200, json={'id': 'test_user_id', 'username': 'test_name', 'email': 'test@mail'})

    # 正常ケース(トークン作成済み)
    mocker.patch('nb_libs.utils.gin.api.get_token_for_auth', return_value=token_get)
    mocker.patch('nb_libs.utils.gin.api.create_token_for_auth', side_effect=UnitTestError())
    mocker.patch('nb_libs.utils.gin.api.get_user_info', return_value=user_info)
    setup_local('user_name', 'password')
    token_setter.assert_called_with('test_token_get')
    user_info_setter.assert_called_with(user_id='test_user_id')

    # 正常ケース(トークン未作成)
    mocker.patch('nb_libs.utils.gin.api.get_token_for_auth', return_value=token_get_no_token)
    mocker.patch('nb_libs.utils.gin.api.create_token_for_auth', return_value=token_create)
    mocker.patch('nb_libs.utils.gin.api.get_user_info', return_value=user_info)
    setup_local('user_name', 'password')
    token_setter.assert_called_with('test_token_create')
    user_info_setter.assert_called_with(user_id='test_user_id')

    # 認証失敗
    res401 = MockResponse(401)
    mocker.patch('nb_libs.utils.gin.api.get_token_for_auth', return_value=res401)
    with pytest.raises(Unauthorized):
        setup_local('user_name', 'password')


def test_initial_gin_user_auth():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_initial_gin_user_auth

    # エラーが発生しなければOK
    initial_gin_user_auth()


def test_create_user_auth_forms():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_create_user_auth_forms

    pn.extension()
    assert create_user_auth_forms()


def test_create_param_form():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_create_param_form

    pn.extension()
    assert create_param_form()


def test_create_select():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_create_select

    pn.extension()
    assert create_select('test_name', ['test_option1', 'test_option2'])


def test_create_button():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_create_button

    pn.extension()
    assert create_button('test_name')


def test_layout_error_text():
    # pytest -v -s tests/unit_tests/nb_libs/utils/form/test_prepare.py::test_layout_error_text

    pn.extension()
    assert layout_error_text()
