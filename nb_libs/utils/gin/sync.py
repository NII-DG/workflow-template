import os
import requests
import traceback
import subprocess
from subprocess import PIPE
import hashlib
import datetime
from urllib import parse

import magic
from datalad import api
from IPython.display import clear_output

from ..git import git_module
from ..common import common
from ..message import message as msg_mod, display as msg_display
from ..path import path as p
from ..params import token, user_info, param_json, repository_id
from . import api as gin_api
from . import container
from ..except_class import RepositoryNotExist, UrlUpdateError, NoValueInDgFileError


SIBLING = 'gin'


def update_repo_url():
    """HTTPとSSHのリモートURLを最新化する

    Returns:
        bool: プライベートリポジトリかどうか

    Raises:
        requests.exceptions.RequestException: 接続の確立不良
        RepositoryNotExist: リモートリポジトリの情報が取得できない
        UrlUpdateError: 想定外のエラーにより最新化に失敗した
    """

    try:
        # APIリクエストに必要な情報を取得する
        gin_http_url = param_json.get_gin_http()
        pr = parse.urlparse(gin_http_url)
        repo_id = repository_id.get_repo_id()

        # APIからリポジトリの最新のSSHのリモートURLを取得し、リモート設定を更新する
        res = gin_api.search_public_repo(pr.scheme, pr.netloc, repo_id)
        res_data = res.json()
        if len(res_data['data']) == 0:
            # 初期設定前の場合は取れない
            ginfork_token = token.get_ginfork_token()
            uid = str(user_info.get_user_id())
            res = gin_api.search_repo(pr.scheme, pr.netloc, repo_id, uid, ginfork_token)
            res_data = res.json()

        res.raise_for_status()
        if len(res_data['data']) == 0:
            raise RepositoryNotExist

        ssh_url = res_data['data'][0]['ssh_url']
        http_url = res_data['data'][0]['html_url'] + '.git'
        update_list = [[SIBLING, ssh_url],['origin', http_url]]
        for update_target in update_list:
            result = subprocess.run('git remote set-url ' + update_target[0] + ' ' + update_target[1], shell=True, stdout=PIPE, stderr=PIPE, text=True)
            if 'No such remote' in result.stderr:
                subprocess.run('git remote add ' + update_target[0] + ' ' + update_target[1], shell=True)

    except requests.exceptions.RequestException:
        raise
    except RepositoryNotExist:
        raise
    except NoValueInDgFileError:
        raise
    except Exception as e:
        raise UrlUpdateError from e

    is_private = res_data['data'][0]['private']
    return is_private


def datalad_create(dir_path:str):
    """dataladのデータセット化する

    Args:
        path (str): データセット化するディレクトリのパス
    """
    if not os.path.isdir(os.path.join(dir_path, ".datalad")):
        api.create(path=dir_path, force=True)
        clear_output()
        msg_display.display_info(msg_mod.get('setup_sync', 'datalad_create_success'))
    else:
        clear_output()
        msg_display.display_warm(msg_mod.get('setup_sync', 'datalad_create_already'))


def datalad_get(dir_path:str):
    """datalad getをする

    Args:
        path (str): datalad getするパス
    """
    api.get(path=dir_path)
    api.unlock(path=dir_path)


def prepare_sync():
    """同期するコンテンツの調整"""

    # S3にあるデータをGIN-forkに同期しないための設定
    git_module.git_annex_untrust()
    git_module.git_annex_trust()

    # 元ファイルからコピーして.gitignoreを作成
    file_path = os.path.join(p.HOME_PATH, '.gitignore')
    orig_file_path = os.path.join(p.DATA_PATH, 'orig_gitignore')
    if not os.path.isfile(file_path):
        common.cp_file(orig_file_path, file_path)


def setup_sibling():
    """siblingの登録"""

    try:
        ginfork_token = token.get_ginfork_token()
        repo_id = repository_id.get_repo_id()
        user_id = user_info.get_user_id()
        params = param_json.get_params()
        pr = parse.urlparse(params['siblings']['ginHttp'])
        response = gin_api.search_repo(pr.scheme, pr.netloc, repo_id, user_id, ginfork_token)
        response.raise_for_status() # ステータスコードが200番台でない場合はraise HTTPError
        res_data = response.json()
        if len(res_data['data']) == 0:
                raise RepositoryNotExist
        ssh_url = res_data['data'][0]['ssh_url']
        http_url = res_data['data'][0]['html_url'] + '.git'
        # Note:
        #   action='add'では既に存在する場合にIncompleteResultsErrorになる
        #   action='config'では無ければ追加、あれば上書き
        #   refs: https://docs.datalad.org/en/stable/generated/datalad.api.siblings.html
        api.siblings(action='configure', name='origin', url=http_url)
        api.siblings(action='configure', name=SIBLING, url=ssh_url)
    except Exception:
        raise
    else:
        clear_output()


