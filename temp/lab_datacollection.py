import argparse
from datetime import datetime
import logging
import os
from src.dartfx.postman import postman


# Unicode characters: https://www.compart.com/en/unicode/



def main():
    api = postman.PostmanApi(os.environ.get('POSTMAN_API_KEY'))
    #workspace = postman.WorkspaceManager(args.workspace_id, api)
    if not args.collection_id:
        #collection_id = workspace.create_collection(f'🔢 Data Product 101 {datetime.now().isoformat()[:19]}', 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json')
        collection = postman.DataProductCollectionManager.factory(api, args.workspace_id, f'🔢 Ipsum Lorem {datetime.now().isoformat()[:19]}')
    else:
        collection_id = args.collection_id
        collection = postman.DataProductCollectionManager(api, collection_id)
    assert collection
    
    # Variables
    #collection.set_variable('test_str',"lorem ipsum")
    #collection.set_variable('test_integer',123)
    #collection.set_variable('test_number',123.456)
    #collection.set_variable('test_bool',True)
    #collection.set_variable('dummy','Hi!')
    #collection.unset_variable('dummy')
    #collection.rename_variable('test_bool','test_boolean')

    # Folders
    dartf_data = collection.get_dartfx_data()
    # Metadata
    metadata_folder_id = dartf_data.get('metadata')
    if not metadata_folder_id:
        metadata_folder_id = collection.create_folder('Metadata')
        dartf_data['metadata'] = {'folder_id': metadata_folder_id}
    # RDS
    mtnards_folder_id = dartf_data.get('mtnards')
    if not mtnards_folder_id:
        mtnards_folder_id = collection.create_folder('Rich Data Services')
        dartf_data['mtnards'] = {'folder_id': mtnards_folder_id}
    # Save environment
    collection.set_dartfx_data(dartf_data)

if __name__ == '__main__':
    """Main"""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--collection_id")
    parser.add_argument("-ws","--workspace_id", default='194dd33d-438d-47e1-ae69-e2ab5b414beb')
    parser.add_argument("-ll","--loglevel", default='INFO', help="Log Level")

    args = parser.parse_args()
    print(args)

    loglevel = getattr(logging, args.loglevel.upper(), None)
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=loglevel)

    main()