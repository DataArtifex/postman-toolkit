import logging
from typing import Optional, Union
from . import templates
from dartfx.mtnards import MtnaRdsServer, MtnaRdsDataProduct
from dartfx.postmanapi import PostmanApi, WorkspaceManager
from dartfx.postmanapi import postman_collection

from pydantic import BaseModel, Field, PrivateAttr


class MtnaRdsPostmanPublisherConfig(BaseModel):
    name_prefix: str | None = Field(default=None)
    name_suffix: str | None = Field(default=None)
    include_rds_collection: bool = Field(default=False) # includes the RDS generated Postman collection (requires management API key)

class MtnaRdsPostmanPublisher(BaseModel):
    postman_api: PostmanApi
    server: MtnaRdsServer
    config: MtnaRdsPostmanPublisherConfig = Field(default=MtnaRdsPostmanPublisherConfig())
    temp_workspace_id: str|None = None # if set can be used for importing temporary collections

    model_config = {
        "arbitrary_types_allowed": True # for postman.PostmanApi
    }
    ### MTNA Collection Publisher Methods ###
    def publish_rds_collection_to_workspace(self, catalog_id, data_product_id, workspace_id):
        """Publish a data product under an existing workspace"""
        collection = self.server.get_postman_collection(catalog_id, data_product_id)
        collection_id = self.postman_api.import_collection(workspace_id, collection)
        return collection_id

    def publish_rds_collection_to_collection(self, catalog_id, data_product_id, collection_uid, folder_uid=None, temp_workspace_id=None, create_root=True):
        """Published a data product under an existing collection or folder"""
        # initialize temporary workspace
        if not temp_workspace_id:
            if self.temp_workspace_id:
                temp_workspace_id = self.temp_workspace_id
            else:
                raise ValueError("No temporary workspace ID provided")
        # get the RDS collection
        rds_collection = self.server.get_postman_collection(catalog_id, data_product_id)
        # publish in a temporary workspace
        temp_collection_id = self.publish_rds_collection_to_workspace(catalog_id, data_product_id, temp_workspace_id)
        temp_collection = self.postman_api.get_collection(temp_collection_id)
        # create a target folder to host the RDS collection
        if create_root: # this should almost always be the case
            # this goes under the collection when folder_uid is not specified
            target_uid = self._create_folder_for_rds_collection(rds_collection, collection_uid, folder_uid)
        elif folder_uid:
            target_uid = folder_uid
        else:
            target_uid = collection_uid
        # move the RDS collection top folder to the target folder (or collection)
        uids = self._get_top_folder_uids(temp_collection)
        target_model = "folder" if folder_uid or create_root else "collection" # collection would be unusual but supported anyway
        self.postman_api.collection_folder_transfer(uids, target_uid, target_model=target_model)
        # delete the temporary collection
        self.postman_api.delete_collection(temp_collection_id)
        # return target folder
        return target_uid

    def _create_folder_for_rds_collection(self, rds_collection:dict, collection_id, folder_id=None, name_prefix=None, name=None, description=None):
        """Create a folder to host and replace the RDS collection.
        
        Args:
            rds_collection (dict): The RDS collection
            collection_id (str): The collection ID
            folder_id (str, optional): The parent folder ID if applicable. Defaults to None.
            name_prefix (str, optional): The folder name prefix. Defaults to None.
            name (str, optional): The folder name. Defaults to None.
            description (str, optional): The folder description. Defaults to None.

        Returns:
            str: The folder ID
        """
        # create the target folder under the collection root
        if not name:
            folder_name = rds_collection['info']['name']
            if name_prefix:
                folder_name = name_prefix + folder_name
        else:
            folder_name = name
        if not description:
            folder_description = rds_collection['info']['description']['content']
        else:
            folder_description = description
        # Create the folder
        folder_uid = self.postman_api.create_folder(collection_id, folder_name, folder_description, parent_id=folder_id)
        return folder_uid

    def _get_top_folder_uids(self, collection):
        # collect a Postman collection top folder identifiers
        uids = []
        for item in collection['collection']['item']:
            uids.append(item['uid'])
        return uids

    ### Generic Collection Publisher Methods ###

    def _add_regression_request_parameters(self, item:postman_collection.Item):
        item.request.url.create_query_parameter('dependent', None, "Required. The ID of the dependent variable.", False)
        item.request.url.create_query_parameter('independent', None, "Required. The ID of the independent variable.", False)
        item.request.url.create_query_parameter('count', "1", "Flag specifying whether the total row count should be returned along side the data.", True)
        item.request.url.create_query_parameter('format', None, "RDS can return a variety of JSON objects to plug into various java script charting libraries. Available formats: MTNA_RDS, MTNA_simple, MTNA_TABULATE, AMCHARTS, GCHARTS, PLOTLY_BAR, PLOTLY_BOXPLOT, PLOTLY_BUBBLE, PLOTLY_HIST, PLOTLY_PIE, PLOTLY_SCATTER.", True)
        item.request.url.create_query_parameter('groupby', None, "When computing a new variable using a function that depends on aggregation, the group by parameter can specify which columns to group by.", True)
        item.request.url.create_query_parameter('inject', "1", "Flag specifying to inject codes into the returned records.", True)
        item.request.url.create_query_parameter('limit', "50", "The maximum number of records to return.", True)
        item.request.url.create_query_parameter('metadata', "1", "Flag specifying if metadata should be returned along side the data.", True)
        item.request.url.create_query_parameter('offset', "0", "The record to start at.", True)
        item.request.url.create_query_parameter('orderby', None, "Allows the data to be reordered in ascending or descending order by column. Example: orderby=V1 DESC,V2 ASC.", True)
        item.request.url.create_query_parameter('weights', None, "The IDs of variables to use as weights in the resulting data.", True)
        item.request.url.create_query_parameter('where', None, "The where parameter allows filters to be applied to the data that will be returned. This follows a syntax similar to a SQL where clause.", True)

    
    def _add_select_request_parameters(self, item:postman_collection.Item):
        item.request.url.create_query_parameter('collimit', "50", "Limits the number of columns returned.", True)
        item.request.url.create_query_parameter('coloffset', "0", "Determines which column to start at.", True)
        item.request.url.create_query_parameter('cols', None, "Column names, regular expressions, keywords, variable groups, or concepts to select. Any of these can be excluded as well by prepending '~' to these syntaxes.", True)
        item.request.url.create_query_parameter('count', "0", "Flag specifying whether the total row count should be returned along side the data.", True)
        item.request.url.create_query_parameter('format', None, "RDS can return a variety of JSON objects to plug into various java script charting libraries. Available formats: MTNA_RDS, MTNA_simple, MTNA_TABULATE, AMCHARTS, GCHARTS, PLOTLY_BAR, PLOTLY_BOXPLOT, PLOTLY_BUBBLE, PLOTLY_HIST, PLOTLY_PIE, PLOTLY_SCATTER.", True)
        item.request.url.create_query_parameter('groupby', None, "When computing a new variable using a function that depends on aggregation, the group by parameter can specify which columns to group by.", True)
        item.request.url.create_query_parameter('inject', "1", "Flag specifying to inject codes into the returned records.", True)
        item.request.url.create_query_parameter('limit', "50", "The maximum number of records to return.", True)
        item.request.url.create_query_parameter('lock', None, "Column names, regular expressions, key words, variable groups, or concepts to lock. These will be returned first adn listed out in DataSetInformation that is returned on the DataSet.", True)
        item.request.url.create_query_parameter('metadata', "1", "Flag specifying if metadata should be returned along side the data.", True)
        item.request.url.create_query_parameter('offset', "0", "The record to start at.", True)
        item.request.url.create_query_parameter('orderby', None, "Allows the data to be reordered in ascending or descending order by column. Example: orderby=V1 DESC,V2 ASC.", True)
        item.request.url.create_query_parameter('weights', None, "The IDs of variables to use as weights in the resulting data.", True)
        item.request.url.create_query_parameter('where', None, "The where parameter allows filters to be applied to the data that will be returned. This follows a syntax similar to a SQL where clause.", True)


    def _add_tabulate_request_parameters(self, item:postman_collection.Item):
        item.request.url.create_query_parameter('dims', None, "Required. Categorical variables / columns to use as dimensions.", False)
        item.request.url.create_query_parameter('measure', None, "Columns to use as measures. Count is used by default.", True)
        item.request.url.create_query_parameter('count', "1", "Flag specifying whether the total row count should be returned along side the data.", True)
        item.request.url.create_query_parameter('format', None, "RDS can return a variety of JSON objects to plug into various java script charting libraries. Available formats: MTNA_RDS, MTNA_simple, MTNA_TABULATE, AMCHARTS, GCHARTS, PLOTLY_BAR, PLOTLY_BOXPLOT, PLOTLY_BUBBLE, PLOTLY_HIST, PLOTLY_PIE, PLOTLY_SCATTER.", True)
        item.request.url.create_query_parameter('groupby', None, "When computing a new variable using a function that depends on aggregation, the group by parameter can specify which columns to group by.", True)
        item.request.url.create_query_parameter('inject', "1", "Flag specifying to inject codes into the returned records.", True)
        item.request.url.create_query_parameter('limit', "50", "The maximum number of records to return.", True)
        item.request.url.create_query_parameter('metadata', "1", "Flag specifying if metadata should be returned along side the data.", True)
        item.request.url.create_query_parameter('offset', "0", "The record to start at.", True)
        item.request.url.create_query_parameter('orderby', None, "Allows the data to be reordered in ascending or descending order by column. Example: orderby=V1 DESC,V2 ASC.", True)
        item.request.url.create_query_parameter('totals', "1", "Flag specifying whether subtotals should be returned along side the data.", True)
        item.request.url.create_query_parameter('weights', None, "The IDs of variables to use as weights in the resulting data.", True)
        item.request.url.create_query_parameter('where', None, "The where parameter allows filters to be applied to the data that will be returned. This follows a syntax similar to a SQL where clause.", True)


    def _add_snippet_generator_parameters(self, item:postman_collection.Item):
        item.request.url.create_query_parameter('library', "rds-js", "The code generator library to use: rds-js, rds-python, rds-r", False)
        item.request.url.create_query_parameter('version', "1.0.0-ALPHA", "the library's version (see snippet generators information endpoint)", False)

    def publish_catalog(self, catalog_id, workspace_id):
        collection = postman_collection.Collection()
        raise NotImplementedError("Publishing a catalog is not implemented yet.")
        return collection


    def publish_data_product(self, catalog_id:str, data_product_id:str, workspace_id:str|None=None, collection_id:str|None=None, config:Optional[MtnaRdsPostmanPublisherConfig] = None) -> str:
        """Publish a data product as a collection under an existing workspace.
        
        If collection_id is specified, its content will be replaced (but the collection id remains the same).
        If both workspace_id and collection_id are provided, collection_id takes precedence, and the collection will be replaced.
        Otherwise, workspace_id must be specified and a new collection will be created.

        """
        # Ensure at least one of workspace_id or collection_id is provided
        if not workspace_id and not collection_id:
            raise ValueError("Either a workspace_id or collection_id must be provided")

        # use default config if not specified
        if config is None:
            config = self.config

        catalog = self.server.get_catalog_by_id(catalog_id)
        if catalog is None:
            raise ValueError(f"Catalog {catalog_id} not found")
        data_product = catalog.get_data_product_by_id(data_product_id)
        if data_product is None:
            raise ValueError(f"Data product {data_product_id} not found")

        # create collection
        collection = postman_collection.Collection()
        
        # name    
        name = f"{config.name_prefix or ''}{data_product.name} [{data_product._catalog.id}/{data_product.id}]{config.name_suffix or ''}"
        collection.info.name = name
        
        # description
        collection.info.description = templates.get_collection_description(markdown=data_product.get_markdown())
    
        # populate collection items
        self._publish_data_product_in_item(data_product, config, collection.item)

        # COLLECTION VARIABLES
        collection.variable = []
        collection.variable.append(postman_collection.Variable(id="platformType", value='mtnards'))
        collection.variable.append(postman_collection.Variable(id="mtnardsCatalogId", value=data_product.catalog_id))
        collection.variable.append(postman_collection.Variable(id="mtnardsDataProductId", value=data_product.id))
        collection.variable.append(postman_collection.Variable(id="hvdnetUri", value=f'mtnards:{self.server.hostname}:{data_product.catalog_id}:{data_product.id}'))

        # import the collection
        collection_dict = collection.to_dict()
        if collection_id:
            # replace existing collection
            collection_id = self.postman_api.replace_collection(collection_id, collection_dict)
        elif workspace_id:
            # create a new collection or replace if same name already exists
            workspace_manager = WorkspaceManager(self.postman_api, workspace_id)
            collection_id = workspace_manager.import_collection(collection_dict, replace=True)
        else:
            raise ValueError("Either a collection_id or workspace_id must be specified")

        return collection_id

    def _publish_data_product_in_item(self, data_product: MtnaRdsDataProduct, config: MtnaRdsPostmanPublisherConfig, item: list[Union[postman_collection.Item,postman_collection.ItemGroup]]) -> None:
        
        # initialize
        hvdnet_base_url = f"https://api.highvaluedata.net/datasets/mtnards:{self.server.hostname}:{data_product.catalog_id}:{data_product.id}"

        # METADATA FOLDER
        metadata_folder = templates.get_metadata_folder()
        metadata_folder.name = "Metadata (standards)"
        item.append(metadata_folder)
        
        # Metadata requests (HVDNet)
        metadata_folder.item.append(templates.get_hvdnet_croissant_request(hvdnet_base_url))
        metadata_folder.item.append(templates.get_hvdnet_dcat_request(hvdnet_base_url))
        metadata_folder.item.append(templates.get_hvdnet_dcat_request(hvdnet_base_url, format='turtle'))
        metadata_folder.item.append(templates.get_hvdnet_ddi_codebook_request(hvdnet_base_url))
        metadata_folder.item.append(templates.get_hvdnet_ddi_cdif_request(hvdnet_base_url))
        metadata_folder.item.append(templates.get_hvdnet_ddi_cdif_request(hvdnet_base_url, format='turtle'))

        # Metadata requests (RDS)
        metadata_rds_folder = templates.get_mtnards_metadata_folder()
        item.append(metadata_rds_folder)

        metadata_rds_request_item = postman_collection.Item()
        metadata_rds_request_item.name = "Overview"
        metadata_rds_request_item.description = "Get data product metadata"
        metadata_rds_request_item.create_request(f"{data_product.metadata_api_url}")
        metadata_rds_folder.item.append(metadata_rds_request_item)

        metadata_rds_request_item = postman_collection.Item()
        metadata_rds_request_item.name = "Variables"
        metadata_rds_request_item.description = "Get the variables of a specific data product. Returns a list of summary objects about any variables that are used in the specified data product. These summaries contain both the variable URI and ID, which can be used to get more detailed information about the variable."
        metadata_rds_request_item.create_request(f"{data_product.metadata_api_url}/variables")
        metadata_rds_folder.item.append(metadata_rds_request_item)

        metadata_rds_request_item = postman_collection.Item()
        metadata_rds_request_item.name = "Variable Details"
        metadata_rds_request_item.description = "Returns a variable with more detail than what is provided by the summary object. If the variable has a classification, its URI should be available on the variable which can be used to retrieve the classification."
        metadata_rds_request_item.create_request(f"{data_product.metadata_api_url}/variable/:id")
        metadata_rds_request_item.request.url.create_variable(key="id", description="The ID or URI of the variable.")
        metadata_rds_folder.item.append(metadata_rds_request_item)

        metadata_rds_request_item = postman_collection.Item()
        metadata_rds_request_item.name = "Classifications"
        metadata_rds_request_item.description = "Get the classifications of a specific data product. Returns a list of summary objects about any classifications that are used in the specified data product.These summary objects hold the classification uri and classification id (among other things) either of which can be used to get more information about the classification."
        metadata_rds_request_item.create_request(f"{data_product.metadata_api_url}/classifications")
        metadata_rds_folder.item.append(metadata_rds_request_item)

        metadata_rds_request_item = postman_collection.Item()
        metadata_rds_request_item.name = "Classification Details"
        metadata_rds_request_item.description = "Returns the specified classification with more detail than the summary. Codes will be excluded from this object, the idea being that this classification could have a large amount of codes and clients can build these codes up through the used of the codes endpoints."
        metadata_rds_request_item.create_request(f"{data_product.metadata_api_url}/classification/:id")
        metadata_rds_request_item.request.url.create_variable(key="id", description="The ID or URI of the classification.")
        metadata_rds_folder.item.append(metadata_rds_request_item)

        metadata_rds_request_item = postman_collection.Item()
        metadata_rds_request_item.name = "Classification Codes"
        metadata_rds_request_item.description = "This allows the client to page through or build up the codes of the classification as desired."
        metadata_rds_request_item.create_request(f"{data_product.metadata_api_url}/classification/:id/codes")
        metadata_rds_request_item.request.url.create_variable(key="id", description="The ID or URI of the classification.")
        metadata_rds_folder.item.append(metadata_rds_request_item)

        metadata_rds_request_item = postman_collection.Item()
        metadata_rds_request_item.name = "Changelog"
        metadata_rds_request_item.description = "Get the change log for a data product. This will be an array of ChangeLog entries ordered with the latest first. If there is no changelog available an empty array will be returned."
        metadata_rds_request_item.create_request(f"{data_product.metadata_api_url}/changelog")
        metadata_rds_folder.item.append(metadata_rds_request_item)

        # DATA FOLDER
        data_folder = templates.get_data_folder(platform="mtnards")
        item.append(data_folder)
        # select
        request_item = templates.get_mtnards_select_request(data_product)
        self._add_select_request_parameters(request_item)
        data_folder.item.append(request_item)
        # tabulate
        request_item = templates.get_mtnards_tabulate_request(data_product)
        self._add_tabulate_request_parameters(request_item)
        data_folder.item.append(request_item)
        # regression
        request_item = templates.get_mtnards_regression_request(data_product)
        self._add_regression_request_parameters
        data_folder.item.append(request_item)

        # CODE FOLDER
        code_folder = templates.get_code_folder(platform="mtnards")
        item.append(code_folder)

        code_request_item = postman_collection.Item()
        code_request_item.name = "List generators"
        code_request_item.description = "Snippet generators can be used to create calls in external libraries that when run, will get the data set represented by a provided query. This end point exposes the available snippet generators and their details."
        code_request_item.create_request(f"{data_product._catalog._server.api_url}/snippet/generators")
        code_folder.item.append(code_request_item)

        code_request_item = postman_collection.Item()
        code_request_item.name = "Select data generator"
        code_request_item.description = "Generates a snippet of code in the requested library to recreate the provided select query."
        code_request_item.create_request(f"{data_product.code_generators_api_url}/select")
        self._add_snippet_generator_parameters(code_request_item)
        self._add_select_request_parameters(code_request_item)
        code_folder.item.append(code_request_item)

        code_request_item = postman_collection.Item()
        code_request_item.name = "Tabulation generator"
        code_request_item.description = "Generates a snippet of code in the requested library to recreate the provided tabulate query."
        code_request_item.create_request(f"{data_product.code_generators_api_url}/tabulate")
        self._add_snippet_generator_parameters(code_request_item)
        self._add_tabulate_request_parameters(code_request_item)
        code_folder.item.append(code_request_item)

        # AI FOLDER
        ai_folder = templates.get_ai_folder()
        item.append(ai_folder)
        ai_folder.item.append(templates.get_markdown_request(hvdnet_base_url))

        # MTNA FOLDER
        if config.include_rds_collection:
            if self.server.api_key:
                try:
                    mtna_collection_data = data_product.get_postman_collection()
                    if mtna_collection_data:
                        # convert to a postman collection
                        mtna_collection = postman_collection.Collection.from_dict(mtna_collection_data)
                        # Remove the 'id' attribute on the requests, otherwise this fails to import through the Postman API
                        # This does not seem to be an issue with request event scripts
                        for mtna_folders in mtna_collection.item: # iterate the top level folders
                            for mtna_request in mtna_folders.item:
                                mtna_request.id = None
                        # create and populate folder
                        mtna_folder = templates.get_mtnards_collection_folder(markdown=mtna_collection.info.description.content)
                        mtna_folder.item = mtna_collection.item
                        # add folder to collection
                        item.append(mtna_folder)
                except Exception as e:
                    logging.warning(f"Failed to get MTNA RDS collection: {e}")
            else:
                logging.warning("No API key provided. Skipping MTNA RDS collection.")

