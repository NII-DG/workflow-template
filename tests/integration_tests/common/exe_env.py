import re
import uuid

from playwright.sync_api import sync_playwright, BrowserContext, Page, expect

from nb_libs.utils.git.git_module import get_current_branch

from . import notebook
from .credentials import get_credentials
from .path import GIN_FORK_URL, JUPYTER_HUB_URL, JUPYTER_HUB_HOME_URL
from .setting import write_it_setting, read_it_setting, write_state
from .utils import (
    get_browser_context,
    login_gakunin_rdm,
    signin_gin_fork,
    operate_base_required_every_time,
    operate_base_launch_an_experiment,
)


def create_res_env(env_key: str):
    """研究実行環境の作成"""

    if read_it_setting(env_key):
        # 環境作成済みの場合は作成しない
        return

    with sync_playwright() as playwright:
        context = get_browser_context(playwright)
        try:
            operate_res_env_creation(env_key, context)
        finally:
            browser = context.browser
            context.close()
            browser.close()


def operate_res_env_creation(env_key: str, context: BrowserContext):
    """研究実行環境の作成"""
    gin_fork = get_credentials('gin_fork')
    project_name = f'auto_test_it_{uuid.uuid4()}'

    page = context.new_page()

    # GIN-forkに遷移
    page.goto(GIN_FORK_URL)
    # GIN-forkにサインイン
    signin_gin_fork(page)

    # リポジトリ作成
    page.goto(f'{GIN_FORK_URL}/repo/create')
    page.locator('#repo_name').fill(project_name)
    page.locator('#project_name').fill('auto_test_it')
    page.get_by_role('button', name='Create Repository').click()

    # DMP登録(amed)
    page.goto(f'{GIN_FORK_URL}/{gin_fork["username"]}/{project_name}/_add/master/dmp.json/?schema=amed')
    # TODO idについているインデックスはリポジトリごとに異なるのでほかの方法で取得する
    # page.locator('#datasetStructure_904').select_option('for_parameters')
    page.get_by_role('button', name='Commit Changes').click()

    # maDMP作成
    page.get_by_role('button', name=re.compile('Generate maDMP')).click()

    # 実験実行環境新規作成
    with page.expect_popup() as page1_info:
        page.get_by_role('link', name='container.madmp').click()
    page1 = page1_info.value
    page1.get_by_role('textbox').fill(gin_fork['password'])
    page1.get_by_role('button', name='launch binder').click()

    # GakuNin RDMへのログイン
    login_gakunin_rdm(page1)

    page1.locator('#notebook').click(timeout=2*60*1000)  # サーバー作成に少し時間がかかるので長めに待つ

    # maDMP.ipynbの操作
    operate_madmp(page1)

    # 研究の情報を設定ファイルに保存
    url = page1.url.split('/')
    it_setting = {
        'project_name': project_name,
        'res_server': url[5],
        'user': url[4],
    }
    write_it_setting(env_key, it_setting)

    # ブラウザの情報を保存
    write_state(context)


def operate_madmp(page: Page):
    """maDMP.ipynbの操作"""

    # ノートブックの初期処理
    notebook.init_notebook(page)

    # チェックアウトするブランチを変更
    branch = get_current_branch()
    change_checkout_branch(page, branch)

    # 1-1. DMP情報の取り込み
    notebook.run_code_cell(page, 0, 1)

    # 1-2. リサーチフローの作成
    notebook.run_code_cell(page, 1, 2)

    # 1-3. GIN-forkアクセス準備
    # リサーチフローテンプレートのダウンロード
    notebook.run_code_cell(page, 2, 3)
    # DMP情報からリサーチフローの作成
    notebook.run_code_cell(page, 3, 4)

    # 2. 研究フロートップページへ
    notebook.run_code_cell(page, 4, 5)


def change_checkout_branch(page: Page, branch_name: str):
    """チェックアウトするブランチをmainから変更する"""

    # 入力のコード部分のHTMLはテキストボックスではないのでfillは使えない。
    # カーソルを移動してブランチ名を1文字ずつ入力することで実現する。

    text_area = 'div:nth-child(6) > .input > .inner_cell > .input_area > .CodeMirror > div > textarea'

    # カーソルをブランチ名の箇所に移動
    page.get_by_text('multi_options').click()
    page.locator(text_area).press('Control+ArrowRight')
    for i in range(6):
        page.locator(text_area).press('ArrowRight')
    # ブランチ名(main)を選択状態にする
    for i in range(4):
        page.locator(text_area).press('Shift+ArrowRight')
    # ブランチ名を入力
    for branch_char in list(branch_name):
        page.locator(text_area).press(branch_char)


