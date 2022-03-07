import os
import json

def fetch_param_file_path():
    param_file_path = '/home/jovyan/EX-WORKFLOW/param_files/params.json'
    return param_file_path

def fetch_ssh_config_path():
    ssh_config_path = '/home/jovyan/.ssh/config'
    return ssh_config_path

def write_mdx_config(item, mode, mdxDomein, name_mdx):
    path = fetch_ssh_config_path()
    with open(path, mode) as f:
        f.write('\nHost mdx\n')
        f.write('\tHostname ' + mdxDomein + '\n')
        f.write('\tUser ' + name_mdx + '\n')
        f.write('\tPort 22\n')
        f.write('\tIdentityFile ~/.ssh/id_rsa\n')
        f.write('\tStrictHostKeyChecking no\n')

def write_GIN_config(item, mode):
    path = fetch_ssh_config_path()
    with open(path, mode) as f:
        f.write('\nhost dg02.dg.rcos.nii.ac.jp\n')
        f.write('\tStrictHostKeyChecking no\n')
        f.write('\tUserKnownHostsFile=/dev/null\n')
        
def config_GIN():
    # SSHホスト（＝GIN）を信頼する設定
    # ドメイン名がハードコーディングにつき要修正
    path = fetch_ssh_config_path()
    s=''
    if os.path.exists(path):
        with open(path, 'r') as f:
            s = f.read()
        if s.find('host dg02.dg.rcos.nii.ac.jp\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile=/dev/null') == -1:
        # 設定が無い場合は追記する
            with open('/home/jovyan/.ssh/config', mode='a') as f:
                write_GIN_config(item='GIN', mode='a')   
        else:
        # すでにGINを信頼する設定があれば何もしない
            pass
    else:
        # 設定ファイルが無い場合は新規作成して設定を書きこむ
        with open('/home/jovyan/.ssh/config', mode='w') as f:
            write_GIN_config(item='GIN', mode='w')
        
def config_mdx(name_mdx, mdxDomein):

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
            write_mdx_config(item='mdx', mode='a', mdxDomein=mdxDomein, name_mdx=name_mdx)
        
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
            write_mdx_config(item='mdx', mode='a', mdxDomein=mdxDomein, name_mdx=name_mdx)
    else:
        # 設定ファイルが無い場合、新規作成して新たに書き込む
        write_mdx_config(item='mdx', mode='w', mdxDomein=mdxDomein, name_mdx=name_mdx)

