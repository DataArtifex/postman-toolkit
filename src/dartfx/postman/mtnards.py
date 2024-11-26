from dataclasses import dataclass, field
from dartfx.mtnards import MtnaRdsServer
from dartfx.postmanapi import PostmanApi


@dataclass
class MtnaRdsPostmanPublisherConfig():
    name_prefix: str = field(default=None)
    name_suffix: str = field(default=None)

class MtnaRdsPostmanPublisher():
    _rds_server: MtnaRdsServer
    _postman_api: PostmanApi
    _temp_workspace_id: str = None # if set can be used for importing temporary collections

    def __init__(self, api: PostmanApi, rds_server: MtnaRdsServer, temp_workspace_id=None):
        self._postman_api = api
        self._rds_server = rds_server
        self._temp_workspace_id = temp_workspace_id

    @property
    def rds_server(self):
        return self._rds_server
    
    @property
    def postman_api(self):
        return self._postman_api
    
    def publish_data_product_to_workspace(self, catalog_id, data_product_id, workspace_id):
        """Publish a data product under an existing workspace"""
        collection = self.rds_server.get_postman_collection(catalog_id, data_product_id)
        collection_id = self.postman_api.import_collection(workspace_id, collection)
        return collection_id

    def publish_data_product_to_collection(self, catalog_id, data_product_id, collection_uid, folder_uid=None, temp_workspace_id=None, create_root=True):
        """Published a data product under an existing collection or folder"""
        # initialize temporary workspace
        if not temp_workspace_id:
            if self._temp_workspace_id:
                temp_workspace_id = self._temp_workspace_id
            else:
                raise ValueError("No temporary workspace ID provided")
        # get the RDS collection
        rds_collection = self.rds_server.get_postman_collection(catalog_id, data_product_id)
        # publish in a temporary workspace
        temp_collection_id = self.publish_data_product_to_workspace(catalog_id, data_product_id, temp_workspace_id)
        temp_collection = self.postman_api.get_collection(temp_collection_id)
        # create a target folder to host the RDS collection
        if create_root: # this should alnost always be the case
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
        # collect a Postman collection top folder identifers
        uids = []
        for item in collection['collection']['item']:
            uids.append(item['uid'])
        return uids