import os
import sys

from playwright.sync_api import Playwright, Page

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
