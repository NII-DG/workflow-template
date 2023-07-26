"""GIN-frokの実行環境一覧への操作"""
import requests
import os
import json
from urllib import parse
from urllib.parse import urljoin
from ..message import message, display
from ..params import user_info, token
from ..path import path
from . import sync, api


def add_container(experiment_title=""):
    """register add container to GIN-fork container list.

    ARG
    ---------------
    experiment_title : str
        Description : a contaier is regarded as an experiment contaier if and only if experiment_title is set.

    RETURN
    ---------------
    Returns nothing.

    EXCEPTION
    ---------------
    """
    try:
        with open(os.environ['HOME'] + '/.repository_id', 'r') as f:
            repo_id = f.read()
        with open(sync.fetch_param_file_path(), mode='r') as f:
            params = json.load(f)

        pr = parse.urlparse(params['siblings']['ginHttp'])
        uid = str(user_info.get_user_id())
        user_token = token.get_ginfork_token()
        server_name = os.environ["JUPYTERHUB_SERVICE_PREFIX"].split('/')[3]
        url = params['rcosBinderUrl'] + os.environ["JUPYTERHUB_SERVICE_PREFIX"] + "notebooks"

        # experiment
        if len(experiment_title) > 0:
            url = urljoin(url, path.URL_EXP_PATH)
            response = api.add_container(scheme=pr.scheme, domain=pr.netloc, token=user_token, repo_id=repo_id, user_id=uid, server_name=server_name, ipynb_url=url, pkg_title=experiment_title)

        # research
        else:
            url = urljoin(url, path.URL_RES_PATH)
            response = api.add_container(scheme=pr.scheme, domain=pr.netloc, token=user_token, repo_id=repo_id, user_id=uid, server_name=server_name, ipynb_url=url)

        if response.status_code == requests.codes.ok:
            display.display_info(message.get('container_api', 'add_success'))
        elif response.json()["error"].startswith("Error 1062"):
            display.display_warm(message.get('container_api', 'add_already_exist'))
        else:
            raise Exception

    except requests.exceptions.RequestException as e:
        display.display_err(message.get('container_api', 'communication_error'))
        raise e
    except Exception:
        display.display_err(message.get('container_api', 'unexpected'))
        raise


def patch_container():
    """update only updated_unix of container

    ARG
    ---------------
    experiment_title : str
        Description : contaier is regarded as experiment contaier if and only if experiment_title is set.

    RETURN
    ---------------
    Returns nothing.

    EXCEPTION
    ---------------
    """
    try:
        with open(sync.fetch_param_file_path(), mode='r') as f:
            params = json.load(f)
        pr = parse.urlparse(params['siblings']['ginHttp'])
        user_token = token.get_ginfork_token()
        server_name = os.environ["JUPYTERHUB_SERVICE_PREFIX"].split('/')[3]
        uid = str(user_info.get_user_id())

        response = api.patch_container(pr.scheme, pr.netloc, user_token, server_name, uid)

        if response.status_code != requests.codes.ok:
            raise Exception

    except requests.exceptions.RequestException as e:
        display.display_err(message.get('container_api', 'communication_error'))
        raise e
    except Exception:
        display.display_err(message.get('container_api', 'unexpected'))
        raise


def delete_container():
    """logical delete of container

    ARG
    ---------------

    RETURN
    ---------------
    Returns nothing.

    EXCEPTION
    ---------------
    """

    try:
        with open(sync.fetch_param_file_path(), mode='r') as f:
                params = json.load(f)
        pr = parse.urlparse(params['siblings']['ginHttp'])
        user_token = token.get_ginfork_token()
        server_name = os.environ["JUPYTERHUB_SERVICE_PREFIX"].split('/')[3]
        uid = str(user_info.get_user_id())

        response = api.delete_container(pr.scheme, pr.netloc, user_token, server_name, uid)

        if response.status_code == requests.codes.ok:
            display.display_info(message.get('container_api', 'delete_success'))
        else:
            raise Exception

    except requests.exceptions.RequestException as e:
        display.display_err(message.get('container_api', 'communication_error'))
        raise e
    except Exception:
        display.display_err(message.get('container_api', 'unexpected'))
        raise