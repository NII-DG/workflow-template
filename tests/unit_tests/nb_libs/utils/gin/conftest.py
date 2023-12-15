import os
import pytest

from nb_libs.utils.gin.ssh import (
    SSH_PATH,
    __SSH_KEY_PATH as SSH_KEY_PATH,
    __SSH_PUB_KEY_PATH as SSH_PUB_KEY_PATH,
    __SSH_CONFIG as SSH_CONFIG,
)

from tests.unit_tests.common.utils import FileUtil, DirUtil


@pytest.fixture()
def create_ssh_pub_key():
    ssh_dir = DirUtil(SSH_PATH)
    ssh_dir.create()

    ssh_pub_key = FileUtil(SSH_PUB_KEY_PATH)
    ssh_pub_key.create('test_key')

    yield

    ssh_pub_key.delete()


@pytest.fixture()
def prepare_ssh_key():
    ssh_dir = DirUtil(SSH_PATH)
    ssh_dir.create()

    yield

    ssh_key = FileUtil(SSH_KEY_PATH)
    ssh_key.delete()
    ssh_pub_key = FileUtil(SSH_PUB_KEY_PATH)
    ssh_pub_key.delete()


@pytest.fixture()
def delete_config():
    ssh_dir = DirUtil(SSH_PATH)
    ssh_dir.create()

    config = FileUtil(SSH_CONFIG)
    config.delete()

    yield

    config.delete()
