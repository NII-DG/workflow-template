from urllib import parse
import requests
from http import HTTPStatus
import traceback
import re
import os

import panel as pn
from IPython.display import clear_output, display

from ..common import common
from ..params import user_info, token, param_json
from ..gin import api as gin_api
from ..message import message as m
from ..path import path as p
from ..except_class import Unauthorized


def submit_user_auth_callback(user_auth_forms, error_message, submit_button_user_auth):
    """Processing method after click on submit button

    Check form values, authenticate users, and update RF configuration files.

    Args:
        user_auth_forms ([list(TextInput or PasswordInput)]) : [form instance]
        error_message ([StaticText]) : [exception messages instance]
        submit_button_user_auth ([Button]): [Submit button instance]
    """
    def callback(event):
        user_name = user_auth_forms[0].value
        password = user_auth_forms[1].value
        # validate value
        if not validate_user_auth(user_name, password, submit_button_user_auth):
            return

        # If the entered value passes validation, a request for user authentication to GIN-fork is sent.
        # GIN API Basic Authentication
        # refs: https://docs.python-requests.org/en/master/user/authentication/
        try:
            setup_local(user_name, password)

        except Unauthorized:
            submit_button_user_auth.button_type = 'warning'
            submit_button_user_auth.name = m.get('user_auth','unauthorized')
            return
        except requests.exceptions.RequestException as e:
            submit_button_user_auth.button_type = 'warning'
            submit_button_user_auth.name = m.get('user_auth','connection_error')
            error_message.value = 'ERROR : {}'.format(traceback.format_exception_only(type(e), e)[0].rstrip('\\n'))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        except Exception as e:
            submit_button_user_auth.button_type = 'danger'
            submit_button_user_auth.name = m.get('user_auth','unexpected')
            error_message.value = 'ERROR : {}'.format(traceback.format_exception_only(type(e), e)[0].rstrip('\\n'))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        else:
            submit_button_user_auth.button_type = 'success'
            submit_button_user_auth.name = m.get('user_auth','success')
            return
    return callback


def validate_format_username(user_name):
    """GIN-fork username format check

    Args:
        user_name ([str]): [GIN-fork username]

    Returns:
        [Match[str] | None]: [Returns None if format does not match]
    """
    validation = re.compile(r'^[a-zA-Z0-9\-_.]+$')
    return validation.fullmatch(user_name)


def validate_format_input(input_text):
    """文字制限（50文字以内, 半角英数字, および"-", "_", "."のみ）"""
    validation = re.compile(r'^[a-zA-Z0-9\-_.]{1,50}$')
    return validation.fullmatch(input_text)


def validate_user_auth(user_name, password, submit_button_user_auth):
    ## user name
    if len(user_name) <= 0:
        submit_button_user_auth.button_type = 'warning'
        submit_button_user_auth.name = m.get('user_auth','username_empty_error')
        return False

    if not validate_format_username(user_name):
        submit_button_user_auth.button_type = 'warning'
        submit_button_user_auth.name = m.get('user_auth','username_pattern_error')
        return False

    ## password
    if len(password) <= 0:
        submit_button_user_auth.button_type = 'warning'
        submit_button_user_auth.name = m.get('user_auth','password_empty_error')
        return False

    return True


def validate_experiment_folder_name(name:str, path:str, title:str, submit_button)->bool:
    """format check for folder title

    Args:
        name (str): Folder name entered
        path (str): path of the folder
        title (str): Name to be displayed in error statements
        submit_button: pn.widgets.Button()

    Returns:
        bool: Whether the format is correct
    """

    if len(name) <= 0:
        submit_button.button_type = 'warning'
        submit_button.name = m.get('setup_package','empty_error').format(title)
        return False

    if not validate_format_input(name):
        submit_button.button_type = 'warning'
        submit_button.name = m.get('setup_package','pattern_error').format(title)
        return False

    if os.path.exists(path):
        submit_button.button_type = 'warning'
        submit_button.name = m.get('setup_package','already_exist_error').format(title, name)
        return False

    return True


