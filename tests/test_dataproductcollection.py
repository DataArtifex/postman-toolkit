from datetime import datetime
from dartfx.postmanapi import postman

def test_create_dataproduct_101(postman_api, postman_workspace):
    # unicode prefixes: ⛁ ⛃ 🔢
    # More at https://www.compart.com/en/unicode/category/So
    collection_id = postman_workspace.create_collection(f'🔢 Data Product 101 {datetime.now().isoformat()}', 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json')
    assert collection_id
    collection = postman.DataProductCollectionManager(postman_api, collection_id)
    assert collection