from datetime import datetime
from functools import cache
import os

import pytest
from src.dartfx.postman import postman


def get_api() -> postman.PostmanApi:
    api = postman.PostmanApi(os.environ.get('POSTMAN_API_KEY'))
    return api

@cache
def get_workspace(id="194dd33d-438d-47e1-ae69-e2ab5b414beb") -> postman.WorkspaceManager:
    ws = postman.WorkspaceManager(get_api(), id)
    return ws
@cache
def get_collection(index=0) -> postman.CollectionManager:
    ws = get_workspace()
    collection_stub = ws.collections[index]
    collection = postman.CollectionManager(get_api(), collection_stub['id'])
    return collection

def test_workspace_properties():
    ws = get_workspace()
    assert ws.id is not None
    assert ws.name is not None
    assert ws.type is not None
    assert ws.visibility is not None
    assert ws.created_by is not None
    assert ws.updated_by is not None
    assert ws.created_at is not None
    assert isinstance(ws.created_at, datetime)
    assert ws.updated_at is not None

def test_workspace_tags():
    ws = get_workspace()
    assert isinstance(ws.tags, list)

def test_workspace_global_variables():
    ws = get_workspace()
    assert isinstance(ws.global_variables, list)

def test_collection_properties():
    collection = get_collection()
    assert collection.info is not None
    assert collection.id == collection.info.get('_postman_id')

@pytest.mark.skip(reason="reactivate as needed")
def test_create_delete_workspace():
    api = get_api()
    id = api.create_workspace('test_workspace',"personal")
    api.delete_workspace(id)