def push_annex_branch():
    """git-annexブランチをpushする"""
    common.exec_subprocess(cmd=f'git push {SIBLING} git-annex:git-annex')


def syncs_with_repo(git_path:list[str], gitannex_path:list[str], gitannex_files :list[str], message:str, get_paths:list[str]):
    """synchronize with the repository

    ARG
    ---------------
    git_path : str or list(str)
        Description : Define directories and files to be managed by git.
    gitannex_path : str or list(str)
        Description : Define directories and files to be managed by git-annex.
    gitannex_files : str or list(str) or None
        Description : Specify the file to which metadata(content_size, sha256, mime_type) is to be added. Specify None if metadata is not to be added.
    message : str
        Description : Commit message

    RETURN
    ---------------
    bool
        Description : 同期の成功判定

    memo:
        update()を最初にするとgit annex lockができない。addをする必要がある。
    """

    success_message = ''
    warm_message = ''
    error_message = ''
    datalad_error = ''
    try:

        os.chdir(p.HOME_PATH)
        print('[INFO] Lock git-annex content')
        os.system('git annex lock')
        print('[INFO] Save git-annex content and Register metadata')
        save_annex_and_register_metadata(gitannex_path, gitannex_files, message)
        print('[INFO] Uulock git-annex content')
        os.system('git annex unlock')
        print('[INFO] Save git content')
        save_git(git_path, message)
        print('[INFO] Lock git-annex content')
        os.system('git annex lock')
        print('[INFO] Update and Merge Repository')
        update()
        if len(get_paths)>0:
            api.get(path=get_paths)
    except:
        datalad_error = traceback.format_exc()
        # if there is a connection error to the remote, try recovery
        if 'Repository does not exist' in datalad_error or 'failed with exitcode 128' in datalad_error:
            try:
                # update URLs of remote repositories
                update_repo_url()
                print('[INFO] Update repository URL')
                warm_message = msg_mod.get('sync', 'resync_repo_rename')
            except RepositoryNotExist:
                # repository may not exist
                error_message = msg_mod.get('sync', 'connect_repo_error')
            except requests.exceptions.RequestException:
                error_message = msg_mod.get('sync', 'connection_error')
            except UrlUpdateError:
                error_message = msg_mod.get('sync', 'unexpected')
        elif 'files would be overwritten by merge:' in datalad_error:
            print('[INFO] Files would be overwritten by merge')
            git_commit_msg = '{}(auto adjustment)'.format(message)
            err_key_info = extract_info_from_datalad_update_err(datalad_error)
            file_paths = list[str]()
            os.chdir(p.HOME_PATH)
            os.system('git annex lock')
            if 'The following untracked working tree' in err_key_info:
                file_paths = common.get_filepaths_from_dalalad_error(err_key_info)
                adjust_add_git_paths = list[str]()
                adjust_add_annex_paths = list[str]()
                for path in file_paths:
                    if '\\u3000' in path:
                        path = path.replace('\\u3000', '　')
                    if common.is_should_annex_content_path(path):
                        if not path.startswith(p.HOME_PATH):
                            path = os.path.join(p.HOME_PATH, path)
                        adjust_add_annex_paths.append(path)
                    else:
                        if not path.startswith(p.HOME_PATH):
                             path = os.path.join(p.HOME_PATH, path)
                        adjust_add_git_paths.append(path)
                print('[INFO] git add. path : {}'.format(adjust_add_git_paths))
                print('[INFO] git annex add. path : {}'.format(adjust_add_annex_paths))
                print('[INFO] Save git-annex content and Register metadata(auto adjustment)')
                save_annex_and_register_metadata(adjust_add_annex_paths, adjust_add_annex_paths, git_commit_msg)
                os.system('git annex unlock')
                print('[INFO] Save git content(auto adjustment)')
                save_git(adjust_add_git_paths, message)
            elif 'Your local changes to the following' in err_key_info:
                if 'Please commit your changes or stash them before you merge' in err_key_info:
                    file_paths = common.get_filepaths_from_dalalad_error(err_key_info)
                    adjust_add_git_paths = list[str]()
                    adjust_add_annex_paths = list[str]()
                    for path in file_paths:
                        if '\\u3000' in path:
                            path = path.replace('\\u3000', '　')
                        if common.is_should_annex_content_path(path):
                            if not path.startswith(p.HOME_PATH):
                                path = os.path.join(p.HOME_PATH, path)
                            adjust_add_annex_paths.append(path)
                        else:
                            if not path.startswith(p.HOME_PATH):
                                path = os.path.join(p.HOME_PATH, path)
                            adjust_add_git_paths.append(path)
                    print('[INFO] git add. path : {}'.format(adjust_add_git_paths))
                    print('[INFO] git annex add. path : {}'.format(adjust_add_annex_paths))
                    print('[INFO] Save git-annex content and Register metadata(auto adjustment)')
                    save_annex_and_register_metadata(adjust_add_annex_paths, adjust_add_annex_paths, git_commit_msg)
                    os.system('git annex unlock')
                    print('[INFO] Save git content(auto adjustment)')
                    save_git(adjust_add_git_paths, message)
                else:
                    result = git_module.git_commmit(git_commit_msg)
                    print(result)
            warm_message = msg_mod.get('sync', 'resync_by_overwrite')
        else:
            # check both modified
            if git_module.is_conflict():
                print('[INFO] Files is CONFLICT')
                error_message = msg_mod.get('sync', 'conflict_error')
            else:
                error_message = msg_mod.get('sync', 'unexpected')
    else:
        try:
            print('[INFO] Push to Remote Repository')
            push()
            print('[INFO] Unlock git-annex content')
            os.system('git annex unlock')
        except:
            datalad_error = traceback.format_exc()
            error_message = msg_mod.get('sync', 'push_error')
        else:
            os.chdir(p.HOME_PATH)
            success_message = msg_mod.get('sync', 'success')
    finally:
        clear_output()
        if success_message:
            msg_display.display_info(success_message)
            # GIN-forkの実行環境一覧の更新日時を更新する
            container.patch_container()
            return True
        else:
            msg_display.display_warm(warm_message)
            msg_display.display_err(error_message)
            msg_display.display_log(datalad_error)
            return False


