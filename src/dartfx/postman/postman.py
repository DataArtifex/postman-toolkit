"""
Classes and helpers to interact with the Postman API, workspaces, collections, folders, and realted resources.


"""
from datetime import datetime
from enum import Enum
import json
import logging
import uuid
import requests


class PostmanApi:
    """Helper to call the Postman API"""

    api_key: str  # The API key

    def __init__(self, api_key: str):
        self.api_key = api_key

    #
    # ENUM
    #
    class EntityType(Enum):
        WORKSPACE = "workspace"
        COLLECTION = "collection"
        API = "api"

    class WorkspaceType(Enum):
        PERSONAL = "personal"
        PRIVATE = "private"
        PUBLIC = "public"
        TEAM = "team"
        PARTNER = "partner"

    #
    # CORE HTTP REQUESTS
    #
    def request(self, method, endpoint, description, headers={}, success=200, **kwargs):
        """Call the Postman API"""
        url = f"https://api.getpostman.com/{endpoint}"
        # prepare headers
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        } | headers
        # call API
        response = requests.request(method, url, headers=headers, **kwargs)
        # handle response
        if response.status_code == success:
            return response
        else:
            logging.error(f"{description} -- {response.status_code}")
            logging.error(response.text)
            raise PostmanApiError(description, url, response.status_code, response)

    def delete_request(self, endpoint, description, headers={}, success=200, **kwargs):
        """Call the Postman API using the DEL method"""
        return self.request(
            "delete", endpoint, description, headers={}, success=200, **kwargs
        )

    def get_request(self, endpoint, description, headers={}, success=200, **kwargs):
        """Call the Postman API using the GET method"""
        return self.request(
            "get", endpoint, description, headers={}, success=200, **kwargs
        )

    def post_request(self, endpoint, description, headers={}, success=200, **kwargs):
        """Call the Postman API using the POST method"""
        return self.request(
            "post", endpoint, description, headers={}, success=200, **kwargs
        )

    def patch_request(self, endpoint, description, headers={}, success=200, **kwargs):
        """Call the Postman API using the PATCH method"""
        return self.request(
            "patch", endpoint, description, headers={}, success=200, **kwargs
        )

    def put_request(self, endpoint, description, headers={}, success=200, **kwargs):
        """Call the Postman API using the PUT method"""
        return self.request(
            "put", endpoint, description, headers={}, success=200, **kwargs
        )

    #
    # COLLECTIONS
    #
    def create_collection(
        self,
        workspace_id,
        name,
        collectionSchemaUrl="https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        variables=None,
    ) -> str:
        """Create a blank Postman collection.

        Use import_collection to create from a dictionnary.

        Args:
            workspace_id (str): The ID of the workspace
            name (str): The name of the collection
            collectionSchemaUrl (str, optional): The URL of the collection schema. Defaults to "https://schema.getpostman.com/json/collection/v2.1.0/collection.json".
            variables (dict, optional): The variables of the collection. Defaults to None. Must be a valid Postman variable object.

        Raises:
            PostmanApiError: If the API returns an error

        Returns:
            str: The UID of the collection

        """
        params = {"workspace": workspace_id}
        data = {
            "collection": {
                "info": {
                    "name": name,
                    "schema": collectionSchemaUrl,
                },
                "item": [],
            }
        }
        if variables:
            data["collection"]["variable"] = variables
        # call API
        logging.debug("API: Cteate collection")
        logging.debug(data)
        response = self.post_request(
            "collections",
            f"Create collection {name} in workspace {workspace_id}",
            params=params,
            json=data,
        )
        data = response.json()
        return data["collection"]["uid"]

    def delete_collection(self, collection_id) -> str:
        """Delete a Postman collection

        Args:
            collection_id (str): The ID of the collection

        Raises:
            PostmanApiError: If the API returns an error

        Returns:
            str: The ID of the collection

        """
        response = self.delete_request(
            f"collections/{collection_id}", f"Delete collection {id}"
        )
        data = response.json()
        return data["collection"]["id"]

    def get_collection(self, collection_id) -> dict:
        """Get a Postman collection.

        Args:
            collection_id (str): The ID of the collection

        Raises:
            PostmanApiError: If the API returns an error

        Returns:
            dict: The collection data

        """
        response = self.get_request(
            f"collections/{collection_id}", f"Get collection {id}"
        )
        data = response.json()
        return data

    def import_collection(self, workspace_id, collection: dict) -> str:
        """Create a Postman collection from a populated dictionary.

        Args:
            workspace_id (str): The ID of the workspace
            collection (dict): The collection data

        Raises:
            PostmanApiError: If the API returns an error

        Returns:
            str: The ID of the collection
        """
        params = {"workspace": workspace_id}
        data = {"collection": collection}
        response = self.post_request(
            "collections",
            f"Import collection in workspace {workspace_id}",
            params=params,
            json=data,
        )
        data = response.json()
        return data["collection"]["id"]

    def replace_collection(self, collection_id:str, collection: dict) -> str:
        """Replaces a Postman collection from a populated dictionary

        Args:
            workspace_id (str): The ID of the workspace
            collection_id (str): The ID of the collection
            collection (dict): The collection data

        Returns:
            str: _description_
        """
        data = {"collection": collection}
        response = self.put_request(
            f"collections/{collection_id}",
            f"Replace collection {collection_id}",
            json=data,
        )
        data = response.json()
        return data["collection"]["id"]


    #
    # FOLDERS
    #
    def create_folder(
        self,
        collection_id,
        name: str = "New Folder",
        description: str = None,
        parent_id: str = None,
        data=None,
    ) -> str:
        """Create a folder in a collection

        Args:
            collection_id (str): The ID of the collection
            name (str): The name of the folder
            description (str, optional): The description of the folder. Defaults to None.
            parent_id (str, optional): The ID of the parent folder. Defaults to None.

        Raises:
            PostmanApiError: If the API returns an error

        Returns:
            str: The UID of the folder
        """
        folder_data = {
            "name": name,
        }
        if description:
            folder_data["description"] = description
        if parent_id:
            folder_data["folder"] = parent_id
        if data:
            folder_data.update(data)
        response = self.post_request(
            f"collections/{collection_id}/folders",
            f"Create folder {name} in collection {collection_id}",
            json=folder_data,
        )
        folder_data = response.json()
        # transfering folder requires uid, so return that instead of just id
        uid = folder_data["data"]["owner"]+'-'+folder_data["data"]["id"]
        return uid

    def get_folder(self, collection_id, folder_id) -> dict:
        """Get a folder in a collection

        Args:
            collection_id (str): The ID of the collection
            id (str): The ID of the folder

        Raises:
            PostmanApiError: If the API returns an error

        Returns:
            dict: The folder data
        """
        response = self.get_request(
            f"collections/{collection_id}/folders/{folder_id}",
            f"Get folder {folder_id} in collection {collection_id}",
        )
        data = response.json()
        return data

    def delete_folder(self, collection_id, id) -> str:
        """Delete a folder in a collection

        Args:
            collection_id (str): The ID of the collection
            id (str): The ID of the folder

        Raises:
            PostmanApiError: If the API returns an error

        Returns:
            str: The ID of the folder
        """
        response = self.delete_request(
            f"collections/{collection_id}/folders/{id}",
            f"Delete folder {id} in collection {collection_id}",
        )
        data = response.json()
        return data

    def update_folder(self, collection_id, id, data: dict) -> dict:
        """Update a folder in a collection

        Args:
            collection_id (str): The ID of the collection
            id (str): The ID of the folder
            data (dict): The folder data

        Raises:
            PostmanApiError: If the API returns an error

        Returns:
            dict: The folder data
        """
        response = self.put_request(
            f"collections/{collection_id}/folders/{id}",
            f"Update folder {id} in collection {collection_id}",
            json=data,
        )
        data = response.json()
        return data

    #
    # TAGS
    #
    def get_elements_by_tag(
        self,
        slug: str,
        entity_type: EntityType = None,
        limit: int = None,
        direction=None,
        cursor: str = None,
    ) -> dict:
        """Get elements by tag.
        Only available under Postman Enterprise plan.

        Args:
            slug (str): The slug of the tag
            entity_type (EntityType, optional): The type of the entity. Defaults to None.
            limit (int, optional): The limit of the elements. Defaults to None.
            direction (str, optional): The direction of the elements. Defaults to None.
            cursor (str, optional): The cursor of the elements. Defaults to None.
        Raises:
            PostmanApiError: If the API returns an error

        Returns:
            dict: The elements
        """
        params = {}
        if entity_type:
            params["entity_type"] = entity_type
        if limit:
            params["limit"] = limit
        if direction:
            params["direction"] = direction
        if cursor:
            params["cursor"] = cursor
        response = self.get_request(
            f"tags/{slug}/elements", f"Get elements by tag {slug}", params=params
        )
        data = response.json()
        return data

    #
    # TRANSFERS
    #

    def collection_folder_transfer(
        self,
        uids: list[str],
        target_uid: str,
        target_model: str = "collection",
        location_position: str = "start",
        location_model=None,
        location_uid: str = None,
        mode: str = "move",
    ) -> dict:
        """Transfer a collection or folder to another collection or folder

        Args:
            uids (list): The folder UIDs to transfer.
            target_uid (str): the UID of the destination collection or folder.
            target_model (str, optional): he type of item where the items will be transferred to (collection or folder). Defaults to 'collection'.
            location_position (str, optional): The item's position within the destination (start, end, before, after). Defaults to 'start'.
            location_model (str, optional):  For the before or after positions, a string value that contains the type of item (model) that the transferred item will be positioned by. Defaults to None.
            location_uid (str, optional): For the before or after positions, a string value that contains the model's UID. Defaults to None.
            mode (str, optional): The transfer mode (move or copy). Defaults to 'move'.

        Raises:
            PostmanApiError: If the API returns an error

        Returns:
            dict: The transfer data
        """
        if isinstance(uids, str):
            uids = [uids]
        data = {
            "ids": uids,
            "target": {
                "id": target_uid,
                "model": target_model,
            },
            "location": {
                "position": location_position,
                "model": location_model,
                "id": location_uid,
            },
            "mode": mode,
        }
        response = self.post_request(
            "collection-folders-transfers",
            f"Transfer elements {uids} to {target_uid} ({target_model})",
            json=data,
        )
        data = response.json()
        return data

    #
    # WORKSPACES
    #
    def create_workspace(
        self, name: str, type: WorkspaceType, description: str = None
    ) -> str:
        """Create a new Postman workspace.

        Args:
            name (str): The name of the workspace
            type (WorkspaceType): The type of the workspace
            description (str, optional): The description of the workspace. Defaults to None.

        Raises:
            PostmanApiError: If the API returns an error

        Returns:
            str: The ID of the workspace

        """
        # prepare data
        data = {
            "workspace": {
                "name": name,
                "type": type.value,
                "description": description,
            }
        }
        # call API
        response = self.post_request(
            "workspaces", f"Create workspace {name}", json=data
        )
        data = response.json()
        return data["workspace"]["uid"]

    def delete_workspace(self, workspace_id) -> str:
        """Delete a Postman workspace

        Args:
            workspace_id (str): The ID of the workspace

        Returns:
            str: The ID of the workspace
        """
        response = self.delete_request(
            f"workspaces/{workspace_id}", f"Delete workspace {id}"
        )
        data = response.json()
        return data["workspace"]["id"]


