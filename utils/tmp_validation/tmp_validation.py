""" .tmp.validationフォルダ配下の操作クラス
"""

import os
import subprocess
import shutil
import json

TMP_VALIDATION_PATH = '.tmp/validation'
VALIDATION_RESULTS_PATH = 'validation_results'
RO_CRATE_FILE_NAME = 'ro_crate.json'
ENTITY_IDS_FILE_NAME = 'entity_ids.json'
RESULTS_FILE_NAME = 'results.json'
REQUEST_ID_FILE_NAME = 'request_id.txt'


def fetch_validation_result_path() -> str:
    """return TMP_VALIDATION_PATH
    RETURN
    -----------------
    VALIDATION_RESULTS_PATH : str
        Description : Path to a directory to temporarily store verification results.
    """
    return VALIDATION_RESULTS_PATH

def fetch_request_id_file_path() -> str:
    """return path to .tmp/validation/requestID.txt
    RETURN
    -----------------
    request_id_file_path : str
        Description : Path to the file that manages the Request ID issued by the Verification Service.
    """
    request_id_file_path = os.path.join(TMP_VALIDATION_PATH, REQUEST_ID_FILE_NAME)
    return request_id_file_path

def fetch_validation_results_file_path() -> str:
    """return path to .tmp/validation/{request_id}/{RESULTS_FILE_NAME}
    RETURN
    -----------------
    validation_results_file_path : str
        Description : path to .tmp/validation/{request_id}/{RESULTS_FILE_NAME}
    """
    validation_results_file_path = os.path.join(get_tmp_result_folder_path(), RESULTS_FILE_NAME)
    return validation_results_file_path

def get_tmp_result_folder_path():
    """return path to a directory to temporarily store verification results
    RETURN
    -----------------
    tmp_result_folder_path : str
        Description : path to a directory to temporarily store verification results
    """
    tmp_result_folder_path = os.path.join(TMP_VALIDATION_PATH, get_request_id())
    return tmp_result_folder_path

def save_request_id(request_id):
    """write the request ID
    RETURN
    -----------------
    """
    os.chdir(os.environ['HOME'])
    file_path = fetch_request_id_file_path()
    if not os.path.exists(TMP_VALIDATION_PATH):
        os.makedirs(TMP_VALIDATION_PATH)
    with open(file_path, 'w') as f:
        f.write(request_id)

def get_request_id():
    """get request ID
    RETURN
    -----------------
    request_id : str
        Description : Request ID obtained from the response of the verification request API
    """
    os.chdir(os.environ['HOME'])
    file_path = fetch_request_id_file_path()
    with open(file_path, 'r') as f:
        request_id = f.read()
    return request_id

def save_verification_results(result):
    """write the verification results in .tmp/validation/{request_id}
    RETURN
    -----------------
    """
    os.chdir(os.environ['HOME'])
    request_id = get_request_id()
    tmp_result_folder = get_tmp_result_folder_path()
    if not os.path.exists(tmp_result_folder):
        os.makedirs(tmp_result_folder)
    tmp_files = [
        [result['request']['roCrate'], os.path.join(tmp_result_folder, RO_CRATE_FILE_NAME)],
        [result['request']['entityIds'], os.path.join(tmp_result_folder, ENTITY_IDS_FILE_NAME)],
        [result['results'], os.path.join(tmp_result_folder, RESULTS_FILE_NAME)]
    ]
    for file in tmp_files:
        with open(file[1], 'w', encoding='utf-8') as f:
            json.dump(file[0], f, indent=4, ensure_ascii=False)

def operate_validation_results(need_sync):
    """If synchronizing verification results, move temporary verification results to VALIDATION_RESULTS_PATH and delete temporary verification-related files.
    If not synchronizing, delete the temporary validation-related files.
    RETURN
    -----------------
    """
    if need_sync == False:
        delete_verification_results_and_request_id()
    elif need_sync == True:
        src = get_tmp_result_folder_path()
        dst = VALIDATION_RESULTS_PATH
        if not os.path.exists(VALIDATION_RESULTS_PATH):
            os.makedirs(VALIDATION_RESULTS_PATH)
        for file in os.listdir(src):
            print(os.path.join(src, file))
            print(os.path.join(dst, file))
            shutil.copyfile(os.path.join(src, file), os.path.join(dst, file))

def delete_verification_results_and_request_id():
    """delete temporary validation-related files(.tmp/validation/{request_id}/*, .tmp/request_id.txt)
    RETURN
    -----------------
    """
    os.chdir(os.environ['HOME'])
    request_id = get_request_id()
    tmp_result_folder = get_tmp_result_folder_path()
    if os.path.exists(tmp_result_folder):
        shutil.rmtree(tmp_result_folder)
    request_id_file_path = fetch_request_id_file_path()
    if os.path.exists(request_id_file_path):
        os.remove(request_id_file_path)