def extract_info_from_datalad_update_err(raw_msg:str)->str:
    start_index = raw_msg.find("[") + 1
    end_index = raw_msg.rfind("]")
    err_info = raw_msg[start_index:end_index]
    start_index = err_info.find("{")
    end_index = err_info.find("}")
    err_detail_info = err_info[start_index:end_index+1]
    start_index = err_detail_info.find("[") + 1
    end_index= err_detail_info.find("]")
    return err_detail_info[start_index:end_index]


def save_annex_and_register_metadata(gitannex_path :list[str], gitannex_files:list[str], message:str):
    """datalad save and metadata assignment (content_size, sha256, mime_type) to git annex files

    ARG
    ---------------
    git_path : str or list(str)
        Description : Define directories and files to be managed by git.
    gitannex_path : str or list(str)
        Description : Define directories and files to be managed by git-annex.
    gitannex_files : str or list(str) or None
        Description : Specify the file to which metadata(content_size, sha256, mime_type) is to be added. Specify None if metadata is not to be added.
    message : str
        Description : Commit message

    RETURN
    ---------------
    Returns nothing.

    EXCEPTION
    ---------------

    NOTE
    ----------------
        in the unlocked state, the entity of data downloaded from outside is also synchronized, so it should be locked.
    """

    # *The git annex metadata command can only be run on files that have already had a git annex add command run on them
    if len(gitannex_path) > 0:
        api.save(message=message + ' (git-annex)', path=gitannex_path)
        # register metadata for gitannex_files
        if type(gitannex_files) == str:
            register_metadata_for_annexdata(gitannex_files)
        elif type(gitannex_files) == list:
            for file in gitannex_files:
                register_metadata_for_annexdata(file)
        else:
            # if gitannex_files is not defined as a single file path (str) or multiple file paths (list), no metadata is given.
            pass

def save_git(git_path:list[str], message:str):
    if len(git_path) > 0:
        api.save(message=message + ' (git)', path=git_path, to_git=True)

def update():
    api.update(sibling=SIBLING, how='merge')

def push():
    api.push(to=SIBLING, data='auto')


def register_metadata_for_annexdata(file_path):
    """register_metadata(content_size, sha256, mime_type) for specified file

    ARG
    ---------------
    file_path : str
        Description : File path to which metadata is to be added.

    RETURN
    ---------------
    Returns nothing.

    EXCEPTION
    ---------------
    """

    if os.path.isfile(file_path):
        # generate metadata
        os.system('git annex unlock')
        mime_type = magic.from_file(file_path, mime=True)
        with open(file_path, 'rb') as f:
            binary_data = f.read()
            sha256 = hashlib.sha3_256(binary_data).hexdigest()
        content_size = os.path.getsize(file_path)

        # register_metadata
        os.chdir(p.HOME_PATH)
        os.system(f'git annex metadata "{file_path}" -s mime_type={mime_type} -s sha256={sha256} -s content_size={content_size}')
    else:
        pass


def register_metadata_for_downloaded_annexdata(file_path):
    """register metadata(sd_date_published)for the specified file

    ARG
    ---------------
    file_path : str
        Description : File path to which metadata is to be added.

    RETURN
    ---------------
    Returns nothing.

    EXCEPTION
    ---------------
    """
    os.system('git annex unlock')
    current_date = datetime.date.today()
    sd_date_published = current_date.isoformat()
    os.system(f'git annex metadata "{file_path}" -s sd_date_published={sd_date_published}')
