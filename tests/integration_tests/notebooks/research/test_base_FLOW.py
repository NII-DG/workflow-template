import os

from playwright.sync_api import sync_playwright, BrowserContext

from tests.integration_tests.common import notebook
from tests.integration_tests.common.path import JUPYTER_HUB_URL, SCREENSHOT_DIR
from tests.integration_tests.common.setting import read_it_setting
from tests.integration_tests.common.utils import get_browser_context, login_gakunin_rdm

FILE_PATH = 'notebooks/research/base_FLOW.ipynb'


def test_base_flow(prepare_res_env):
    # pytest -v -s tests/integration_tests/notebooks/research/test_base_FLOW.py::test_base_flow

    with sync_playwright() as playwright:
        context = get_browser_context(playwright)
        try:
            base_flow(context)
        finally:
            browser = context.browser
            context.close()
            browser.close()


def base_flow(context: BrowserContext):
    it_setting = read_it_setting()
    page_url = f'{JUPYTER_HUB_URL}/user/{it_setting["user"]}/{it_setting["res_server"]}/notebooks/WORKFLOWS/{FILE_PATH}'
    page = context.new_page()
    page.goto(page_url)

    # GakuNin RDMへのログイン
    login_gakunin_rdm(page)

    # ノートブックの初期処理
    notebook.init_notebook(page)

    # 共通メニュー
    # セルの実行
    notebook.run_code_cell(page, 0, None)
    # セル実行後のスクリーンショット保存
    path = os.path.join(SCREENSHOT_DIR, 'research', 'base_flow_01.png')
    page.screenshot(path=path, full_page=True)
    # セルの実行に成功したか確認
    cell = notebook.get_code_cell(page, 0)
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # 1つ目のセルの実行インデックス取得
    execute_index = notebook.get_execute_index(cell)

    # 研究フロー図を表示
    # セルの実行
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 1, execute_index)
    # セル実行後のスクリーンショット保存
    path = os.path.join(SCREENSHOT_DIR, 'research', 'base_flow_02.png')
    page.screenshot(path=path, full_page=True)
    # セルの実行に成功したか確認
    cell = notebook.get_code_cell(page, 1)
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)