class PostmanApiError(Exception):
    """Custom exception for Postman API errors."""

    def __init__(self, message, url, status_code=None, response=None):
        super().__init__(message)
        self.message = message
        self.url = url
        self.status_code = status_code
        self.response = response

    def __str__(self):
        base_message = f"PostmanApiError: {self.message}"
        if self.status_code is not None:
            base_message += f" (Status Code: {self.status_code})"
        if self.response is not None:
            base_message += f" (Response: {self.response})"
        return base_message


class WorkspaceManager:
    """Helper to interact with a Postman workspace"""

    TYPES = ["personal", "private", "public", "team", "partner"]
    _id: str  # workspace id
    _api: str  # API object
    _data: dict  # the workspace Postman JSON object
    _tags: list[str]  # the workspace tags as an array
    _global_variables: list[
        object
    ]  # the workspace gloabl variables as an array of JSON objects
    _updated_at: datetime  # local update timestamp

    def __init__(self, api: PostmanApi, id: str):
        self._api = api
        self._id = id
        self._data = None
        self._tags = None
        self._global_variables = None
        self._updated_at = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def data(self) -> dict:
        if self._data is None:
            self.refresh_workspace()
        return self._data

    @property
    def name(self) -> str:
        return self.data.get("name")

    @name.setter
    def name(self, value: str):
        self._date["name"] = value
        self._updated_at = datetime.now

    @property
    def type(self) -> str:
        return self.data.get("type")

    @property
    def description(self) -> str:
        return self.data.get("description")

    @description.setter
    def description(self, value: str):
        self._data["description"] = value
        self._updated_at = datetime.now

    @property
    def visibility(self) -> str:
        return self.data.get("visibility")

    @visibility.setter
    def visibility(self, value: bool):
        self._data["visibility"] = bool(value)
        self._updated_at = datetime.now

    @property
    def created_by(self) -> str:
        return self.data.get("createdBy")

    @property
    def updated_by(self) -> str:
        return self.data.get("updatedBy")

    @property
    def created_at(self) -> datetime:
        value = self.data.get("createdAt")
        value = value.replace(".000Z", "+00:00")  # for Python < 3.11
        return datetime.fromisoformat(value)

    @property
    def updated_at(self) -> datetime:
        value = self.data.get("updatedAt")
        value = value.replace(".000Z", "+00:00")  # for Python < 3.11
        return datetime.fromisoformat(value)

    @property
    def collections(self):
        return self.data.get("collections")

    @property
    def apis(self):
        return self.data.get("apis")

    @property
    def tags(self):
        if self._tags is None:
            self.refresh_tags()
        return self._tags

    @property
    def global_variables(self):
        if self._global_variables is None:
            self.refresh_global_variables()
        return self._global_variables

    @property
    def postman_api(self) -> PostmanApi:
        """The Postman API object associated with this workspace"""
        return self._api

    def create_collection(
        self,
        name,
        collectionSchemaUrl="https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    ):
        """Helper to create a collection for this workspace."""
        return self.postman_api.create_collection(self.id, name, collectionSchemaUrl)

    def get_global_variables(self):
        """Get the workspace global variables"""
        response = self._api.get_request(
            f"workspaces/{self._id}/global-variables", "Get workspace variables"
        )
        data = response.json()
        return data

    def set_global_variable(self, name: str, value: str):
        # TODO
        logging.warning("set_global_variable not implemented.")
        return

    def unset_global_variable(self, name: str, value: str):
        # TODO
        logging.warning("unset_global_variable not implemented.")
        return

    def get_workspace(self):
        """Get the workspace information"""
        response = self._api.get_request(
            f"workspaces/{self._id}", "Get workspace information"
        )
        data = response.json()
        return data

    def get_workspace_tags(self):
        """Get the workspace tags (Enterprise only)"""
        response = self._api.get_request(
            f"workspaces/{self._id}/tags", "Get workspace tags"
        )
        data = response.json()
        return data


    def get_collection(self, collection_id) -> dict:
        """Proxy to Postman API get_collection method."""
        return self.postman_api.get_collection(collection_id)

    def import_collection(self, collection: dict):
        """Import a Postman collection in this workspace"""
        collection_id = self.postman_api.import_collection(self._id, collection)
        self.refresh_workspace()
        return collection_id

    def refresh_workspace(self):
        """Refresh the workspace data from the API"""
        data = self.get_workspace()
        self._data = data["workspace"]
        return self.data

    def refresh_tags(self):
        """Refresh the workspace tags from the API"""
        data = self.get_workspace_tags()
        self._tags = []
        for tag in data["tags"]:
            self._tags.append(tag["slug"])
        return self.tags

    def refresh_global_variables(self):
        """Refresh the workspace global variables from the API"""
        data = self.get_global_variables()
        self._global_variables = data["values"]
        return self.global_variables


class CollectionManager:
    """Helper to interact with an existing Postman collection"""

    _id: str  # Postman collection id
    _api: str  # API object
    _data: dict  # the underlying Postman JSON object
    _updated_at: datetime  # local update timestamp
    _tags: list[str]  # the collection tags as an array (enterprise only)

    def __init__(self, api: PostmanApi, collection_id: str, refresh=True):
        self._id = collection_id
        self._api = api
        self._data = None
        self._updated_at = None
        if refresh:
            self.refresh_collection_data()

    @property
    def data(self) -> dict:
        if self._data is None:
            self.refresh_collection_data()
        return self._data

    @property
    def description(self):
        return self.data.get("info").get("name")

    @description.setter
    def description(self, value: str):
        self.data["info"]["description"] = value
        # PATCH
        patch_data = {"collection": {"info": {"description": value}}}
        response = self._api.patch_request(
            f"collections/{self._id}",
            json=patch_data,
            description="Patching collection info description",
        )
        return response

    @property
    def id(self):
        return self._id

    @property
    def info(self):
        return self.data.get("info")

    def patch_info(self):
        patch_data = {"collection": {"info": self.info}}
        logging.debug(f"Patch info data: {patch_data}")
        response = self._api.patch_request(
            f"collections/{self._id}",
            json=patch_data,
            description="Patching collection info",
        )
        return response

    @property
    def name(self):
        return self.data.get("info").get("name")

    @name.setter
    def name(self, value: str):
        self.data["info"]["name"] = value
        # PATCH
        patch_data = {"collection": {"info": {"name": value}}}
        response = self._api.patch_request(
            f"collections/{self._id}",
            json=patch_data,
            description="Patching collection info name",
        )
        return response

    @property
    def uid(self):
        return self.info.get("uid")

    @property
    def variables(self):
        if "variable" not in self.data:
            self.data["variable"] = []
        return self.data.get("variable")

    def get_collection(self):
        """Fecth colelction data from API"""
        response = self._api.get_request(
            f"collections/{self._id}", "Get collection information"
        )
        data = response.json()
        print(data)
        return data


    def refresh_collection_data(self):
        """Refreshes the cached collection data from the API"""
        data = self.get_collection()
        self._data = data["collection"]

    # FOLDER
    def get_folder(self, id: str):
        return self._api.get_folder(self._id, id)

    def delete_folder(self, id: str):
        return self._api.delete_folder(self._id, id)

    def update_folder(self, id: str, data: dict):
        return self._api.update_folder(self._id, id, data)

    def create_folder(self, name: str, description: str = None, parent_id: str = None):
        return self._api.create_folder(self._id, name, description, parent_id)

    # VARIABLES
    def get_variable(self, name: str):
        if self.variables:
            for variable in self.variables:
                if variable.get("key") == name:
                    return variable
        return

    def patch_variables(self):
        self.sanitize_variables()
        patch_data = {"collection": {"variables": self.data["variable"]}}
        logging.debug(f"Patch variables data: {patch_data}")
        response = self._api.patch_request(
            f"collections/{self._id}",
            json=patch_data,
            description="Patching collection variables",
        )
        return response

    def sanitize_variables(self):
        """Remove properties from the variables that would cause an error.
        These may be set and returned by the API but should not be submitted back.
        """
        for variable in self.variables:
            variable.pop("id", None)

    def set_variable(self, key: str, value, disabled: bool = False):
        """Adds or updates a variable in the collection"""
        # analyze and adjust type
        value_type = type(value).__name__
        if isinstance(value, dict):
            value = json.dumps(value)
            value_type = "string"
        elif isinstance(value, list):
            value = json.dumps(value)
            value_type = "string"
        elif value_type == "str":
            value_type = "string"
        elif value_type == "int":
            value_type = "integer"
        elif value_type == "float":
            value_type = "number"
        elif value_type == "bool":
            value_type = "boolean"
        else:
            raise Exception(f"Unsupported data type {value_type}: {value_type}")
        # get or create variable
        variable = self.get_variable(key)
        if not variable:  # create it
            variable = {"key": key}
            self.data["variable"].append(variable)
        # set variable properties
        variable["value"] = value
        variable["type"] = value_type
        variable["disabled"] = disabled
        return self.patch_variables()

    def rename_variable(self, old_key: str, new_key: str):
        """renames a variable in the collection"""
        for variable in self.variables:
            if variable.get("key") == old_key:
                variable["key"] = new_key
                return self.patch_variables()
        logging.warning(f"Variable {old_key} not found")
        return

    def unset_variable(self, key: str):
        """removes a variable from the collection"""
        for i, variable in enumerate(self.variables):
            if variable.get("key") == key:
                self.variables.pop(i)
                return self.patch_variables()
        logging.warning(f"Variable {key} not found")
        return


class DataProductCollectionManager(CollectionManager):
    """Helper to interact with a Postman collection specializing in data.
    
    
    """

    _dartfx_variable_name: str
    _dartfx_data: dict

    @classmethod
    def factory(
        cls,
        api: PostmanApi,
        workspace_id: str,
        name: str,
        dartfx_id: str = None,
        dartfx_variable_name: str = "_dartfx",
    ):
        """Create a new data product collection"""
        if not dartfx_id:  # generate an id if not provided
            dartfx_id = str(uuid.uuid4())
        dartfx_data = {"id": dartfx_id}
        dartfx_variable_item = {
            "key": dartfx_variable_name,
            "value": json.dumps(dartfx_data),
            "type": "string",
            "disabled": False,
        }
        variables = [dartfx_variable_item]
        collection_id = api.create_collection(workspace_id, name, variables=variables)
        return cls(api, collection_id, dartfx_variable_name)

    def __init__(self, api: PostmanApi, collection_id: str, dartfx_variable: str = "_dartfx"):
        super().__init__(api, collection_id)
        self._dartfx_variable_name = dartfx_variable


    # DartFX data storage
    def get_dartfx_data(self, refresh=True):
        data = self.get_variable(self._dartfx_variable_name)
        self._dartfx_data = json.loads(data["value"]) # return the variable value as dictionnary
        return self._dartfx_data

    def set_dartfx_data(self):
        return self.set_variable(self._dartfx_variable_name, self._dartfx_data)

    # DartFX variable
    def get_dartfx_variable(self, key: str, refresh=True):
        return self.get_dartfx_data().get(key)

    def set_dartfx_variable(self, key: str, value):
        if value:
            self.get_dartfx_data().set[key] = value
        else:
            self.get_dartfx_data().pop(key, None)
        return self.set_dartfx_data()

    # Folders
    def register_folder(self, id: str, name: str):
        pass

    def get_registered_folder(self, id: str):
        pass
    
    
class Foldermanager:
    """Helper to interact with an existing Postman folder"""

    _id: str  # Postman folder id
    _collection_id: str  # Postman collection id
    _api: str  # API object
    _data: dict  # the underlying Postman JSON object
    _updated_at: datetime  # local update timestamp
    _tags: list[str]  # the collection tags as an array (enterprise only)

    def __init__(self, api: PostmanApi, collection_id: str, folder_id, refresh=True):
        self.collection_id = collection_id
        self._id = folder_id
        self._api = api
        self._data = None
        self._updated_at = None
        if refresh:
            self.refresh_data()

    @property
    def data(self) -> dict:
        if self._data is None:
            self.refresh_data()
        return self._data

    def refresh_data(self):
        """Refreshes the cached collection data from the API"""
        data = self.get_collection()
        self._data = data["collection"]


    def create_folder(self, name: str, description: str = None, ):
        return self._api.create_folder(self._id, name, description, self.id)

