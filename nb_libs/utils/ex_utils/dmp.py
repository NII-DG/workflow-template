import os
import json
from ..path import path as p


def is_for_parameter(dataset_structure:str):
    """データセット構造種別がfor_parameterかどうかを判定する

    Args:
        dataset_structure: データセット構造種別

    Returns:
        bool: データセット構造種別がfor_parameterかどうか
    """
    if dataset_structure == 'for_parameters':
        return True
    else:
        return False


def fetch_gin_monitoring_assigned_values():
    """dmp.jsonからcontentSize, workflowIdentifier, datasetStructureの値を取得する"""

    dmp_file_path = os.path.join(p.HOME_PATH, 'dmp.json')
    with open(dmp_file_path, mode='r') as f:
        dmp_json = json.load(f)
    assigned_values = {
        'workflowIdentifier': dmp_json['workflowIdentifier'],
        'contentSize': dmp_json['contentSize'],
        'datasetStructure': dmp_json['datasetStructure']
    }
    return assigned_values


def get_datasetStructure():
    assigned_values = fetch_gin_monitoring_assigned_values()
    return assigned_values['datasetStructure']
