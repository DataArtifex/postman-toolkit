import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from dartfx.postmanapi import postman
from dartfx.socrata.socrata import SocrataServer
from dartfx.uscensus.uscensus import UsCensusApi, UsCensusCatalog


@pytest.fixture(scope="session", autouse=True)
def test_dir() -> Path:
    return Path(__file__).parent


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    dotenv_path = Path(__file__).parent / ".env"  # Construct path from current test file dir
    load_dotenv(dotenv_path=dotenv_path)


#
# POSTMAN
#
@pytest.fixture(scope="session")
def postman_api_key() -> str:
    key = os.environ.get("DARTFX_POSTMAN_API_KEY")
    if not key:  # fallback to POSTMAN_API_KEY
        key = os.environ.get("POSTMAN_API_KEY")
    if key is None:
        pytest.skip("DARTFX_POSTMAN_API_KEY or POSTMAN_API_KEY must be set")
    assert key is not None
    return key


@pytest.fixture(scope="module")
def postman_api(postman_api_key: str) -> postman.PostmanApi:
    api = postman.PostmanApi(api_key=postman_api_key)
    return api


@pytest.fixture(scope="module")
def postman_workspace(postman_api: postman.PostmanApi) -> postman.WorkspaceManager:
    workspace_id = os.environ.get("DARTFX_POSTMAN_WS")
    if workspace_id is None:
        pytest.skip("DARTFX_POSTMAN_WS is not set")
    ws = postman.WorkspaceManager(postman_api, workspace_id)
    return ws


#
# SOCRATA
#


@pytest.fixture(scope="module")
def socrata_cache_root(test_dir: Path) -> str:
    return os.path.join(test_dir, "socrata")


@pytest.fixture(scope="module")
def socrata_sfo_server(socrata_cache_root: str) -> SocrataServer:
    return SocrataServer(host="data.sfgov.org", disk_cache_root=socrata_cache_root)


@pytest.fixture(scope="module")
def socrata_yyc_server(socrata_cache_root: str) -> SocrataServer:
    return SocrataServer(host="data.calgary.ca", disk_cache_root=socrata_cache_root)


@pytest.fixture(scope="module")
def socrata_sfo_workspace(postman_api: postman.PostmanApi) -> postman.WorkspaceManager:
    workspace_id = os.environ.get("DARTFX_POSTMAN_WS_SOCRATA_SFO")
    if workspace_id is None:
        pytest.skip("DARTFX_POSTMAN_WS_SOCRATA_SFO is not set")
    ws = postman.WorkspaceManager(api=postman_api, id=workspace_id)
    return ws


#
# U.S. Census
#


@pytest.fixture(scope="module")
def uscensus_api() -> UsCensusApi:
    return UsCensusApi()


@pytest.fixture(scope="module")
def uscensus_server(api: UsCensusApi) -> UsCensusCatalog:
    return UsCensusCatalog(api=api)
