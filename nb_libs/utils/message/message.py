import configparser


CONFIG_PATH = '../../../data/message.ini'
config_ini = configparser.ConfigParser()
config = config_ini.read(CONFIG_PATH, encoding='utf-8')


def get(section:str, key:str) -> str:
    """メッセージを取得する

    Args:
        section (str): section of message.ini
        key (str): key of message.ini
    Returns:
        str: message for user
    """
    return config[section][key]