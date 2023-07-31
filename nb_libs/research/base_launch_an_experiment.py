from http import HTTPStatus
import requests
from ..utils.gin import sync
from ..utils.except_class import RepositoryNotExist, UrlUpdateError, NoValueInDgFileError, QueryError
from ..utils.message import display as msg_display, message
from ..utils.params import token, param_json
from ..utils.gin import api as gin_api
from ..utils.git import git_module
from ..utils.path import display as path_display, path
from IPython.display import display, HTML, clear_output
from urllib import parse
from ..utils.flow.module import check_finished_setup_research
# To remove the git config warning message on module import with execution result
clear_output()

LAUNCH_EX_URL = 'https://binder.cs.rcos.nii.ac.jp/v2/git/{}/master?filepath={}'

def launch_ex_env():
    """Generation and display of buttons for creating the experiment execution environment

    When creating an experimental execution environment for a private repository, obtain a token for building the environment and generate a URL for creating the environment.

    """
    is_finished = check_finished_setup_research()
    if not is_finished:
        err_msg = message.get('DEFAULT', 'not_finish_setup')
        msg_display.display_warm(err_msg)
        return

    # Up-to-date repository information in containers
    try:
        is_praivate = sync.update_repo_url()
    except NoValueInDgFileError as e:
        # Processing setup not complete
        err_msg_with_reason = message.get('launch', 'fail_update_repo_info')
        reason = message.get('ma_dmp', 'non_exec_ma_dmp')
        msg_display.display_err(err_msg_with_reason.format(reason))
        raise e
    except requests.exceptions.RequestException as e:
        # Poor connection to GIN-fork
        err_msg_with_reason = message.get('launch', 'fail_update_repo_info')
        reason = message.get('DEFAULT', 'fail_connnection_for_gin')
        msg_display.display_err(err_msg_with_reason.format(reason))
        msg_display.display_log(msg=str(e))
        raise e
    except RepositoryNotExist as e:
        # Repository unidentifiable
        err_msg_with_reason = message.get('launch', 'fail_update_repo_info')
        reason = message.get('gin', 'fail_search_repo')
        msg_display.display_err(err_msg_with_reason.format(reason))
        msg_display.display_log(msg=str(e))
        raise e
    except UrlUpdateError as e:
        # Unexpected errors
        err_msg = message.get('DEFAULT', 'unexpected')
        msg_display.display_err(err_msg)
        raise e


    # Get the repository URL from git config(remote.origin.url).
    repo_url = git_module.get_remote_url()

    # Check whether the repository is private or public.
    if is_praivate:
        # It's private.
        ## Create launchURL for private repository.
        ### Obtain a GIN-fork token.
        try:
            gin_token = token.get_ginfork_token()
        except (FileNotFoundError , KeyError) as e:
            # Processing setup not complete
            err_msg = message.get('DEFAULT', 'not_finish_setup')
            msg_display.display_warm(err_msg)
            return
        except Exception as e:
            # Unexpected errors
            err_msg = message.get('DEFAULT', 'unexpected')
            msg_display.display_err(err_msg)
            raise e

        ### Obtain a token for construction and user name from GIN-fork.
        try:
            launch_token, user_name = get_token_for_launch_and_username(gin_token=gin_token)
        except Exception as e:
            # Unexpected errors
            err_msg = message.get('DEFAULT', 'unexpected')
            msg_display.display_err(err_msg)
            raise e

        ### Create launchURL for private repository.
        pos = repo_url.find("://")
        repo_url_with_auth = f"{repo_url[:pos+3]}{user_name}:{launch_token}@{repo_url[pos+3:]}"
        launch_url = LAUNCH_EX_URL.format(parse.quote(repo_url_with_auth, safe=''), path.URL_EXP_PATH)
    else:
        # It's public.
        ## Create launchURL for public repository.
        launch_url = LAUNCH_EX_URL.format(parse.quote(repo_url,  safe=''), path.URL_EXP_PATH)

    # Display the Create Experiment Run Environment button.
    launch_button = get_launch_ex_botton_html(launch_url)
    display(HTML(launch_button))



def get_token_for_launch_and_username(gin_token):
    ## Error handling is not necessary when acquiring the URL for Gin-fork. Because it has been confirmed in the previous process
    gin_http_url = param_json.get_gin_http()
    pr = parse.urlparse(gin_http_url)
    response = gin_api.create_token_for_launch(scheme=pr.scheme, domain=pr.netloc, token=gin_token)

    launch_token = ''
    if response.status_code == HTTPStatus.CREATED:
        launch_token_response_data = response.json()
        launch_token = launch_token_response_data['sha1']
    else:
        err_msg = 'Fail to create buildling token from GIN-fork API. status_code : {}'.format(response.status_code)
        raise QueryError(err_msg)

    response = gin_api.get_user_info(scheme=pr.scheme, domain=pr.netloc,token=gin_token)
    response.raise_for_status()

    res_data_user_info = response.json()
    user_name =  res_data_user_info['username']
    return launch_token, user_name

def get_launch_ex_botton_html(link_url):
    return path_display.button_html(url=link_url, msg=message.get('launch', 'launch'), target='_blank', button_background_color='#21ba45')
