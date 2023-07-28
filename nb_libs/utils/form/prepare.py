import json
import os
from IPython.display import clear_output, display
from urllib import parse
import requests
from http import HTTPStatus
import traceback
import panel as pn
import urllib
import re
from ..common import common
from ..params import user_info, token, param_json
from ..gin import api as gin_api
from ..gin import sync
from ..git import git_module as git
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


def validate_format_username(user_name):
    """GIN-fork username format check

    Args:
        user_name ([str]): [GIN-fork username]

    Returns:
        [Match[str] | None]: [Returns None if format does not match]
    """
    validation = re.compile(r'^[a-zA-Z0-9\-_.]+$')
    return validation.fullmatch(user_name)


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

    button = pn.widgets.Button(name= m.get('user_auth','end_input'), button_type= "primary", width=700)

    # Define processing after clicking the submit button
    button.on_click(submit_user_auth_callback(user_auth_forms, error_message, button))

    clear_output()
    for form in user_auth_forms:
        display(form)
    display(button)
    display(error_message)


def create_user_auth_forms():
    # user name form
    user_name_form = pn.widgets.TextInput(name=m.get('user_auth','username_title'), placeholder=m.get('user_auth','username_help'), width=700)
    # password form
    password_form = pn.widgets.PasswordInput(name=m.get('user_auth','password_title'), placeholder=m.get('user_auth','password_help'), width=700)
    return [user_name_form, password_form]


def layout_error_text():
    return pn.widgets.StaticText(value='', style={'color': 'red'}, sizing_mode='stretch_width')


def submit_build_for_private_callback(user_auth_forms, error_message, submit_button_user_auth, success_private_button):
    """Processing method after click on submit button

    Check form values, authenticate users, and update RF configuration files.

    Args:
        user_auth_forms ([list(TextInput or PasswordInput)]) : [form instance]
        error_message ([StaticText]) : [exception messages instance]
        submit_button_user_auth ([Button]): [Submit button instance]
        success_private_button ([StaticText]) : [launch binder button]
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
            params = param_json.get_params()
            pr = parse.urlparse(params['siblings']['ginHttp'])
            response = gin_api.get_token_for_auth(pr.scheme, pr.netloc, user_name, password)

            ## Unauthorized
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise Unauthorized
            response.raise_for_status()

            # get building token
            launch_token_res = gin_api.create_token_for_launch(scheme=pr.scheme, domain=pr.netloc, token=token.get_ginfork_token())
            launch_token = ''
            if launch_token_res.status_code == HTTPStatus.CREATED:
                launch_token_response_data = launch_token_res.json()
                launch_token = launch_token_response_data['sha1']
            else:
                err_msg = 'Fail to create buildling token from GIN-fork API. status_code : {}'.format(launch_token_res.status_code)
                raise Exception(err_msg)

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
            submit_button_user_auth.name = m.get('build_container', 'new_experimnet')
            error_message.object = pn.pane.HTML(error_message.value)

            remote_http_url = git.get_remote_url()
            pos = remote_http_url.find("://")
            remote_http_url = f"{remote_http_url[:pos+3]}{user_name}:{launch_token}@{remote_http_url[pos+3:]}"
            url = "https://binder.cs.rcos.nii.ac.jp/v2/git/" + urllib.parse.quote(remote_http_url, safe='') + "/HEAD?filepath=WORKFLOWS/experiment.ipynb"
            success_private_button.value = f'<button onclick="window.open(\'{url}\')">'+ m.get('build_container', 'build_button') +'</button>'
            success_private_button.object = pn.pane.HTML(success_private_button.value)
            return
    return callback


def initial_build_for_private():
    pn.extension()

    # form of user name and password
    user_auth_forms = create_user_auth_forms()

    # Instance for exception messages
    error_message = layout_error_text()

    button = pn.widgets.Button(name= m.get('user_auth','end_input'), button_type= "primary", width=700)
    succecc_private_button = pn.widgets.StaticText(value='', sizing_mode='stretch_width')

    # Define processing after clicking the submit button
    button.on_click(submit_build_for_private_callback(user_auth_forms, error_message, button, succecc_private_button))

    clear_output()
    for form in user_auth_forms:
        display(form)
    display(button)
    display(error_message)
    display(succecc_private_button)



def submit_init_experiment_callback(input_forms, input_radios, error_message, submit_button):

    def callback(event):
        # form values
        user_name = input_forms[0].value
        password = input_forms[1].value
        package_name = input_forms[2].value
        paramfolder_name = None
        if len(input_forms) > 3:
            paramfolder_name = input_forms[4].value

        # validate value for forms
        if not validate_user_auth(user_name, password, submit_button):
            return


        if paramfolder_name is not None:
            pass




        if input_radios[0].value == m.get('setup_package','true'):
            is_test_folder = True
        else:
            is_test_folder = False

        if input_radios[1].value == m.get('setup_package','true'):
            is_test_folder = True
        else:
            is_test_folder = False







        try:
            setup_local(user_name, password)

        except Unauthorized:
            submit_button.button_type = 'warning'
            submit_button.name = m.get('user_auth','unauthorized')
            return
        except requests.exceptions.RequestException as e:
            submit_button.button_type = 'warning'
            submit_button.name = m.get('user_auth','connection_error')
            error_message.value = 'ERROR : {}'.format(traceback.format_exception_only(type(e), e)[0].rstrip('\\n'))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        except Exception as e:
            submit_button.button_type = 'danger'
            submit_button.name = m.get('user_auth','unexpected')
            error_message.value = 'ERROR : {}'.format(traceback.format_exception_only(type(e), e)[0].rstrip('\\n'))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        else:
            submit_button.button_type = 'success'
            submit_button.name = m.get('user_auth','success')
            return
        

    return callback


def initial_experiment():
    pn.extension()

    # form of user name and password
    input_forms = create_user_auth_forms()

    # form of experiment
    package_name_form = pn.widgets.TextInput(name=m.get('setup_package','package_name_title'), width=700)
    input_forms.append(package_name_form)

    assigned_values = sync.fetch_gin_monitoring_assigned_values()
    if assigned_values['datasetStructure'] == 'for_parameters':
        paramfolder_form = pn.widgets.TextInput(name=m.get('setup_package','paramfolder_name_title'), width=700)
        input_forms.append(paramfolder_form)

    options = [m.get('setup_package','true'), m.get('setup_package','false')]
    init_value = m.get('setup_package','false')
    test_folder_radio = pn.widgets.RadioBoxGroup(name=m.get('setup_package','test_folder_title'), options=options, inline=True, value=init_value)
    ci_folder_radio = pn.widgets.RadioBoxGroup(name=m.get('setup_package','ci_folder_title'), options=options, inline=True, value=init_value)
    input_radios = [test_folder_radio, ci_folder_radio]

    # Instance for exception messages
    error_message = layout_error_text()

    button = pn.widgets.Button(name= m.get('DEFAULT','end_input'), button_type= "primary", width=700)

    # Define processing after clicking the submit button
    button.on_click(submit_user_auth_callback(input_forms, input_radios,error_message, button))

    clear_output()
    display(pn.Column(*input_forms ,*input_radios, button, error_message))