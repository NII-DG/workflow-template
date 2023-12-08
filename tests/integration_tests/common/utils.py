import os
import sys

from playwright.sync_api import Playwright, Page, expect

from nb_libs.utils.message import message

from . import notebook
from .credentials import get_credentials
from .path import GIN_FORK_URL
from .setting import STATE_PATH


def get_browser_context(playwright: Playwright):
    """ブラウザコンテキストを取得する"""

    args = sys.argv

    # ブラウザの表示設定
    headless = True
    if '--headed' in args:
        headless = False
    if 'debugpy' in sys.modules:
        # デバッグ実行の場合はブラウザを表示する
        headless = False

    # State file
    storage_state = STATE_PATH if os.path.exists(STATE_PATH) else None

    context = None
    if '--browser' in args:
        browser_type = args[args.index('--browser') + 1]
        if browser_type == 'chromium':
            if '--browser-channel' in args:
                channel_type = args[args.index('--browser-channel') + 1]
                browser = playwright.chromium.launch(channel=channel_type, headless=headless)
            else:
                browser = playwright.chromium.launch(headless=headless)
            context = browser.new_context(storage_state=storage_state)

        elif browser_type == 'firefox':
            browser = playwright.firefox.launch(headless=headless)
            context = browser.new_context(storage_state=storage_state)

        elif browser_type == 'webkit':
            browser = playwright.webkit.launch(headless=headless)
            device_option = [x for x in args if '--device=' in x]
            if device_option:
                device_type = device_option[0].replace('--device=', '').replace('"', '')
                if device_type in playwright.devices:
                    device = playwright.devices[device_type]
                    context = browser.new_context(storage_state=storage_state, **device)
            else:
                context = browser.new_context(storage_state=storage_state)

    if not context:
        # ブラウザの指定なしの場合
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=storage_state)

    return context


def login_gakunin_rdm(page: Page):
    """GakuNin RDMにログインする"""

    # stateファイルがある場合はログイン済み
    if os.path.exists(STATE_PATH):
        return

    # 認証情報取得
    credentials = get_credentials('gakunin_rdm')

    page.locator('#dropdown_img').click()
    page.get_by_text('GakuNin RDM IdP').click()
    page.locator('#wayf_submit_button').click()
    page.get_by_label('Username').fill(credentials['username'])
    page.get_by_label('Password').fill(credentials['password'])
    page.get_by_role('button', name='Login').click()
    page.get_by_role('button', name='Accept').click()


def signin_gin_fork(page: Page):
    """GIN-forkにサインインする"""

    # stateファイルがある場合はサインイン済み
    if os.path.exists(STATE_PATH):
        return

    gin_fork = get_credentials('gin_fork')

    # サインイン
    page.goto(f'{GIN_FORK_URL}/user/login?redirect_to=')
    page.get_by_label('Username or email').fill(gin_fork['username'])
    page.get_by_label('Password').fill(gin_fork['password'])
    page.get_by_text('Remember Me').click()
    page.get_by_role('button', name='Sign In').click()


def operate_base_required_every_time(page: Page):
    """base_required_every_time.ipynbの操作"""

    # ノートブックの初期処理
    notebook.init_notebook(page)

    # 共通メニュー
    notebook.run_code_cell(page, 0, None)

    # 1つ目のセルの実行インデックス取得
    cell = notebook.get_code_cell(page, 0)
    execute_index = notebook.get_execute_index(cell)

    # 1. 事前準備
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 1, execute_index)
    # GIN-forkのユーザー情報入力
    gin_fork = get_credentials('gin_fork')
    cell = notebook.get_code_cell(page, 1)
    cell.get_by_placeholder(message.get('user_auth', 'username_help')).fill(gin_fork['username'])
    cell.get_by_placeholder(message.get('user_auth', 'password_help')).fill(gin_fork['password'])
    cell.get_by_role('button').click()
    expect(page.get_by_role('button', name=message.get('user_auth', 'success'))).to_be_visible()

    # 2. 初期セットアップ
    # 2-1. 不要なGIN-forkアクセストークンの削除
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 2, execute_index)

    # 2-2. データ同期設定
    # dataladデータセット設定
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 3, execute_index)
    # SSHキー作成
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 4, execute_index)
    # GIN-forkへの公開鍵の登録
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 5, execute_index)
    # SSHホスト（GIN-fork）を信頼することを設定する
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 6, execute_index)
    # GIN-forkへの同期調整
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 7, execute_index)
    # ローカルリポジトリへのSSH接続情報の登録
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 8, execute_index)

    # 2-3. 実行環境情報を登録
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 9, execute_index)

    # 2-4. 研究フロー図を更新
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 10, execute_index)

    # 2-5. 実行結果の保存準備
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 11, execute_index)

    # 3. GIN-forkに実行結果を同期
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 12, execute_index, 60 * 1000)

    # 4. 研究フロートップページへ
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 13, execute_index)


def operate_base_launch_an_experiment(page: Page) -> Page:
    """base_launch_an_experiment.ipynbの操作"""

    # ノートブックの初期処理
    notebook.init_notebook(page)

    # 共通メニュー
    notebook.run_code_cell(page, 0, None)

    # 1つ目のセルの実行インデックス取得
    cell = notebook.get_code_cell(page, 0)
    execute_index = notebook.get_execute_index(cell)

    # 1. 実験実行環境の作成
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 1, execute_index)
    # 作成ボタンクリック
    cell = notebook.get_code_cell(page, 1)
    with page.expect_popup() as page1_info:
        cell.get_by_role('button', name=message.get('launch', 'launch')).click()
    page1 = page1_info.value
    page1.locator('#notebook').click(timeout=2*60*1000)  # サーバー作成に少し時間がかかるので長めに待つ

    return page1
