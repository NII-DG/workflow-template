import json
import os

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


def write_it_setting(setting_json):
    with open(SETTING_PATH, mode='w') as f:
        json.dump(setting_json, f, indent=4)


def read_it_setting():
    with open(SETTING_PATH, mode='r') as f:
        return json.load(f)


def write_state(context):
    context.storage_state(path=STATE_PATH)
