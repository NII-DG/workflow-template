import json

DMP = ""
def get_dmp():
    with open('../../../dmp.json') as f:
        DMP = json.load(f)
        return DMP

def get_dmp_from_outsystem(DMP_PATH):
    with open(DMP_PATH) as f:
        DMP = json.load(f)
        return DMP