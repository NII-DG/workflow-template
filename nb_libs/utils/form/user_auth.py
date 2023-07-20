import json
import os
from IPython.display import clear_output, display
from urllib import parse
import requests
from http import HTTPStatus
import panel as pn
import urllib
import re
from ..common import common
from ..params import user_info
from ..gin import api as gin_api
from ..gin import sync
import ..message as mess


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
        mail_addres = user_auth_forms[2].value
        # validate value
        ## user name
        if len(user_name) <= 0:
            submit_button_user_auth.button_type = 'warning'
            submit_button_user_auth.name = mess.get('user_auth','username_empty_error')
            return

        if not validate_format_username(user_name):
            submit_button_user_auth.button_type = 'warning'
            submit_button_user_auth.name = mess.get('user_auth','username_pattern_error')
            return

        ## password
        if len(password) <= 0:
            submit_button_user_auth.button_type = 'warning'
            submit_button_user_auth.name = mess.get('user_auth','password_empty_error')
            return

        ## mail addres
        if  len(mail_addres) <= 0:
            submit_button_user_auth.button_type = 'warning'
            submit_button_user_auth.name = mess.get('user_auth','mailaddress_empty_error')
            return

        if not validate_format_mail_address(mail_addres):
            submit_button_user_auth.button_type = 'warning'
            submit_button_user_auth.name = mess.get('user_auth','mailaddress_pattern_error')
            return

        # If the entered value passes validation, a request for user authentication to GIN-fork is sent.
        # GIN API Basic Authentication
        # refs: https://docs.python-requests.org/en/master/user/authentication/
        try:
            params = {}
            with open(sync.fetch_param_file_path(), mode='r') as f:
                params = json.load(f)

            baseURL = params['siblings']['ginHttp'] + '/api/v1/users/'
            response = requests.get(baseURL + user_name + '/tokens', auth=(user_name, password))

            ## Unauthorized
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                submit_button_user_auth.button_type = 'warning'
                submit_button_user_auth.name = mess.get('user_auth','unauthorized')
                return

            user_info.set_user_info(user_name)

            ## Check to see if there is an existing token
            access_token = dict()
            tokens = response.json()
            if len(tokens) >= 1:
                access_token = response.json()[-1]
            elif len(tokens) < 1:
                response = requests.post(baseURL + user_name + '/tokens', data={"name": "system-generated"}, auth=(user_name, password))
                if response.status_code == HTTPStatus.CREATED:
                    access_token = response.json()

        # Write out the GIN-fork access token to /home/jovyan/.token.json.

            token_dict = {"ginfork_token": access_token['sha1']}
            with open('/home/jovyan/.token.json', 'w') as f:
                json.dump(token_dict, f, indent=4)

            os.chdir(os.environ['HOME'])
            common.exec_subprocess(cmd='git config --global user.name {}'.format(user_name))
            common.exec_subprocess(cmd='git config --global user.email {}'.format(mail_addres))
        except Exception as e:
            submit_button_user_auth.button_type = 'danger'
            submit_button_user_auth.name = mess.get('user_auth','exception')
            error_message.value = 'ERROR : {}'.format(str(e))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        else:
            submit_button_user_auth.button_type = 'success'
            submit_button_user_auth.name = mess.get('user_auth','success')
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

def validate_format_mail_address(mail_addres):
    """mail address format check

    Args:
        mail_address ([str]): [mail address]

    Returns:
        [Match[str] | None]: [Returns None if format does not match]
    """
    validation =     re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return validation.fullmatch(mail_addres)

def initial_gin_user_auth():
    pn.extension()
    # user name form
    user_name_form = pn.widgets.TextInput(name=mess.get('user_auth','username_title'), placeholder=mess.get('user_auth','username_help'), width=700)
    # password form
    password_form = pn.widgets.PasswordInput(name=mess.get('user_auth','password_title'), placeholder=mess.get('user_auth','password_help'), width=700)
    # email address form
    mail_address_form = pn.widgets.TextInput(name=mess.get('user_auth','emailaddress_title'), placeholder=mess.get('user_auth','emailaddress_help'), width=700)
    user_auth_forms = [user_name_form, password_form, mail_address_form]

    # Instance for exception messages
    error_message = pn.widgets.StaticText(value='', style={'color': 'red'}, sizing_mode='stretch_width')

    button = pn.widgets.Button(name= mess.get('button','entry'), button_type= "primary", width=700)


    # Define processing after clicking the submit button
    button.on_click(submit_user_auth_callback(user_auth_forms, error_message, button))

    clear_output()
    for form in user_auth_forms:
        display(form)
    display(button)
    display(error_message)

