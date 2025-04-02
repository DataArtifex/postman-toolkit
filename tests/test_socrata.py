
import os
from dartfx.socrata import SocrataServer, SocrataDataset
from dartfx.postman.socrata import SocrataPostmanCollectionGenerator
import pytest


@pytest.fixture(scope="module")
def cache_root(test_dir):    
    return os.path.join(test_dir,'socrata')

@pytest.fixture(scope="module")
def socrata_sfo(cache_root):
    return SocrataServer(host="data.sfgov.org", disk_cache_root=cache_root)

@pytest.fixture(scope="module")
def socrata_yyc(cache_root):
    return SocrataServer(host="data.calgary.ca", disk_cache_root=cache_root)

def test_generate_sfo_311(socrata_sfo):
    dataset = SocrataDataset(server=socrata_sfo, id="vw6y-z8j6")
    assert dataset
    generator = SocrataPostmanCollectionGenerator(dataset=dataset)
    collection = generator.generate()
    print(collection.model_dump(exclude_none=True))
    assert collection
