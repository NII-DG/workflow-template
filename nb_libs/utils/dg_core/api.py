"""
DG-core APIの通信メソッド群
"""
from urllib import parse
import requests
import time
import json


def verify_metadata(scheme, netloc, ro_crate):
    sub_url = "validate"
    api_url = parse.urlunparse((scheme, netloc, sub_url, "", "", ""))
    headers = {'content-type': 'application/json'}

    return requests.post(url=api_url, data=json.dumps(ro_crate), headers=headers)

def get_verification_result(scheme, netloc, request_id):
    sub_url = f'{request_id}'
    api_url = parse.urlunparse((scheme, netloc, sub_url, "", "", ""))
    return requests.get(api_url)
