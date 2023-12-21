from nb_libs.utils.ex_utils.dmp import (
    is_for_parameter,
    fetch_gin_monitoring_assigned_values,
    get_datasetStructure
)

from tests.unit_tests.common.utils import FileUtil


def test_is_for_parameter():
    # pytest -v -s tests/unit_tests/nb_libs/utils/ex_utils/test_dmp.py::test_is_for_parameter

    assert is_for_parameter('for_parameters')
    assert not is_for_parameter('with_code')


def test_fetch_gin_monitoring_assigned_values(prepare_dmp_json):
    # pytest -v -s tests/unit_tests/nb_libs/utils/ex_utils/test_dmp.py::test_fetch_gin_monitoring_assigned_values

    dmp_file = FileUtil(prepare_dmp_json)
    dmp_file.create_json({
        'workflowIdentifier': 'test_workflow_identifier',
        'contentSize': 'test_content_size',
        'datasetStructure': 'test_dataset_structure',
    })

    assigned_values = fetch_gin_monitoring_assigned_values()

    assert assigned_values['workflowIdentifier'] == 'test_workflow_identifier'
    assert assigned_values['contentSize'] == 'test_content_size'
    assert assigned_values['datasetStructure'] == 'test_dataset_structure'


def test_get_datasetStructure(prepare_dmp_json):
    # pytest -v -s tests/unit_tests/nb_libs/utils/ex_utils/test_dmp.py::test_get_datasetStructure

    dmp_file = FileUtil(prepare_dmp_json)
    dmp_file.create_json({
        'workflowIdentifier': 'test_workflow_identifier',
        'contentSize': 'test_content_size',
        'datasetStructure': 'test_dataset_structure',
    })

    dataset_structure = get_datasetStructure()
    assert dataset_structure == 'test_dataset_structure'
