"""
Classes and helpers to publish Socrata data products to Postman collections.
"""
import logging
from typing import Optional
from pydantic import BaseModel, Field

from . import templates
from dartfx.postmanapi import postman
from dartfx.postmanapi import postman_collection
from dartfx.socrata import SocrataServer, SocrataDataset

class SocrataPostmanPublisherConfig(BaseModel):
    """Configuration for SocrataPostmanPublisher."""
    # unicode prefixes: ⛁ ⛃ 🔢
    # More at https://www.compart.com/en/unicode/category/So
    name_prefix: str | None = Field(default=None)
    name_suffix: str | None = Field(default=None)
    
class SocrataPostmanPublisher(BaseModel):
    """Postman collection generator for Socrata datasets."""
    postman_api: postman.PostmanApi
    server: SocrataServer
    config: SocrataPostmanPublisherConfig = Field(default=SocrataPostmanPublisherConfig())

    model_config = {
        "arbitrary_types_allowed": True # for postman.PostmanApi
    }

    def publish_dataset(self, dataset_id:str, workspace_id:str|None=None, collection_id:str|None=None, config:Optional[SocrataPostmanPublisherConfig] = None) -> str:
        """Publish a dataset as a collection under an existing workspace.
        
        If collection_id is specified, its content will be replaced (but the collection id remains the same).
        Otherwise, workspace_id must be specified and a new collection will be created. 

        """

        # use default config if not specified
        if config is None:
            config = self.config

        # get the dataset
        dataset = SocrataDataset(server=self.server, id=dataset_id)
        generator = SocrataPostmanCollectionGenerator(dataset=dataset, config=config)
        generated_collection = generator.generate()
        generated_collection_data = generated_collection.to_dict()

        # instantiate collection manager
        if collection_id:
            # replace existing collection
            collection_id = self.postman_api.replace_collection(collection_id, generated_collection_data)
        elif workspace_id:
            # create a new collection or replace if same name already exists
            workspace_manager = postman.WorkspaceManager(self.postman_api, workspace_id)
            collection_id = workspace_manager.import_collection(generated_collection_data, replace=True)
        else:
            raise ValueError("Either a collection_id or workspace_id must be specified")

        return collection_id
    

class SocrataPostmanCollectionGenerator(BaseModel):
    dataset: SocrataDataset
    config: SocrataPostmanPublisherConfig = Field(default=SocrataPostmanPublisherConfig())
    
    def _add_query_request_parameters(self, request: postman_collection.Request):
        """Add query parameters that are common to all Socrata data requests.
        """
        if request.url is None or isinstance(request.url, str):
            request.url = postman_collection.URL()
        param = request.url.create_query_parameter('$select',description="The set of columns to be returned, similar to a SELECT in SQL. Default: All columns, equivalent to $select=* (which includes computed variables whose names start with @).", disabled=False)
        param.value = ",".join(self.dataset.get_visible_variables_names()) # make sure only visible variables are selected by default
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

        collection.info.description = templates.get_collection_description(markdown=dataset.get_markdown())

        # Metadata Folder
        metadata_folder = templates.get_metadata_folder()
        collection.item.append(metadata_folder)
        
        hvdnet_base_url = f"https://api.highvaluedata.net/datasets/socrata:{dataset.server.host}:{dataset.id}"

        # Metadata requests
        metadata_folder.item.append(templates.get_hvdnet_croissant_request(hvdnet_base_url))
        metadata_folder.item.append(templates.get_hvdnet_dcat_request(hvdnet_base_url))
        metadata_folder.item.append(templates.get_hvdnet_dcat_request(hvdnet_base_url, format='turtle'))
        metadata_folder.item.append(templates.get_hvdnet_ddi_codebook_request(hvdnet_base_url))
        metadata_folder.item.append(templates.get_hvdnet_ddi_cdif_request(hvdnet_base_url))
        metadata_folder.item.append(templates.get_hvdnet_ddi_cdif_request(hvdnet_base_url, format='turtle'))
        metadata_folder.item.append(templates.get_hvdnet_socrata_request(hvdnet_base_url))

        # DATA FOLDER
        data_folder = templates.get_data_folder(platform="socrata")
        collection.item.append(data_folder)

        # Query Data Request (JSON)
        item = postman_collection.Item()
        item.name = "Query Data (JSON)"
        item.request = item.create_request(f"https://{dataset.server.host}/resource/{dataset.id}.json")
        self._add_query_request_parameters(item.request)
        data_folder.item.append(item)

        # Query Data Request (CSV)
        item = postman_collection.Item()
        item.name = "Query Data (CSV)"
        item.request = item.create_request(f"https://{dataset.server.host}/resource/{dataset.id}.csv")
        self._add_query_request_parameters(item.request)
        data_folder.item.append(item)

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

        for language in languages:
            item = postman_collection.Item()
            item.name = language["name"]
            item.create_request(f"{hvdnet_base_url}/generate/{language['path']}")
            self._add_query_request_parameters(item.request)
            code_folder.item.append(item)

        # SQL FOLDER
        #sql_folder = templates.get_sql_folder()
        #collection.item.append(sql_folder)

        # AI FOLDER
        ai_folder = templates.get_ai_folder()
        collection.item.append(ai_folder)
        ai_folder.item.append(templates.get_markdown_request(hvdnet_base_url))

        # VISUALIZATION FOLDER
        #dv_folder = templates.get_visualization_folder()
        #collection.item.append(dv_folder)

        # COLLECTION VARIABLES
        collection.variable = []
        collection.variable.append(postman_collection.Variable(id="socrataId", value=dataset.id))
        collection.variable.append(postman_collection.Variable(id="hvdnetUri", value=f'socrata:{dataset.server.host}:{dataset.id}'))

        return collection
    

   