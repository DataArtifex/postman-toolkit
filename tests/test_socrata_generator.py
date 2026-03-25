import json
from dartfx.socrata import SocrataDataset
from dartfx.postman.templates import initialize_socrata_workspace
from dartfx.postman.socrata import SocrataPostmanCollectionGenerator
import os


def test_init_workspace(socrata_sfo_server, postman_api):
    workspace = initialize_socrata_workspace(socrata_sfo_server, postman_api, workspace_type="personal")
    assert workspace
    assert workspace.data
    print(workspace.id)
    postman_api.delete_workspace(workspace.id)


def test_init_sfo_workspace(socrata_sfo_workspace, socrata_sfo_server, postman_api):
    workspace = initialize_socrata_workspace(
        socrata_sfo_server, postman_api, workspace_type="personal", workspace_id=socrata_sfo_workspace.id
    )
    assert workspace


def test_generate_sfo_311(socrata_sfo_server, test_dir):
    dataset = SocrataDataset(server=socrata_sfo_server, id="vw6y-z8j6")
    assert dataset
    generator = SocrataPostmanCollectionGenerator(dataset=dataset)
    collection = generator.generate()
    assert collection
    collection_json = collection.model_dump(exclude_none=True)
    collection_json = json.dumps(collection_json, indent=4)
    print(collection_json)
    # save to file
    with open(os.path.join(test_dir, "socrata_vw6y-z8j6.collection.json"), "w") as f:
        f.write(collection_json)
