from nb_libs.utils.dg_core.api import verify_metadata, get_verification_result

from tests.unit_tests.common.utils import MockResponse


def test_verify_metadata(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/dg_core/test_api.py::test_verify_metadata

    mock_obj = mocker.patch('requests.post', return_value=MockResponse(200))
    verify_metadata('https', 'test.domain', {'test_key': 'test_value'})
    mock_obj.assert_called_with(
        url='https://test.domain/validate',
        data='{"test_key": "test_value"}',
        headers={'content-type': 'application/json'}
    )


def test_get_verification_result(mocker):
    # pytest -v -s tests/unit_tests/nb_libs/utils/dg_core/test_api.py::test_get_verification_result

    mock_obj = mocker.patch('requests.get', return_value=MockResponse(200))
    get_verification_result('https', 'test.domain', 'req_id')
    mock_obj.assert_called_with('https://test.domain/req_id')
