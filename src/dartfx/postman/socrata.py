"""
Classes and helpers to publish Socrata data products to Postman collections.
"""
from dataclasses import dataclass, field

from dartfx.postman import postman
from dartfx.postman import postman_collection
from dartfx.socrata import SocrataServer, SocrataDataset

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
            collection_manager = postman.DataProductCollectionManager.factory(self._postman_api, target_id, dataset.id, dartfx_id=f'socrata:{dataset.server.host}:{dataset.id}')
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
        metadata_folder = postman_collection.ItemGroup()
        metadata_folder.name = "Metadata"
        metadata_folder.description = (
            "Metadata is essential for creating machine-actionable insights that drive automation, "
            "machine learning, and efficient data governance. High-quality metadata reduces the burden "
            "of data wrangling, facilitating faster, more reliable insights and enabling seamless integration "
            "of datasets across platforms. The requests in this folder deliver structured metadata adhering to "
            "the following industry standards:"
        )
        metadata_folder.description += (
            "\n- [Croissant](https://mlcommons.org/working-groups/data/croissant/): a leading-edge specification "
            "designed to enhance machine learning and AI workflows through standardized metadata practices"
        )
        metadata_folder.description += (
            "\n- [DCAT](https://www.w3.org/TR/vocab-dcat-3/): the W3C's Data Catalog Vocabulary, widely used for "
            "data discovery and cataloging in open data ecosystems"
        )
        metadata_folder.description += (
            "\n- [DDI-C](https://ddialliance.org/Specification/DDI-Codebook/2.5/): a lightweight XML-based codebook "
            "specification from the DDI Alliance that supports efficient metadata management for social, behavioral, "
            "and economic sciences"
        )
        metadata_folder.description += (
            "\n- [DDI-CDI](https://ddialliance.org/Specification/ddi-cdi): the latest RDF-based Cross-Domain Integration "
            "specification from the DDI Alliance, enabling metadata interoperability across diverse domains"
        )
        metadata_folder.description += (
            "\n\nBy leveraging these standards, along with best practices, this folder supports the [FAIR principles]"
            "(https://www.go-fair.org/fair-principles/) (Findable, Accessible, Interoperable, and Reusable data) "
            "and the [Cross-Domain Interoperability Framework](https://cdif.codata.org/). The API endpoints are hosted "
            "by the [High-Value Data Network](https://www.highvaluedata.net) to facilitate broad, cross-functional data utility."
        )
        collection.item.append(metadata_folder)
        
        base_url = f"https://highvaluedata.net/api/datasets/socrata:{dataset.server.host}:{dataset.id}"

        # Croissant request
        item = postman_collection.Item()
        item.name = "Croissant"
        item.create_request(f"{base_url}/croissant")
        item.request.url.create_query_parameter('format', description="The serialization format.", disabled=True)
        item.request.description  = "## Croissant"
        item.request.description += (
            "\nReturn the dataset metadata based on the MLCommons Croissant specification."
            "\nFor more infornation, visit https://mlcommons.org/working-groups/data/croissant/ and https://github.com/mlcommons/croissant"
        )
        metadata_folder.item.append(item)


        # DCAT request
        item = postman_collection.Item()
        item.name = "DCAT W3C (JSON-LD)"
        item.create_request(f"{base_url}/dcat")
        item.request.url.create_query_parameter('format', description="The serialization format.", disabled=True)
        item.request.description = "## DCAT (JSON-LD)"
        item.request.description += (
            "\nReturn the dataset metadata based on the W3C Data Catalog standard.."
            "\nFor more infornation, visit https://www.w3.org/TR/vocab-dcat-3/"
        )
        metadata_folder.item.append(item)

        # DCAT request
        item = postman_collection.Item()
        item.name = "DCAT W3C (Turtle)"
        item.create_request(f"{base_url}/dcat")
        item.request.url.create_query_parameter('format', value='ttl', description="The serialization format.")
        item.request.description = "## DCAT"
        item.request.description += "\nFor more infornation, visit https://www.w3.org/TR/vocab-dcat-3/"
        metadata_folder.item.append(item)
                
        # DDI-Codebook request
        item = postman_collection.Item()
        item.name = "DDI-Codebook"
        item.create_request(f"{base_url}/ddi/codebook")
        item.request.description = "## DDI Codebook"
        item.request.description += "\nDDI-Codebook (Data Documentation Initiative Codebook), also known as DDI version 2, is a metadata standard designed for describing simple survey data for exchange or archiving in the social, behavioral, and economic sciences. It's an XML-based specification that provides a structured format for documenting various aspects of research data, including variables, coding schemes, methodology, and other relevant information. DDI-Codebook is simpler compared to its counterpart DDI-Lifecycle (version 3), making it suitable for straightforward data documentation needs. It allows researchers and data archivists to create standardized, machine-readable metadata that facilitates data discovery, understanding, and reuse across different research projects and institutions[1][3]."
        item.request.description += "\nFor more information, visit https://ddialliance.org/Specification/DDI-Codebook/2.5/"
        metadata_folder.item.append(item)

        # DDI-CDI CDIF request
        item = postman_collection.Item()
        item.name = "DDI-CDI CDIF (JSON-LD)"
        item.create_request(f"{base_url}/ddi/cdif")
        item.request.description = "## DDI-CDI CDIF"
        item.request.description += "\nFor more information, visit  https://cdif.codata.org/"
        metadata_folder.item.append(item)

        # DDI-CDI CDIF request
        item = postman_collection.Item()
        item.name = "DDI-CDI CDIF (Turtle)"
        item.description = """
        <TODO
        For more information, visit https://cdif.codata.org/
        """
        item.create_request(f"{base_url}/ddi/cdif")
        item.request.url.create_query_parameter('format', value='ttl', description="The serialization format.")
        item.request.description = "## DDI-CDI CDIF"
        item.request.description += "\nFor more information, visit  https://cdif.codata.org/"
        metadata_folder.item.append(item)

        # DATA FOLDER
        data_folder = postman_collection.ItemGroup()
        data_folder.name = "Data"
        data_folder.description  = "This folder contains request to query the dataset using the host platform API."
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
        code_folder = postman_collection.ItemGroup()
        code_folder.name = "Code Snippets"
        code_folder.description = (
            "This folder provides API requests that generate code snippets designed to streamline development and data science workflows. "
            "By offering reusable, customizable code samples, this collection helps developers and data scientists to quickly implement "
            "standard tasks, reduce boilerplate code, and improve productivity across projects.."
        )
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
            item.create_request(f"{base_url}/code/{language['path']}")
            self._add_query_request_parameters(item.request)
            code_folder.item.append(item)

        # SQL FOLDER
        sql_folder = postman_collection.ItemGroup()
        sql_folder.name = "SQL"
        sql_folder.description  = "This folder contains requests to generate SQL code for loading the dataset in various database environments."
        collection.item.append(sql_folder)


        # AI FOLDER
        ai_folder = postman_collection.ItemGroup()
        ai_folder.name = "AI"
        ai_folder.description  = "This folder contains requests to facilitate integration of the dataset wwith various AI tools."
        collection.item.append(ai_folder)

        # VISUALIZATION FOLDER
        dv_folder = postman_collection.ItemGroup()
        dv_folder.name = "Visualization"
        dv_folder.description  = "This folder contains requests to facilitate the visualization of the dataset."
        collection.item.append(dv_folder)

        # COLLECTION VARIABLES
        collection.variable = []
        collection.variable.append(postman_collection.Variable(id="socrataId", value=dataset.id))

        return collection