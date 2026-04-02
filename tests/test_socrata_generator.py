import json
from pathlib import Path

from dartfx.postman.socrata import SocrataPostmanCollectionGenerator
from dartfx.postman.templates import initialize_socrata_workspace
from dartfx.postmanapi import postman
from dartfx.socrata.socrata import SocrataDataset, SocrataServer


def test_init_workspace(socrata_sfo_server: SocrataServer, postman_api: postman.PostmanApi) -> None:
    workspace = initialize_socrata_workspace(socrata_sfo_server, postman_api, workspace_type="personal")
    assert workspace
    assert workspace.data
    print(workspace.id)
    postman_api.delete_workspace(workspace.id)


def test_init_sfo_workspace(
    socrata_sfo_workspace: postman.WorkspaceManager,
    socrata_sfo_server: SocrataServer,
    postman_api: postman.PostmanApi,
) -> None:
    workspace = initialize_socrata_workspace(
        socrata_sfo_server, postman_api, workspace_type="personal", workspace_id=socrata_sfo_workspace.id
    )
    assert workspace


def test_generate_sfo_311(socrata_sfo_server: SocrataServer) -> None:
    dataset = SocrataDataset(server=socrata_sfo_server, id="vw6y-z8j6")
    assert dataset
    generator = SocrataPostmanCollectionGenerator(dataset=dataset)
    collection = generator.generate()
    assert collection
    collection_data = collection.model_dump(exclude_none=True)
    collection_json = json.dumps(collection_data, indent=4)
    output_dir = Path(__file__).resolve().parents[1] / "temp" / "test-outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "socrata_vw6y-z8j6.collection.json"
    output_path.write_text(collection_json)
    print(f"Saved generated collection to {output_path}")
