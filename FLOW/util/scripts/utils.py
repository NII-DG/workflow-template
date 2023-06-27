import json
import os
import glob
import shutil
from IPython.display import clear_output, HTML, display
from urllib import parse
import getpass
import requests
from http import HTTPStatus
from datalad import api
import traceback
import subprocess
from subprocess import PIPE
import magic
import hashlib
import datetime
import re
import panel as pn
os.chdir('/home/jovyan/WORKFLOWS')
from utils.git import git_module
from utils.common import common
from utils import display_util

def fetch_param_file_path() -> str:
    return '/home/jovyan/WORKFLOWS/FLOW/param_files/params.json'


def fetch_gin_monitoring_assigned_values():
    # dmp.jsonからcontentSize, workflowIdentifier, datasetStructureの値を取得する
    dmp_file_path = '/home/jovyan/dmp.json'
    with open(dmp_file_path, mode='r') as f:
         dmp_json = json.load(f)
    assigned_values = {
        'workflowIdentifier': dmp_json['workflowIdentifier'],
        'contentSize': dmp_json['contentSize'],
        'datasetStructure': dmp_json['datasetStructure']
    }
    return assigned_values

def get_datasetStructure():
    assigned_values = fetch_gin_monitoring_assigned_values()
    return assigned_values['datasetStructure']


user_name_form = pn.widgets.TextInput(name="GIN-fork ユーザー名", placeholder= "Enter your user name on GIN-fork here...", width=700)
password_form = pn.widgets.PasswordInput(name="パスワード", placeholder= "Enter password here...", width=700)
mail_address_form = pn.widgets.TextInput(name="メールアドレス", placeholder= "Enter email address here...", width=700)
submit_button_user_auth = pn.widgets.Button(name= "入力を完了する", button_type= "primary")

def submit_user_auth(event):
    user_name = user_name_form.value
    password = password_form.value
    mail_addres =mail_address_form.value

    # validate value
    ## user name
    if user_name is None:
        submit_button_user_auth.button_type = 'danger'
        submit_button_user_auth.name = 'ユーザー名が入力されていません。ユーザー名を入力し再度、ボタンとクリックしてください。'
        return

    if not validate_format_username(user_name):
        submit_button_user_auth.button_type = 'danger'
        submit_button_user_auth.name = 'ユーザ―名は英数字および"-", "_", "."のみで入力し再度、ボタンとクリックしてください。'
        return

    ## password
    if password is None:
        submit_button_user_auth.button_type = 'danger'
        submit_button_user_auth.name = 'パスワードが入力されていません。パスワードを入力し再度、ボタンとクリックしてください。'
        return

    ## mail addres
    if mail_addres is None:
        submit_button_user_auth.button_type = 'danger'
        submit_button_user_auth.name = 'メールアドレスが入力されていません。メールアドレスを入力し再度、ボタンとクリックしてください。'
        return

    if not validate_format_mail_addres(mail_addres):
        submit_button_user_auth.button_type = 'danger'
        submit_button_user_auth.name = 'メールアドレスの形式が不正です。再度、入力しボタンとクリックしてください。'
        return

    # If the entered value passes validation, a request for user authentication to GIN-fork is sent.
    # GIN API Basic Authentication
    # refs: https://docs.python-requests.org/en/master/user/authentication/
    params = {}
    with open(fetch_param_file_path(), mode='r') as f:
        params = json.load(f)

    baseURL = params['siblings']['ginHttp'] + '/api/v1/users/'
    response = requests.get(baseURL + user_name + '/tokens', auth=(user_name, password))

    ## Unauthorized
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        submit_button_user_auth.button_type = 'danger'
        submit_button_user_auth.name = 'ユーザ名、またはパスワードが間違っています。再度、入力しボタンとクリックしてください。'
        return

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
    shutil.copy("~/.gitconfig", "~/WORKFLOWS/PACKAGE/.gitconfig")

    submit_button_user_auth.button_type = 'success'
    submit_button_user_auth.name = '認証が正常に完了しました。次の手順へお進みください。'

def validate_format_username(user_name):
    validation = re.compile(r'^[a-zA-Z0-9\-_.]+$')
    return validation.fullmatch(user_name)

