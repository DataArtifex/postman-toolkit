"""
Classes and helpers to publish Socrata data products to Postman collections.

"""
from dataclasses import dataclass, field
import json
import logging
import os
import requests
from typing import Optional

from dartfx.postman import postman
from dartfx.postman import postman_collection


class SocrataApiError(Exception):
    """Custom exception for Socrata API errors."""

    def __init__(self, message, url, status_code=None, response=None):
        super().__init__(message)
        self.message = message
        self.url = url
        self.status_code = status_code
        self.response = response

    def __str__(self):
        base_message = f"SocrataApiError: {self.message}"
        if self.status_code is not None:
            base_message += f" (Status Code: {self.status_code})"
        if self.response is not None:
            base_message += f" (Response: {self.response})"
        return base_message


@dataclass
class SocrataServer:
    host: str
    disk_cache_root: Optional[str] = field(default=None)
    in_memory_cache: dict = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        self.memory_cache = {}

    @property
    def disk_cache_dir(self):
        if self.disk_cache_root:
            if os.path.isdir(self.disk_cache_root):
                if self.disk_cache_root:
                    path = os.path.join(self.disk_cache_root, self.host)
                    os.makedirs(path, exist_ok=True)
                    return path
            else:
                raise ValueError(f"Cache root directory does not exist: {self.disk_cache_root}")

    def get_dataset_info(self, dataset_id, refresh=False):
        # check if in memory cache
        if dataset_id in self.memory_cache and not refresh:
            return self.memory_cache[dataset_id]
        # init local file if cache is enabled
        file_name = f"{dataset_id}.json"
        if self.disk_cache_dir:
            file_path = os.path.join(self.disk_cache_dir, file_name)
        if self.disk_cache_dir and os.path.isfile(file_path) and not refresh:
            # load from disk cache
            logging.debug(f"Loading from disk cache {file_path}")
            with open(file_path) as f:
                data = json.load(f)
                self.memory_cache[dataset_id] = data
                return data
        else:
            # retrieve from server
            url = f"https://{self.host}/api/views/{file_name}"
            logging.debug(f"GET {url}")
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                # save to disk cache if enabled
                if self.disk_cache_dir: # save to local cache if enabled
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=4)
                # save to in memory cache
                self.memory_cache[dataset_id] = data
                return data
            else:
                raise SocrataApiError("Error getting dataset info", url, r.status_code, r.text)

@dataclass
class SocrataDataset:
    server: SocrataServer
    id: str
    _data: dict = field(init=False, repr=False)
    _variables: list["SocrataVariable"] = field(init=False, repr=False, default_factory=list)

    def __post_init__(self):
        self._data = self.server.get_dataset_info(self.id)
        if self.asset_type != 'dataset':
            raise ValueError(f"Unexpected asset type: {self.asset_type}. Must be 'dataset'.")

    @property   
    def data(self):
        return self._data


    @property
    def asset_type(self):
        return self._data.get("assetType")

    @property
    def description(self):
        return self._data.get("description")

    @property
    def name(self):
        return self._data.get("name")
    
    @property
    def variables(self) -> list["SocrataVariable"]:
        if not self._variables:
            self._variables = []
            for index, column in enumerate(self._data["columns"]):
                self._variables.append(SocrataVariable(self, index))
        return self._variables

    def get_variable_count(self, exclude_hidden=True, exclude_deleted=True, exclude_computed=True) -> int:
        count = 0
        for variable in self.variables:
            if variable.is_hidden and exclude_hidden:
                continue
            else:
                if variable.is_deleted and exclude_deleted:
                    continue
                if variable.is_computed and exclude_computed:
                    continue
            count += 1
        return count
    
    def get_record_count(self):
        count = self.data["columns"][0]["cachedContents"]["count"]
        return count