def submit_user_auth_callback_without_email(user_auth_forms, error_message, submit_button_user_auth, success_private_button):
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
        ## user name
        if len(user_name) <= 0:
            submit_button_user_auth.button_type = 'warning'
            submit_button_user_auth.name = mess.get('user_auth','username_empty_error')
            return

        if not validate_format_username(user_name):
            submit_button_user_auth.button_type = 'warning'
            submit_button_user_auth.name = mess.get('user_auth','username_pattern_error')
            return

        ## password
        if len(password) <= 0:
            submit_button_user_auth.button_type = 'warning'
            submit_button_user_auth.name = mess.get('user_auth','password_empty_error')
            return

        # If the entered value passes validation, a request for user authentication to GIN-fork is sent.
        # GIN API Basic Authentication
        # refs: https://docs.python-requests.org/en/master/user/authentication/
        try:
            params = {}
            with open(sync.fetch_param_file_path(), mode='r') as f:
                params = json.load(f)

            baseURL = params['siblings']['ginHttp'] + '/api/v1/users/'
            response = requests.get(baseURL + user_name + '/tokens', auth=(user_name, password))

            ## Unauthorized
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                submit_button_user_auth.button_type = 'warning'
                submit_button_user_auth.name = mess.get('user_auth','unauthorized')
                return

            user_info.set_user_info(user_name)

            ## Check to see if there is an existing token
            access_token = dict()
            tokens = response.json()
            if len(tokens) >= 1:
                access_token = response.json()[-1]
            elif len(tokens) < 1:
                response = requests.post(baseURL + user_name + '/tokens', data={"name": "system-generated"}, auth=(user_name, password))
                if response.status_code == HTTPStatus.CREATED:
                    access_token = response.json()

        # Write out the GIN-fork access token to /home/jovyan/.token.json.

            token_dict = {"ginfork_token": access_token['sha1']}
            with open('/home/jovyan/.token.json', 'w') as f:
                json.dump(token_dict, f, indent=4)

            os.chdir(os.environ['HOME'])
            common.exec_subprocess(cmd='git config --global user.name {}'.format(user_name))

            pr = parse.urlparse(params['siblings']['ginHttp'])
            # get building token
            launch_token_res = gin_api.create_token_for_launch(scheme=pr.scheme, domain=pr.netloc, token=access_token['sha1'])
            launch_token = ''
            if launch_token_res.status_code == HTTPStatus.CREATED:
                launch_token_response_data = launch_token_res.json()
                launch_token = launch_token_response_data['sha1']
            else:
                err_msg = 'Fail to create buildling token from GIN-fork API. status_code : {}'.format(launch_token_res.status_code)
                raise Exception(err_msg)

        except Exception as e:
            submit_button_user_auth.button_type = 'danger'
            submit_button_user_auth.name = mess.get('user_auth','exception')
            error_message.value = 'ERROR : {}'.format(str(e))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        else:
            submit_button_user_auth.button_type = 'success'
            submit_button_user_auth.name = mess.get('build_container', 'new_experimnet')
            error_message.object = pn.pane.HTML(error_message.value)

            remote_http_url = common.exec_subprocess(cmd='git config --get remote.origin.url')[0].decode()[:-1]
            pos = remote_http_url.find("://")
            remote_http_url = f"{remote_http_url[:pos+3]}{user_name}:{launch_token}@{remote_http_url[pos+3:]}"
            url = "https://binder.cs.rcos.nii.ac.jp/v2/git/" + urllib.parse.quote(remote_http_url, safe='') + "/HEAD?filepath=WORKFLOWS/experiment.ipynb"
            success_private_button.value = f'<button onclick="window.open(\'{url}\')">'+ mess.get('build_container', 'build_button') +'</button>'
            success_private_button.object = pn.pane.HTML(success_private_button.value)
            return
    return callback

def initial_gin_user_auth_without_email():
    pn.extension()

    # user name form
    user_name_form = pn.widgets.TextInput(name=mess.get('user_auth','username_title'), placeholder= mess.get('user_auth','username_help'), width=700)
    # password form
    password_form = pn.widgets.PasswordInput(name=mess.get('user_auth','password_title'), placeholder=mess.get('user_auth','password_help'), width=700)
    user_auth_forms = [user_name_form, password_form]

    # Instance for exception messages
    error_message = pn.widgets.StaticText(value='', style={'color': 'red'}, sizing_mode='stretch_width')

    button = pn.widgets.Button(name= mess.get('button','entry'), button_type= "primary", width=700)
    succecc_private_button = pn.widgets.StaticText(value='', sizing_mode='stretch_width')

    # Define processing after clicking the submit button
    button.on_click(submit_user_auth_callback_without_email(user_auth_forms, error_message, button, succecc_private_button))

    clear_output()
    for form in user_auth_forms:
        display(form)
    display(button)
    display(error_message)
    display(succecc_private_button)