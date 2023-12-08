import json
import os

from playwright.sync_api import BrowserContext

from .path import DATA_DIR

SETTING_PATH = os.path.join(DATA_DIR, 'it_setting.json')
STATE_PATH = os.path.join(DATA_DIR, 'it_state.json')


def init_setting():
    # テスト中に作成する設定ファイルを削除
    if os.path.exists(SETTING_PATH):
        os.remove(SETTING_PATH)
    if os.path.exists(STATE_PATH):
        os.remove(STATE_PATH)

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def write_it_setting(env_key: str, it_setting: dict):
    data = read_it_setting()
    data[env_key] = it_setting

    with open(SETTING_PATH, mode='w') as f:
        json.dump(data, f, indent=4)


def read_it_setting(env_key: str = None) -> dict:
    if not os.path.exists(SETTING_PATH):
        return {}

    with open(SETTING_PATH, mode='r') as f:
        it_setting = json.load(f)

    if env_key:
        if env_key in it_setting:
            return it_setting[env_key]
        else:
            return {}
    else:
        return it_setting


def write_state(context: BrowserContext):
    context.storage_state(path=STATE_PATH)
