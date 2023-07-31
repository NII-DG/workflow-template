import requests
from ..utils.gin import sync
from ..utils.except_class import RepositoryNotExist, UrlUpdateError
from ..utils.message import display as msg_display, message


def launch_ex_env():
    # Up-to-date repository information in containers
    try:
        is_praivate = sync.update_repo_url()
    except requests.exceptions.RequestException as e:
        # Poor connection to GIN-fork
        err_msg_with_reason = message.get('launch', 'fail_update_repo_info')
        reason = message.get('DEFAULT', 'fail_connnection_for_gin')
        msg_display.display_err(err_msg_with_reason.format(reason))
        msg_display.display_log(msg=str(e))
        return
    except RepositoryNotExist as e:
        # Repository unidentifiable
        pass
    except UrlUpdateError as e:
        # Unexpected errors
        pass

    # Check whether the repository is private or public.
    is_praivate = True

    if is_praivate:
        # It's private.
        ## Create launchURL for private repository.
        ### Obtain a GIN-fork token.
        ### Obtain a token for construction from GIN-fork.
        ### User information is obtained from GIN-fork.
        ### Create launchURL for private repository.

        pass
    else:
        # It's public.

        ## Create launchURL for public repository.
        pass

    # Display the Create Experiment Run Environment button.
