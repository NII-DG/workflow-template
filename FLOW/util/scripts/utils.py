from .... utils.gin_api import api as gin_api
from datalad import api
from http import HTTPStatus
import requests
import getpass
from IPython.display import clear_output
from urllib import parse
import glob
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def fetch_param_file_path() -> str:
    return '/home/jovyan/WORKFLOWS/FLOW/param_files/params.json'


def fetch_monitoring_param_file_path() -> str:
    return '/home/jovyan/WORKFLOWS/FLOW/param_files/monitoring_params.json'


def reflect_monitoring_results(monitoring_item, isOK: bool, package_path) -> None:
    # モニタリング観点名とnotebookへのパスとを取得
    path_params = fetch_param_file_path()
    params = {}
    with open(path_params, 'r') as f:
        params = json.load(f)

    nb = params['monitoring'][monitoring_item]
    # nb['name']: モニタリング観点名(str)
    # nb['path']: Notebookへのパス(str)

    nb['path'] = os.path.relpath(nb['path'], package_path)

    # READMEの内容を取得する
    readme_path = package_path + '/README.md'
    with open(readme_path, "r") as f:
        readme = f.read()
    point1 = readme.find("| " + nb['name'] + " |")
    output = readme[:point1]

    # 該当する行を書き換え
    output += "| " + nb['name'] + " | [" + ("OK" if isOK else "NG") + "](" + nb['path'] + ") |"

    point2 = readme[point1:].find("\n")
    output += readme[point1 + point2:]

    with open(readme_path, "w") as f:
        f.write(output)


def verify_GIN_user():
    # 以下の認証の手順で用いる、
    # GINのドメイン名等をパラメタファイルから取得する
    params = {}
    with open(fetch_param_file_path(), mode='r') as f:
        params = json.load(f)

    # 正常に認証が終わるまで繰り返し
    global tokens
    global access_token
    while True:
        name = input("ユーザー名：")
        password = getpass.getpass("パスワード：")
        email = input("メールアドレス：")
        clear_output()

        # GIN API Basic Authentication
        # refs: https://docs.python-requests.org/en/master/user/authentication/

        # 既存のトークンがあるか確認する
        baseURL = params['siblings']['ginHttp'] + '/api/v1/users/'
        response = requests.get(baseURL + name + '/tokens', auth=(name, password))
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            print("ユーザ名、またはパスワードが間違っています。\n恐れ入りますがもう一度ご入力ください。")
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
        この時、/home/jovyan/.ssh/configファイルに設定値を書き込みいく。
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
    pr = parse.urlparse(params['siblings']['ginHttp'])
    res_data = res.json()
    ssh_url = res_data["data"][0]["ssh_url"]
    http_url = res_data["data"][0]["html_url"] + '.git'
    api.siblings(action='configure', name='gin', url=ssh_url)
    api.siblings(action='configure', name='origin', url=http_url)
    res = gin_api.repos_search_by_repo_id(pr.scheme, pr.netloc, repo_id)
    print(res.json())
