import requests
from ..utils.message import message, display
from ..utils.params import token
from ..utils.git import git_module
from ..utils.flow import module as flow

def del_build_token():
    """不要なGIN-forkトークンの削除"""

    url = git_module.get_remote_url()

    try:
        # delete build token(only private)
        token.del_build_token_by_remote_origin_url(url)
    except requests.exceptions.RequestException:
        display.display_err(message.get('build_token', 'connection_error'))
        raise
    except Exception:
        raise


def finished_setup():
    flow.put_mark('research', 'base_required_every_time', '済')


def syncs_config() -> tuple[list[str], str]:
    git_path = ['/home/jovyan/.gitignore', '/home/jovyan/WORKFLOWS', '/home/jovyan/maDMP.ipynb']
    commit_message = '[GIN] 研究リポジトリ初期セットアップを完了'
    return git_path, commit_message