def res_init_setup(env_key: str):
    """研究実行環境の初期セットアップ"""

    with sync_playwright() as playwright:
        context = get_browser_context(playwright)
        try:
            # 研究の初期セットアップ
            it_setting = read_it_setting(env_key)
            file_path = 'notebooks/research/base_required_every_time.ipynb'
            page_url = f'{JUPYTER_HUB_URL}/user/{it_setting["user"]}/{it_setting["res_server"]}/notebooks/WORKFLOWS/{file_path}'
            page = context.new_page()
            page.goto(page_url)

            # GakuNin RDMへのログイン
            login_gakunin_rdm(page)

            # base_required_every_time.ipynbの操作
            operate_base_required_every_time(page)

        finally:
            browser = context.browser
            context.close()
            browser.close()


def delete_res_env(env_key: str):
    """研究実行環境の削除"""

    with sync_playwright() as playwright:
        context = get_browser_context(playwright)
        try:
            operate_res_env_deletion(env_key, context)
        finally:
            browser = context.browser
            context.close()
            browser.close()


def operate_res_env_deletion(env_key: str, context: BrowserContext):
    it_setting = read_it_setting(env_key)
    if 'res_server' not in it_setting:
        # 何らかの理由で削除済みの場合は何もしない
        return

    page = context.new_page()

    # サーバー削除
    page.goto(JUPYTER_HUB_HOME_URL)

    expect(page.locator(f'#stop-{it_setting["res_server"]}')).to_be_visible()
    page.locator(f'#stop-{it_setting["res_server"]}').click()
    expect(page.locator(f'#delete-{it_setting["res_server"]}')).to_be_visible(timeout=10*1000)
    page.locator(f'#delete-{it_setting["res_server"]}').click()

    # GIN-forkのリポジトリ削除
    gin_fork = get_credentials('gin_fork')
    page_url = f'{GIN_FORK_URL}/{gin_fork["username"]}/{it_setting["project_name"]}/settings'
    page.goto(page_url)

    page.get_by_role('button', name='Delete This Repository').click()
    page.locator('#delete-repo-modal #repo_name').fill(it_setting['project_name'])
    page.get_by_role('button', name='Confirm Deletion').click()


def create_exp_env(env_key: str):
    """実験実行環境の作成"""

    if read_it_setting(env_key):
        # 環境作成済みの場合は作成しない
        return

    with sync_playwright() as playwright:
        context = get_browser_context(playwright)
        try:
            # 研究実行環境の作成
            operate_res_env_creation(env_key, context)
            # 実験実行環境の作成
            operate_exp_env_creation(env_key, context)
        finally:
            browser = context.browser
            context.close()
            browser.close()


def operate_exp_env_creation(env_key: str, context: BrowserContext):
    """実験実行環境の作成"""

    # 研究の初期セットアップ
    it_setting = read_it_setting(env_key)
    file_path = 'notebooks/research/base_required_every_time.ipynb'
    page_url = f'{JUPYTER_HUB_URL}/user/{it_setting["user"]}/{it_setting["res_server"]}/notebooks/WORKFLOWS/{file_path}'
    page = context.new_page()
    page.goto(page_url)

    # GakuNin RDMへのログイン
    login_gakunin_rdm(page)

    # base_required_every_time.ipynbの操作
    operate_base_required_every_time(page)

    # 実験実行環境作成
    file_path = 'notebooks/research/base_launch_an_experiment.ipynb'
    page_url = f'{JUPYTER_HUB_URL}/user/{it_setting["user"]}/{it_setting["res_server"]}/notebooks/WORKFLOWS/{file_path}'
    page.goto(page_url)

    # base_launch_an_experiment.ipynbの操作
    exp_page = operate_base_launch_an_experiment(page)

    # 実験の情報を設定ファイルに保存
    exp_url = exp_page.url.split('/')
    it_setting['exp_server'] = exp_url[5]
    write_it_setting(env_key, it_setting)


def delete_exp_env(env_key: str):
    """実験実行環境の削除"""

    with sync_playwright() as playwright:
        context = get_browser_context(playwright)
        try:
            # 実験実行環境の削除
            operate_exp_env_deletion(env_key, context)
            # 研究実行環境の削除
            operate_res_env_deletion(env_key, context)
        finally:
            browser = context.browser
            context.close()
            browser.close()


def operate_exp_env_deletion(env_key: str, context: BrowserContext):
    """実験実行環境の削除"""

    it_setting = read_it_setting(env_key)
    if 'exp_server' not in it_setting:
        # 実験実行環境を作成していない場合は削除しない
        return

    page = context.new_page()

    # サーバー削除
    page.goto(JUPYTER_HUB_HOME_URL)

    expect(page.locator(f'#stop-{it_setting["exp_server"]}')).to_be_visible()
    page.locator(f'#stop-{it_setting["exp_server"]}').click()
    expect(page.locator(f'#delete-{it_setting["exp_server"]}')).to_be_visible(timeout=10*1000)
    page.locator(f'#delete-{it_setting["exp_server"]}').click()
