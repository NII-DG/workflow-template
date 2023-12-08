from playwright.sync_api import BrowserContext, Page, Locator, expect

from nb_libs.utils.message import message

from tests.integration_tests.common import notebook
from tests.integration_tests.common.credentials import get_credentials
from tests.integration_tests.common.path import JUPYTER_HUB_URL, SCREENSHOT_DIR
from tests.integration_tests.common.setting import read_it_setting
from tests.integration_tests.common.utils import login_gakunin_rdm

FILE_PATH = 'notebooks/research/base_required_every_time.ipynb'


def base_required_every_time(env_key: str, context: BrowserContext):
    it_setting = read_it_setting(env_key)
    page_url = f'{JUPYTER_HUB_URL}/user/{it_setting["user"]}/{it_setting["res_server"]}/notebooks/WORKFLOWS/{FILE_PATH}'
    page = context.new_page()
    page.goto(page_url)

    # GakuNin RDMへのログイン
    login_gakunin_rdm(page)

    # ノートブックの初期処理
    notebook.init_notebook(page)

    # 共通メニュー
    cell_index = 0
    cell = notebook.get_code_cell(page, cell_index)
    # セルの実行
    notebook.run_code_cell(page, cell_index, None)
    # セル実行後のスクリーンショット保存
    notebook.screenshot(page, 'research/base_required_every_time_01.png')
    # セルの実行に成功したか確認
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # 1つ目のセルの実行インデックス取得
    execute_index = notebook.get_execute_index(cell)

    # 1. 事前準備
    cell_index = 1
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index)
    notebook.screenshot(page, 'research/base_required_every_time_02.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)
    # GIN-forkのユーザー情報入力のテスト
    check_gin_fork_user_input(page, cell)

    # 2. 初期セットアップ
    # 2-1. 不要なGIN-forkアクセストークンの削除
    cell_index = 2
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index)
    notebook.screenshot(page, 'research/base_required_every_time_03.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # 2-2. データ同期設定
    # dataladデータセット設定
    cell_index = 3
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index)
    notebook.screenshot(page, 'research/base_required_every_time_04.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # SSHキー作成
    cell_index = 4
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index)
    notebook.screenshot(page, 'research/base_required_every_time_05.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # GIN-forkへの公開鍵の登録
    cell_index = 5
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index)
    notebook.screenshot(page, 'research/base_required_every_time_06.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # SSHホスト（GIN-fork）を信頼することを設定する
    cell_index = 6
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index)
    notebook.screenshot(page, 'research/base_required_every_time_07.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # GIN-forkへの同期調整
    cell_index = 7
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index)
    notebook.screenshot(page, 'research/base_required_every_time_08.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # ローカルリポジトリへのSSH接続情報の登録
    cell_index = 8
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index)
    notebook.screenshot(page, 'research/base_required_every_time_09.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # 2-3. 実行環境情報を登録
    cell_index = 9
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index)
    notebook.screenshot(page, 'research/base_required_every_time_10.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # 2-4. 研究フロー図を更新
    cell_index = 10
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index)
    notebook.screenshot(page, 'research/base_required_every_time_11.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # 2-5. 実行結果の保存準備
    cell_index = 11
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index)
    notebook.screenshot(page, 'research/base_required_every_time_12.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # 3. GIN-forkに実行結果を同期
    cell_index = 12
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index, 60 * 1000)
    notebook.screenshot(page, 'research/base_required_every_time_13.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # 4. 研究フロートップページへ
    cell_index = 13
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    notebook.run_code_cell(page, cell_index, execute_index, 60 * 1000)
    notebook.screenshot(page, 'research/base_required_every_time_14.png')
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)


def check_gin_fork_user_input(page: Page, cell: Locator):
    """GIN-forkのユーザー情報入力のテスト"""
    gin_fork = get_credentials('gin_fork')

    # ユーザー名未入力
    cell.get_by_placeholder(message.get('user_auth', 'username_help')).fill('')
    cell.get_by_placeholder(message.get('user_auth', 'password_help')).fill(gin_fork['password'])
    cell.get_by_role('button').click()
    notebook.screenshot(page, 'research/base_required_every_time_02_1.png')
    expect(cell.get_by_role('button', name=message.get('user_auth', 'username_empty_error'))).to_be_visible()

    # パスワード未入力
    cell.get_by_placeholder(message.get('user_auth', 'username_help')).fill(gin_fork['username'])
    cell.get_by_placeholder(message.get('user_auth', 'password_help')).fill('')
    cell.get_by_role('button').click()
    notebook.screenshot(page, 'research/base_required_every_time_02_2.png')
    expect(cell.get_by_role('button', name=message.get('user_auth', 'password_empty_error'))).to_be_visible()

    # ユーザー名不正
    cell.get_by_placeholder(message.get('user_auth', 'username_help')).fill('!dummy')
    cell.get_by_placeholder(message.get('user_auth', 'password_help')).fill('dummy')
    cell.get_by_role('button').click()
    notebook.screenshot(page, 'research/base_required_every_time_02_3.png')
    expect(cell.get_by_role('button', name=message.get('user_auth', 'username_pattern_error'))).to_be_visible()

    # 認証失敗
    cell.get_by_placeholder(message.get('user_auth', 'username_help')).fill('dummy')
    cell.get_by_placeholder(message.get('user_auth', 'password_help')).fill('dummy')
    page.wait_for_timeout(500)
    cell.get_by_role('button').click()
    page.wait_for_timeout(500)
    notebook.screenshot(page, 'research/base_required_every_time_02_4.png')
    expect(cell.get_by_role('button', name=message.get('user_auth', 'unauthorized'))).to_be_visible()

    # 正常ケース
    cell.get_by_placeholder(message.get('user_auth', 'username_help')).fill(gin_fork['username'])
    cell.get_by_placeholder(message.get('user_auth', 'password_help')).fill(gin_fork['password'])
    page.wait_for_timeout(500)
    cell.get_by_role('button').click()
    page.wait_for_timeout(500)
    notebook.screenshot(page, 'research/base_required_every_time_02_5.png')
    expect(cell.get_by_role('button', name=message.get('user_auth', 'success'))).to_be_visible()
