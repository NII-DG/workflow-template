import os
import requests
from ..utils.message import message, display
from ..utils.params import token, user_info
from ..utils.git import git_module
from ..utils.gin import sync, ssh, container
from ..utils.path import path
from ..utils.flow import module as flow
from ..utils.except_class import DidNotFinishError


def preparation_completed():
    if not (os.path.isfile(user_info.FILE_PATH) and os.path.isfile(token.FILE_PATH)):
        display.display_err(message.get('setup', 'not_entered'))
        raise DidNotFinishError


def del_build_token():
    """不要なGIN-forkトークンの削除"""
    preparation_completed()
    url = git_module.get_remote_url()

    try:
        # delete build token(only private)
        token.del_build_token_by_remote_origin_url(url)
    except requests.exceptions.RequestException:
        display.display_err(message.get('build_token', 'connection_error'))
        raise
    except Exception:
        raise


def datalad_create():
    """ローカルをdataladデータセット化する"""
    preparation_completed()
    sync.datalad_create(path.HOME_PATH)


def ssh_create_key():
    """SSH keyの作成"""
    preparation_completed()
    ssh.create_key()


def upload_ssh_key():
    """GIN-frokへ公開鍵の登録"""
    preparation_completed()
    ssh.upload_ssh_key()


def ssh_trust_gin():
    preparation_completed()
    ssh.trust_gin()


def prepare_sync():
    preparation_completed()
    sync.prepare_sync()


def setup_sibling():
    """siblingを設定する

    Note:
        git-annexブランチのpushはリポジトリ名の変更時に正常動作するために必要
        リモートにgit-annexブランチが無い場合、リポジトリ名が変更されるとpushできない
    """
    preparation_completed()
    sync.push_annex_branch()


def add_container():
    preparation_completed()
    container.add_container()


def finished_setup():
    preparation_completed()
    flow.put_mark('research', 'base_required_every_time', '済')


def syncs_config() -> tuple[list[str], str]:
    preparation_completed()
    git_path = ['/home/jovyan/.gitignore', '/home/jovyan/WORKFLOWS', '/home/jovyan/maDMP.ipynb']
    commit_message = '[GIN] 研究リポジトリ初期セットアップを完了'
    return git_path, commit_message