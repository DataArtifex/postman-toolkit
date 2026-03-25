from dartfx.postman.socrata import SocrataPostmanPublisher, SocrataPostmanPublisherConfig


def test_publish_sfo_311(postman_workspace, socrata_sfo_server):
    config = SocrataPostmanPublisherConfig(name_prefix="🔢 TEST: ")
    publisher = SocrataPostmanPublisher(postman_api=postman_workspace.api, server=socrata_sfo_server, config=config)
    collection = publisher.publish_dataset(dataset_id="vw6y-z8j6", workspace_id=postman_workspace.id)
    assert collection
