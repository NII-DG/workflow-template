from nb_libs.utils.message import message


def test_get():
    # pytest -v -s tests/unit_tests/nb_libs/utils/message/test_message.py::test_get

    msg = message.get('menu', 'select')
    assert msg
