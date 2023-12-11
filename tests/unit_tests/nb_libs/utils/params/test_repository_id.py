from nb_libs.utils.params.repository_id import get_repo_id


def test_get_repo_id(create_repo_id_file):
    # pytest -v -s tests/unit_tests/nb_libs/utils/params/test_repository_id.py::test_get_repo_id

    repo_id = get_repo_id()
    assert repo_id == 'test_repo_id'