def validate_format_mail_addres(mail_addres):
    validation =     re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return validation.fullmatch(mail_addres)

def create_user_auth_form()->pn.Column:
    user_auth_columns = pn.Column()
    user_auth_columns.append(user_name_form)
    user_auth_columns.append(password_form)
    user_auth_columns.append(mail_address_form)
    button = pn.widgets.Button(name= "入力を完了する", button_type= "primary")
    button.on_click(submit_user_auth)
    user_auth_columns.append(button)
    return user_auth_columns











def verify_GIN_user():
    # 以下の認証の手順で用いる、
    # GINのドメイン名等をパラメタファイルから取得する
    params = {}
    with open(fetch_param_file_path(), mode='r') as f:
        params = json.load(f)

    # 正常に認証が終わるまで繰り返し
    global tokens
    global access_token
    clear_output()
    while True:
        warn = ''
        validation = re.compile(r'^[a-zA-Z0-9\-_.]+$')
        while True:
            display_util.display_info("GIN-forkのユーザー情報を入力後、Enterキーを押下してください。")
            if len(warn) > 0:
                display_util.display_err(warn)
            name = input("ユーザー名：")
            if len(name) <= 0:
                warn = "ユーザー名が入力されていません。ユーザー名を入力してください。"
                clear_output()
            elif not validation.fullmatch(name):
                warn = 'ユーザ―名は英数字および"-", "_", "."のみで入力してください。'
                clear_output()
            else:
                break
        warn = ''
        while True:
            clear_output()
            display_util.display_info("GIN-forkのユーザー情報を入力後、Enterキーを押下してください。")
            display_util.display_msg("ユーザー名："+ name)
            if len(warn) > 0:
                display_util.display_err(warn)
            password = getpass.getpass("パスワード：")
            if len(password) <= 0:
                warn = "パスワードが入力されていません。パスワードを入力してください。"
            else:
                break
        validation = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        warn = ''
        while True:
            clear_output()
            display_util.display_info("GIN-forkのユーザー情報を入力後、Enterキーを押下してください。")
            display_util.display_msg("ユーザー名："+ name)
            display_util.display_msg("パスワード：········")
            if len(warn) > 0:
                display_util.display_err(warn)
            email = input("メールアドレス：")
            if len(email) <= 0:
                warn = "メールアドレスが入力されていません。メールアドレスを入力してください。"
            elif not validation.fullmatch(email):
                warn = "メールアドレスの形式が不正です。恐れ入りますがもう一度ご入力ください。"
            else:
                break
        clear_output()

        # GIN API Basic Authentication
        # refs: https://docs.python-requests.org/en/master/user/authentication/

        # 既存のトークンがあるか確認する
        baseURL = params['siblings']['ginHttp'] + '/api/v1/users/'
        response = requests.get(baseURL + name + '/tokens', auth=(name, password))
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            display_util.display_err("ユーザ名、またはパスワードが間違っています。<br>恐れ入りますがもう一度ご入力ください。<br>")
            continue

        tokens = response.json()
        if len(tokens) >= 1:
            access_token = response.json()[-1]
            clear_output()
            break
        elif len(tokens) < 1:
            # 既存のトークンがなければ作成する
            response = requests.post(baseURL + name + '/tokens', data={"name": "system-generated"}, auth=(name, password))
            if response.status_code == HTTPStatus.CREATED:
                access_token = response.json()
                clear_output()
                break
    return tokens, access_token, name, email


def fetch_ssh_config_path():
    ssh_config_path = '/home/jovyan/.ssh/config'
    return ssh_config_path