def validate_parameter_folder_name(name, pkg_name, submit_button)->bool:

    if not validate_experiment_folder_name(name,
                    p.create_experiments_with_subpath(pkg_name, name),
                    m.get('setup_package','paramfolder_title'), submit_button):
        return False

    if name == pkg_name:
        submit_button.button_type = 'warning'
        submit_button.name = m.get('setup_package','paramfolder_same_pkg_error')
        return False
    elif name == 'parameter':
        submit_button.button_type = 'warning'
        submit_button.name = m.get('setup_package','paramfolder_prohibited_error')
        return False

    return True


def validate_select_default(select_value, error_message, submit_button)->bool:
    """デフォルトの値は選択できない"""
    if select_value == SELECT_DEFAULT_VALUE:
        submit_button.button_type = 'warning'
        submit_button.name = error_message
        return False
    else:
        return True


def setup_local(user_name, password):
    params = param_json.get_params()
    pr = parse.urlparse(params['siblings']['ginHttp'])
    response = gin_api.get_token_for_auth(pr.scheme, pr.netloc, user_name, password)

    ## Unauthorized
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise Unauthorized
    response.raise_for_status()

    ## Check to see if there is an existing token
    access_token = dict()
    tokens = response.json()
    if len(tokens) >= 1:
        access_token = response.json()[-1]
    elif len(tokens) < 1:
        response = gin_api.create_token_for_auth(pr.scheme, pr.netloc, user_name, password)
        if response.status_code == HTTPStatus.CREATED:
            access_token = response.json()
        response.raise_for_status()

    # Write out the GIN-fork access token
    token.set_ginfork_token(access_token['sha1'])

    # Get user info
    response = gin_api.get_user_info(pr.scheme, pr.netloc, access_token['sha1'])
    response.raise_for_status()

    # Set user info
    res_data = response.json()
    user_info.set_user_info(user_id=res_data['id'])
    common.exec_subprocess(cmd='git config --global user.name {}'.format(res_data['username']))
    common.exec_subprocess(cmd='git config --global user.email {}'.format(res_data['email']))


def initial_gin_user_auth():
    pn.extension()

    # form of user name and password
    user_auth_forms = create_user_auth_forms()

    # Instance for exception messages
    error_message = layout_error_text()

    button = create_button(name= m.get('user_auth','end_input'))

    # Define processing after clicking the submit button
    button.on_click(submit_user_auth_callback(user_auth_forms, error_message, button))

    clear_output()
    # Columnを利用すると値を取れない場合がある
    for form in user_auth_forms:
        display(form)
    display(button)
    display(error_message)


DEFAULT_WIDTH = 600
SELECT_DEFAULT_VALUE = '--'


def create_user_auth_forms():
    # user name form
    user_name_form = pn.widgets.TextInput(name=m.get('user_auth','username_title'), placeholder=m.get('user_auth','username_help'), width=DEFAULT_WIDTH)
    # password form
    password_form = pn.widgets.PasswordInput(name=m.get('user_auth','password_title'), placeholder=m.get('user_auth','password_help'), width=DEFAULT_WIDTH)
    return [user_name_form, password_form]


def create_param_form():
    return pn.widgets.TextInput(name=m.get('setup_package','paramfolder_title'), placeholder=m.get('setup_package','paramfolder_help'), width=DEFAULT_WIDTH)


def create_select(name:str, options:list[str]):
    options = [SELECT_DEFAULT_VALUE] + options
    return pn.widgets.Select(name=name, options=options, width=DEFAULT_WIDTH, value=SELECT_DEFAULT_VALUE)


def create_button(name):
    return pn.widgets.Button(name=name, button_type= "primary", width=DEFAULT_WIDTH)


def layout_error_text():
    return pn.widgets.StaticText(value='', style={'color': 'red'}, sizing_mode='stretch_width')
