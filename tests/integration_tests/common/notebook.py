import re

from playwright.sync_api import Page, Locator, expect

CELL_CLASS_SUCCESS = 'cell-status-success'
CELL_CLASS_ERROR = 'cell-status-error'


def init_notebook(page: Page):
    """notebookの初期処理"""

    # 全セルのフリーズ解除
    page.get_by_title('unfreeze below all').click()

    # セルの折り畳み解除
    page.locator('#notebook').press('Control+Shift+ArrowRight')


def get_code_cell(page: Page, index: int) -> Locator:
    """コードセル取得"""
    return page.locator('.code_cell').nth(index)


def run_cell(page: Page):
    """選択中のセルの実行"""
    page.get_by_title('run cell, select below').click()


def wait_until_finished(page: Page, expected_index: int = None, timeout: int = 10 * 1000) -> int:
    """実行中のセルが終了するまで待機"""
    if expected_index is None:
        # 1つ目のセルでは共通メニューが表示されるまで待機
        cell = get_code_cell(page, 0)
        expect(cell.locator('.bk-input')).to_be_visible(timeout=timeout)
    else:
        # 2つ目以降のセルは"In [index]"が表示されるまで待機
        expect(page.locator('#notebook-container div').filter(has_text=f'In [{expected_index}]:').nth(2)).to_be_visible(timeout=timeout)


def get_execute_index(locate: Locator) -> int:
    """セルの実行回数を取得"""
    text = locate.locator('.input_prompt').inner_text()
    pattern = r'\[(.*)\]'
    match = re.search(pattern, text)
    return int(match.group(1))


def check_cell(cell: Locator, expected: str):
    """セルの実行結果が期待通りか確認する"""
    expect(cell).to_have_class(re.compile(expected))


def run_code_cell(
        page: Page,
        code_cell_index: int,
        execute_index: int = None,
        timeout: int = 10 * 1000,
):
    """セルを実行する

    Args:
        page (Page)             : notebookを開いているページ

        code_cell_index (int)   : コードセル番号

        execute_index (int)     : 実行インデックス(セル実行後に表示されるIn [index]のインデックス)

        timeout (int)           : タイムアウト時間(ms)
    """

    # セルを選択
    cell = get_code_cell(page, code_cell_index)
    cell.click()

    # すぐに実行すると出力の表示がうまくいかないことがあったので少し待機する
    page.wait_for_timeout(1000)

    # セルを実行
    run_cell(page)

    # 終了まで待機
    wait_until_finished(page, execute_index, timeout)
