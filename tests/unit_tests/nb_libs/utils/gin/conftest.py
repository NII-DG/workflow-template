import os
import pytest

from nb_libs.utils.gin.ssh import (
    SSH_PATH,
    __SSH_KEY_PATH as SSH_KEY_PATH,
    __SSH_PUB_KEY_PATH as SSH_PUB_KEY_PATH,
    __SSH_CONFIG as SSH_CONFIG,
)


@pytest.fixture()
def create_ssh_pub_key():
    os.makedirs(SSH_PATH, exist_ok=True)

    with open(SSH_PUB_KEY_PATH, 'w') as f:
        f.write('test_key')

    yield

    if os.path.exists(SSH_PUB_KEY_PATH):
        os.remove(SSH_PUB_KEY_PATH)


@pytest.fixture()
def delete_ssh_key():
    os.makedirs(SSH_PATH, exist_ok=True)

    if os.path.exists(SSH_KEY_PATH):
        os.remove(SSH_KEY_PATH)
    if os.path.exists(SSH_PUB_KEY_PATH):
        os.remove(SSH_PUB_KEY_PATH)

    yield

    if os.path.exists(SSH_KEY_PATH):
        os.remove(SSH_KEY_PATH)
    if os.path.exists(SSH_PUB_KEY_PATH):
        os.remove(SSH_PUB_KEY_PATH)


@pytest.fixture()
def delete_config():
    os.makedirs(SSH_PATH, exist_ok=True)

    if os.path.exists(SSH_CONFIG):
        os.remove(SSH_CONFIG)

    yield

    if os.path.exists(SSH_CONFIG):
        os.remove(SSH_CONFIG)
