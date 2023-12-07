import os

from playwright.sync_api import sync_playwright, BrowserContext

from tests.integration_tests.common import notebook
from tests.integration_tests.common.path import JUPYTER_HUB_URL, SCREENSHOT_DIR
from tests.integration_tests.common.setting import read_it_setting
from tests.integration_tests.common.utils import get_browser_context, login_gakunin_rdm

FILE_PATH = 'notebooks/experiment/experiment.ipynb'


def test_experiment(prepare_exp_env):
    # pytest -v -s tests/integration_tests/notebooks/experiment/test_experiment.py::test_experiment

    with sync_playwright() as playwright:
        context = get_browser_context(playwright)
        try:
            experiment(context)
        finally:
            browser = context.browser
            context.close()
            browser.close()


def experiment(context: BrowserContext):
    it_setting = read_it_setting()
    page_url = f'{JUPYTER_HUB_URL}/user/{it_setting["user"]}/{it_setting["exp_server"]}/notebooks/WORKFLOWS/{FILE_PATH}'
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
    path = os.path.join(SCREENSHOT_DIR, 'experiment', 'experiment_01.png')
    page.screenshot(path=path, full_page=True)
    # セルの実行に成功したか確認
    cell = notebook.get_code_cell(page, 0)
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # 1つ目のセルの実行インデックス取得
    execute_index = notebook.get_execute_index(cell)

    # 実験フロー図を表示
    # セルの実行
    execute_index = execute_index + 1
    notebook.run_code_cell(page, 1, execute_index)
    # セル実行後のスクリーンショット保存
    path = os.path.join(SCREENSHOT_DIR, 'experiment', 'experiment_02.png')
    page.screenshot(path=path, full_page=True)
    # セルの実行に成功したか確認
    cell = notebook.get_code_cell(page, 1)
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)
