from datetime import datetime
from functools import cache
import os

from src.dartfx.postman import postman


def get_api() -> postman.PostmanApi:
    api = postman.PostmanApi(os.environ.get('POSTMAN_API_KEY'))
    return api

@cache
def get_workspace(id="194dd33d-438d-47e1-ae69-e2ab5b414beb") -> postman.WorkspaceManager:
    ws = postman.WorkspaceManager(get_api(), id)
    return ws

def test_create_dataproduct_101():
    # unicode prefixes: ⛁ ⛃ 🔢
    # More at https://www.compart.com/en/unicode/category/So
    collection_id = get_workspace().create_collection(f'🔢 Data Product 101 {datetime.now().isoformat()}', 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json')
    collection = postman.DataProductCollectionManager(get_api(), collection_id)
    assert collection