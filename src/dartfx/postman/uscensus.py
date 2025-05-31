"""
Classes and helpers to publish Socrata data products to Postman collections.
"""
from dataclasses import dataclass, field

from . import templates
from dartfx.postmanapi import postman
from dartfx.postmanapi import postman_collection
from dartfx.uscensus import UsCensusApi, UsCensusCatalog,  UsCensusDataset, UsCensusMicrodataDataset, UsCensusAggregatedDataset

@dataclass
class UsCensusPostmanPublisherConfig():
    name_prefix: str = field(default=None)
    name_suffix: str = field(default=None)
    
class UsCensusPostmanPublisher():
    _postman_api: postman.PostmanApi
    _server: UsCensusCatalog
    _config: UsCensusPostmanPublisherConfig

    def __init__(self, api: postman.PostmanApi, server: UsCensusCatalog, config:UsCensusPostmanPublisherConfig = UsCensusPostmanPublisherConfig()):
        self._postman_api = api
        self._server = server
        self._config = config

    def publish_dataset(self, dataset_id:str, target_id:str, target_type="workspace", config:UsCensusPostmanPublisherConfig = None) -> str:
        """Publish a dataset as a collection under an existing workspace.
        
        If the target is a workspace, a new collection will be created. 
        If the target is a collection, its content will be replaced (but the collection id remains the same).

        """

        # use default config if not specified
        if config is None:
            config = self._config

        # get the dataset
        dataset = self._server.datasets.get(dataset_id)

        if dataset is None:
            raise ValueError(f"Dataset {dataset_id} not found")

        # instantiate collection manager
        if target_type == "workspace":
            # create a new collection
            collection_manager = postman.DataProductCollectionManager.factory(self._postman_api, target_id, dataset.id, dartfx_id=f'uscensus:{dataset.id}')
        elif target_type == "collection":
            # use existing collection
            collection_manager = postman.DataProductCollectionManager(self._postman_api, target_id)
        else:
            raise ValueError("target_type must be 'workspace' or 'collection'")

        # collection name
        name = f"{dataset.name} [{dataset.id}]"
        if config.name_prefix:
            name = f"{config.name_prefix}{name}"
        if config.name_suffix:
            name = f"{name}{config.name_suffix}"
        collection_manager.name = name

        # collection description
        description = ""
        if dataset.description:
            description = f"## Description\n{dataset.description}\n"
        collection_manager.description = description

        # collection level variables
        collection_manager.set_variable("host", dataset.server.host)
        collection_manager.set_variable("baseUrl", "https://{{host}}")
          
        return collection_manager.id
    

class PostmanCollectionGenerator():
    dataset: UsCensusDataset
    config: UsCensusPostmanPublisherConfig
    
    def __init__(self, dataset: UsCensusDataset, config:UsCensusPostmanPublisherConfig = UsCensusPostmanPublisherConfig()):
        self.dataset = dataset
        self.config = config

    def _add_query_request_parameters(self, request: postman_collection.Request):
        request.url.create_query_parameter('$select',description="The set of columns to be returned, similar to a SELECT in SQL. Default: All columns, equivalent to $select=*.", disabled=True)
        request.url.create_query_parameter('$where',None, "Filters the rows to be returned, similar to WHERE. No default value.", True)
        request.url.create_query_parameter('$order',None, "Column to order results on, similar to ORDER BY in SQL. Default is unspecified order.", True)
        request.url.create_query_parameter('$group',None, "Column to group results on, similar to GROUP BY in SQL. Default is no grouping.", True)
        request.url.create_query_parameter('$having',None, "Filters the rows that result from an aggregation, similar to HAVING. Default is no filter.", True)
        request.url.create_query_parameter('$limit',None, "Maximum number of results to return. Default is 1,000. Maximum is 50,000).", True)
        request.url.create_query_parameter('$offset',None, "Offset count into the results to start at, used for paging. Default is 0.", True)
        request.url.create_query_parameter('$q',None, "Performs a full text search for a value. Default is no search.", True)
        request.url.create_query_parameter('$query',None, "A full SoQL query string, all as one parameter.", True)
        request.url.create_query_parameter('$bom',None, "Prepends a UTF-8 Byte Order Mark to the beginning of CSV output. Default is False", True)
        return
        

    def generate(self) -> postman_collection.Collection:
        collection = postman_collection.Collection()
        dataset = self.dataset
        config = self.config

        # collection name
        name = f"{dataset.name} [{dataset.id}]"
        if config.name_prefix:
            name = f"{config.name_prefix}{name}"
        if config.name_suffix:
            name = f"{name}{config.name_suffix}"
        collection.info.name = name

        # collection description    
        description = ""
        if dataset.description:
            description = f"## Description\n{dataset.description}\n"
        collection.info.description = description

        # Metadata Folder
        metadata_folder = templates.get_metadata_folder()
        collection.item.append(metadata_folder)
        
        base_url = f"https://highvaluedata.net/api/datasets/uscensus:api.census.gov:{dataset.id}"

        # Metadata requests
        metadata_folder.item.append(templates.get_hvdnet_croissant_request(base_url))
        metadata_folder.item.append(templates.get_hvdnet_dcat_request(base_url))
        metadata_folder.item.append(templates.get_hvdnet_dcat_request(base_url, format='turtle'))
        metadata_folder.item.append(templates.get_hvdnet_ddi_codebook_request(base_url))
        metadata_folder.item.append(templates.get_hvdnet_ddi_cdif_request(base_url))
        metadata_folder.item.append(templates.get_hvdnet_ddi_cdif_request(base_url, format='turtle'))

        # DATA FOLDER
        data_folder = templates.get_data_folder()
        collection.item.append(data_folder)

        # Query Data Request (JSON)
        #item = postman_collection.Item()
        #item.name = "Query Data (JSON)"
        #item.request = item.create_request(f"https://{dataset.server.host}/resource/{dataset.id}.json")
        #self._add_query_request_parameters(item.request)
        #data_folder.item.append(item)


        # CODE FOLDER
        code_folder = templates.get_code_folder()
        collection.item.append(code_folder)

        languages = [
            {"name": "JQuery", "path": "jquery"},
            {"name": "Python Pandas", "path": "python-pandas"},
            {"name": "Powershell", "path": "powershell"},
            {"name": "R Socrata", "path": "r-socrata"},
            {"name": "SAS", "path": "sas"},
            {"name": "SODA Ruby", "path": "soda-ruby"},
            {"name": "SODA .NET", "path": "soda-dotnet"},
            {"name": "Stata", "path": "stata"},
        ]

        #for language in languages:
        #    item = postman_collection.Item()
        #    item.name = language["name"]
        #    item.create_request(f"{base_url}/code/{language['path']}")
        #    self._add_query_request_parameters(item.request)
        #    code_folder.item.append(item)

        # AI FOLDER
        ai_folder = templates.get_ai_folder()
        collection.item.append(ai_folder)

        # COLLECTION VARIABLES
        collection.variable = []
        collection.variable.append(postman_collection.Variable(id="platformId", value=dataset.id))
        collection.variable.append(postman_collection.Variable(id="hvdnetUri", value=f"uscensus:api.{dataset.id}"))

        return collection