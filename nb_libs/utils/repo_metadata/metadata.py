from utils.gin import api as gin_api
from urllib import parse

def get_metadata_from_repo(head_url, token, repo_id, branch):

    pr = parse.urlparse(head_url)
    response = gin_api.get_repo_metadata(
            scheme=pr.scheme,
            domain=pr.netloc,
            token=token,
            repo_id=repo_id,
            branch=branch)