def config_mdx(name_mdx, mdxDomain):
    # mdx接続情報を設定ファイルに反映させる
    path = fetch_ssh_config_path()
    s = ''

    if os.path.exists(path):
        # 設定ファイルがある場合
        with open(path, "r") as f:
            s = f.read()

        # mdxの設定があれば該当部分のみ削除して設定を新たに追記する
        if s.find('Host mdx') == -1:
            # mdxの設定が無ければ追記する
            write_mdx_config(mode='a', mdxDomain=mdxDomain, name_mdx=name_mdx)

        else:
            # mdxの設定があれば該当部分のみ削除して設定を新たに追記する
            front = s[:s.find('Host mdx')]
            front = front.rstrip()
            find_words = 'IdentityFile ~/.ssh/id_rsa\n\tStrictHostKeyChecking no'
            back = s[(s.find(find_words) + len(find_words)):]
            back = back.strip()
            if len(back) >= 1:
                s = front + '\n' + back + '\n'
            elif len(front) <= 0:
                s = front
            else:
                s = front + '\n'
            with open(path, 'w') as f:
                f.write(s)
            write_mdx_config(mode='a', mdxDomain=mdxDomain, name_mdx=name_mdx)
    else:
        # 設定ファイルが無い場合、新規作成して新たに書き込む
        write_mdx_config(mode='w', mdxDomain=mdxDomain, name_mdx=name_mdx)


def write_mdx_config(mode, mdxDomain, name_mdx):
    path = fetch_ssh_config_path()
    with open(path, mode) as f:
        f.write('\nHost mdx\n')
        f.write('\tHostname ' + mdxDomain + '\n')
        f.write('\tUser ' + name_mdx + '\n')
        f.write('\tPort 22\n')
        f.write('\tIdentityFile ~/.ssh/id_rsa\n')
        f.write('\tStrictHostKeyChecking no\n')


def config_GIN(ginHttp):
    """リポジトリホスティングサーバのURLからドメイン名を抽出してコンテナに対してSHH通信を信頼させるメソッド
        この時、/home/jovyan/.ssh/configファイルに設定値を出力する。
    ARG
    ---------------------------
    ginHttp : str
        Description : リポジトリホスティングサーバのURL ex : http://dg01.dg.rcos.nii.ac.jp
    """
    # SSHホスト（＝GIN）を信頼する設定
    path = fetch_ssh_config_path()
    s = ''
    pr = parse.urlparse(ginHttp)
    ginDomain = pr.netloc
    if os.path.exists(path):
        with open(path, 'r') as f:
            s = f.read()
        if s.find('host ' + ginDomain + '\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile=/dev/null') == -1:
            # 設定が無い場合は追記する
            with open('/home/jovyan/.ssh/config', mode='a') as f:
                write_GIN_config(mode='a', ginDomain=ginDomain)
        else:
            # すでにGINを信頼する設定があれば何もしない
            pass
    else:
        # 設定ファイルが無い場合は新規作成して設定を書きこむ
        with open('/home/jovyan/.ssh/config', mode='w') as f:
            write_GIN_config(mode='w', ginDomain=ginDomain)


def write_GIN_config(mode, ginDomain):
    path = fetch_ssh_config_path()
    with open(path, mode) as f:
        f.write('\nhost ' + ginDomain + '\n')
        f.write('\tStrictHostKeyChecking no\n')
        f.write('\tUserKnownHostsFile=/dev/null\n')


def fetch_files(dir_path):
    """引数に与えたディレクトリパス以下にあるファイルのリストを作成して返す"""
    data_list = []
    files = glob.glob(dir_path + "/*")
    for f in files:
        data_list += [f]
    return data_list


def update_repo_url():
    # HTTPとSSHのリモートURLを最新化する
    # APIリクエストに必要な情報を取得する
    params = {}
    with open(fetch_param_file_path(), mode='r') as f:
        params = json.load(f)
    os.chdir(os.environ['HOME'])
    file_path = '.repository_id'
    f = open(file_path, 'r')
    repo_id = f.read()
    f.close()

    # APIからリポジトリの最新のSSHのリモートURLを取得し、リモート設定を更新する
    request_url = params['siblings']['ginHttp'] + '/api/v1/repos/search?id=' + repo_id
    res = requests.get(request_url)
    res_data = res.json()
    ssh_url = res_data['data'][0]['ssh_url']
    http_url = res_data['data'][0]['html_url'] + '.git'
    update_list = [['gin', ssh_url],['origin', http_url]]
    for update_target in update_list:
        result = subprocess.run('git remote set-url ' + update_target[0] + ' ' + update_target[1], shell=True, stdout=PIPE, stderr=PIPE, text=True)
        if 'No such remote' in result.stderr:
            subprocess.run('git remote add ' + update_target[0] + ' ' + update_target[1], shell=True)


