import os
import json
import glob

def fetch_param_file_path():
    param_file_path = '/home/jovyan/WORKFLOWS/EX-WORKFLOWS/param_files/params.json'
    return param_file_path

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
            #mdxの設定があれば該当部分のみ削除して設定を新たに追記する
            front = s[:s.find('Host mdx')]
            front = front.rstrip()
            find_words = 'IdentityFile ~/.ssh/id_rsa\n\tStrictHostKeyChecking no'
            back = s[(s.find(find_words)  + len(find_words)):]
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
    # SSHホスト（＝GIN）を信頼する設定
    path = fetch_ssh_config_path()
    s=''
    ginDomain = ginHttp.split('/')[-2]
    if os.path.exists(path):
        with open(path, 'r') as f:
            s = f.read()
        if s.find('host ' + ginDomain +'\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile=/dev/null') == -1:
        # 設定が無い場合は追記する
            with open('/home/jovyan/.ssh/config', mode='a') as f:
                write_GIN_config(mode='a', ginDomain = ginDomain)
        else:
        # すでにGINを信頼する設定があれば何もしない
            pass
    else:
        # 設定ファイルが無い場合は新規作成して設定を書きこむ
        with open('/home/jovyan/.ssh/config', mode='w') as f:
            write_GIN_config(mode='w', ginDomain = ginDomain)

def write_GIN_config(mode, ginDomain):
    path = fetch_ssh_config_path()
    with open(path, mode) as f:
        f.write('\nhost ' + ginDomain +'\n')
        f.write('\tStrictHostKeyChecking no\n')
        f.write('\tUserKnownHostsFile=/dev/null\n')

def fetch_files(dir_path):
    """引数に与えたディレクトリパス以下にあるファイルのリストを作成して返す"""
    data_list = []
    files = glob.glob(dir_path + "/*")
    for f in files:
        data_list += [f]
    return data_list

def fetch_experiment_title():
    with open("/home/jovyan/experiment.txt", "r") as f:
        experiment_title = f.read().splitlines()[0]
    return experiment_title

def fetch_experiment_file_path():
    experiment_title = fetch_experiment_title()
    experiment_path = '/home/jovyan/experiments/' + experiment_title
    return experiment_path