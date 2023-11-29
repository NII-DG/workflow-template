from nb_libs.utils.repo_metadata.metadata import get_metadata_from_repo


def test_get_metadata_from_repo(mocker):
    # pytest -v -s tests/nb_libs/utils/repo_metadata/test_metadata.py::test_get_metadata_from_repo

    mocker.patch('nb_libs.utils.gin.api.get_repo_metadata')

    # エラーが発生しなければOK
    get_metadata_from_repo('http://test-domain/', 'token', 'repo_id', 'branch')