SIBLING = 'gin'
SUCCESS = 'データ同期が完了しました。'
RESYNC_REPO_RENAME = '同期不良が発生しました(リモートリポジトリ名の変更)。自動調整が実行されたため、同セルを再実行してください。'
RESYNC_BY_OVERWRITE = '同期不良が発生しました(ファイルの変更)。自動調整が実行されため、同セルを再実行してください。'
CONNECT_REPO_ERROR = 'リポジトリに接続できません。リポジトリが存在しているか確認してください。'
CONFLICT_ERROR = 'リポジトリ側の変更と競合しました。競合を解決してください。'
PUSH_ERROR = 'リポジトリへの同期に失敗しました。'
UNEXPECTED_ERROR = '想定外のエラーが発生しています。担当者に問い合わせください。'


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

    EXCEPTION
    ---------------
    CONNECT_REPO_ERROR
    CONFLICT_ERROR
    PUSH_ERROR

    memo:
        update()を最初にするとgit annex lockができない。addをする必要がある。
    """

    success_message = ''
    warm_message = ''
    error_message = ''
    datalad_error = ''
    try:

        os.chdir(os.environ['HOME'])
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
        if 'Repository does not exist' in datalad_error:
            try:
                # update URLs of remote repositories
                update_repo_url()
                print('[INFO] Update repository URL')
                warm_message = RESYNC_REPO_RENAME
            except:
                # repository may not exist
                error_message = CONNECT_REPO_ERROR
        elif 'files would be overwritten by merge:' in datalad_error:
            print('[INFO] Files would be overwritten by merge')
            git_commit_msg = '{}(auto adjustment)'.format(message)
            err_key_info = extract_info_from_datalad_update_err(datalad_error)
            file_paths = list[str]()
            os.chdir(os.environ['HOME'])
            os.system('git annex lock')
            if 'The following untracked working tree' in err_key_info:
                file_paths = common.get_filepaths_from_dalalad_error(err_key_info)
                adjust_add_git_paths = list[str]()
                adjust_add_annex_paths = list[str]()
                for path in file_paths:
                    if '\\u3000' in path:
                        path = path.replace('\\u3000', '　')
                    if common.is_should_annex_content_path(path):
                        adjust_add_annex_paths.append(path)
                    else:
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
                            adjust_add_annex_paths.append(path)
                        else:
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
            warm_message = RESYNC_BY_OVERWRITE
        else:
            # check both modified
            if git_module.is_conflict():
                print('[INFO] Files is CONFLICT')
                error_message = CONFLICT_ERROR
            else:
                error_message = UNEXPECTED_ERROR
    else:
        try:
            print('[INFO] Push to Remote Repository')
            push()
            print('[INFO] Unlock git-annex content')
            os.system('git annex unlock')
        except:
            datalad_error = traceback.format_exc()
            error_message = PUSH_ERROR
        else:
            os.chdir(os.environ['HOME'])
            success_message = SUCCESS
    finally:
        clear_output()
        if success_message:
            display_util.display_info(success_message)
            return True
        else:
            display_util.display_warm(warm_message)
            display_util.display_err(error_message)
            display_util.display_log(datalad_error)
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
        os.chdir(os.environ['HOME'])
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

# 研究名と実験名を表示する関数
def show_name(color='black', EXPERIMENT_TITLE=None):
    # リモートリポジトリのURLを最新化する
    update_repo_url()
    os.chdir(os.environ['HOME'])

    # 研究リポジトリ名表示
    RESEARCH_TITLE = subprocess.getoutput('git config --get remote.origin.url').split('/')[-1].replace('.git', '')
    res_text = "<h1 style='color:" + color + "'>研究リポジトリ名：" + RESEARCH_TITLE + "</h1>"
    clear_output()
    display(HTML(res_text))

    if EXPERIMENT_TITLE is not None:
        #実験パッケージ名表示
        exp_text = "<h1 style='color:" + color + "'>実験パッケージ名：" + EXPERIMENT_TITLE + "</h1>"
        display(HTML(exp_text))