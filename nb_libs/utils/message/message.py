import configparser
import os
from ..path import path


CONFIG_PATH = os.path.join(path.DATA_PATH, 'message.ini')
config = configparser.ConfigParser()
config.read(CONFIG_PATH, encoding='utf-8')


def get(section:str, option:str) -> str:
    """メッセージを取得する

    Args:
        section (str): section of message.ini
        key (str): key of message.ini
    Returns:
        str: message for user
    """

    return config[section][option]