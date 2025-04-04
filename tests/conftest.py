from dotenv import load_dotenv
from pathlib import Path
import os
import pytest

from dartfx.postmanapi import postman
from dartfx.socrata import SocrataServer


@pytest.fixture(scope="session", autouse=True)
def test_dir(): 
    return Path(__file__).parent

@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv_path = Path(__file__).parent / ".env"  # Construct path from current test file dir
    load_dotenv(dotenv_path=dotenv_path)

@pytest.fixture(scope="session")
def postman_api_key():
    key = os.environ.get('DARTFX_POSTMAN_API_KEY')
    if not key: # fallback to POSTMAN_API_KEY
        key = os.environ.get('POSTMAN_API_KEY')
    return key

@pytest.fixture(scope="module")
def postman_api(postman_api_key):
    api = postman.PostmanApi(api_key=postman_api_key)
    return api

@pytest.fixture(scope="module")
def postman_workspace(postman_api):
    id = os.environ.get('DARTFX_POSTMAN_WS')
    ws = postman.WorkspaceManager(postman_api, id)
    return ws

@pytest.fixture(scope="module")
def socrata_cache_root(test_dir):    
    return os.path.join(test_dir,'socrata')

@pytest.fixture(scope="module")
def socrata_sfo_server(socrata_cache_root):
    return SocrataServer(host="data.sfgov.org", disk_cache_root=socrata_cache_root)

@pytest.fixture(scope="module")
def socrata_yyc_server(socrata_cache_root):
    return SocrataServer(host="data.calgary.ca", disk_cache_root=socrata_cache_root)