@dataclass
class SocrataVariable:
    """Helper class to process/use Socarata dataset variables (columns).

    This uses a standard terminology and hides Socrata properietary attribute names.

    """
    dataset: SocrataDataset
    index: int

    def __post_init__(self):
        pass

    @property
    def cached_content(self):
        return self.data.get('cachedContents')

    @property
    def data(self):
        return self.dataset._data["columns"][self.index]

    @property
    def id(self):
        """The variable is which is always a number"""
        return self.data["id"]

    @property
    def is_computed(self):
        """The name, which is the 'filedname' property, starts with ':@computed'"""
        return self.name.startswith(":@computed")

    @property
    def is_deleted(self):
        """The label, which is the 'name' property, starts with 'DELETE -'"""
        return self.label.startswith("DELETE -")

    @property
    def is_hidden(self):
        """Is either computed or deleted"""
        return self.is_computed or self.is_deleted

    @property
    def is_visible(self):
        """Not hdden"""
        return not self.is_hidden

    @property
    def label(self):
        # Note that the 'name' property is actually the variable label
        # Be aware that variables marked for deletion, that are hidden from users, have a 'name' that starts with 'DELETE -'
        return self.data["name"]

    @property
    def name(self):
        # Note that the 'filedName' property is actually the variable name
        # Be aware that compute variables, that are hidden from users, start with :@computed
        return self.data["fieldName"]

    @property
    def position(self):
        return self.data["position"]

    @property
    def socrata_data_type(self):
        return self.data["dataTypeName"]

    @property
    def generic_data_type(self):
        #TODO: implement
        return None
        
    @property
    def socrata_render_type(self):
        return self.data["renderTypeName"]


@dataclass
class PostmanPublisherConfig():
    name_prefix: str = field(default=None)
    name_suffix: str = field(default=None)
    
class SocrataPostmanPublisher():
    _postman_api: postman.PostmanApi
    _server: SocrataServer
    _config: PostmanPublisherConfig

    def __init__(self, api: postman.PostmanApi, server: SocrataServer, config:PostmanPublisherConfig = PostmanPublisherConfig()):
        self._postman_api = api
        self._server = server
        self._config = config

    def publish_dataset(self, dataset_id:str, target_id:str, target_type="workspace", config:"PostmanPublisherConfig" = None) -> str:
        """Publish a dataset as a collection under an existing workspace.
        
        If the target is a workspace, a new collection will be created. 
        If the target is a collection, its content will be replaced (but the collection id remains the same).

        """

        # use default config if not specified
        if config is None:
            config = self._config

        # get the dataset
        dataset = SocrataDataset(self._server, dataset_id)

        # instantiate collection manager
        if target_type == "workspace":
            # create a new collection
            collection_manager = postman.DataProductCollectionManager.create(self._postman_api, target_id, dataset.id, dartfx_id=f'socrata:{dataset.server.host}:{dataset.id}')
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
    dataset: SocrataDataset
    config: PostmanPublisherConfig
    
    def __init__(self, dataset: SocrataDataset, config:PostmanPublisherConfig = PostmanPublisherConfig()):
        self.dataset = dataset
        self.config = config

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

        # Query Data Request
        item = postman_collection.Item()
        item.name = "Query Data"
        request = item.create_request(f"https://{dataset.server.host}/resource/{dataset.id}.json")
        item.request = request
        # request paraneters
        request.url.create_query_parameter('$select',description="The set of columns to be returned, similar to a SELECT in SQL. Default: All columns, equivalent to $select=*.", disabled=True)
        request.url.create_query_parameter('$where',None, "Filters the rows to be returned, similar to WHERE. No default value.", True)
        request.url.create_query_parameter('$order',None, "Column to order results on, similar to ORDER BY in SQL. Default is unspecified order.", True)
        request.url.create_query_parameter('$group',None, "Column to group results on, similar to GROUP BY in SQL. Default is no grouping.", True)
        request.url.create_query_parameter('$having',None, "Filters the rows that result from an aggregation, similar to HAVING. Default is no filter.", True)
        request.url.create_query_parameter('$limit',None, "Maximum number of results to return. Default is 1,000. Maximum is 50,000).", True)
        request.url.create_query_parameter('$offset',None, "Offset count into the results to start at, used for paging. Default is 0.", True)
        request.url.create_query_parameter('$q',None, "Performs a full text search for a value. Default is no search.", True)
        request.url.create_query_parameter('$query',None, "A full SoQL query string, all as one parameter.", True)
        request.url.create_query_parameter('$$bom',None, "Prepends a UTF-8 Byte Order Mark to the beginning of CSV output. Default is False", True)
        collection.item.append(item)

        # variables
        collection.variable = []
        collection.variable.append(postman_collection.Variable(id="socrata_id", value=dataset.id))

        return collection