from requests.exceptions import RequestException

from nb_libs.utils.aws.s3 import access_s3_url
from nb_libs.utils.message import message

from tests.unit_tests.common.utils import MockResponse


def test_access_s3_url(mocker):
    # pytest -v -s tests/nb_libs/utils/aws/test_s3.py::test_access_s3_url

    mocker.patch('requests.head', return_value=MockResponse(200))
    msg = access_s3_url('')
    assert msg == ''

    mocker.patch('requests.head', return_value=MockResponse(404))
    msg = access_s3_url('')
    assert msg == message.get('from_repo_s3', 'wrong_or_private')

    mocker.patch('requests.head', return_value=MockResponse(500))
    msg = access_s3_url('')
    assert msg == message.get('from_repo_s3', 'unexpected')

    mocker.patch('requests.head', side_effect=RequestException())
    msg = access_s3_url('')
    assert msg == message.get('from_repo_s3', 'wrong_or_private')
