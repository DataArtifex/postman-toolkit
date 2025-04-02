from dartfx.postmanapi import postman_collection

def get_metadata_folder():
        folder = postman_collection.ItemGroup()
        folder.name = "Metadata"
        folder.description = (
            "Metadata is essential for creating machine-actionable insights that drive automation, "
            "machine learning, and efficient data governance. High-quality metadata reduces the burden "
            "of data wrangling, facilitating faster, more reliable insights and enabling seamless integration "
            "of datasets across platforms. The requests in this folder deliver structured metadata adhering to "
            "the following industry standards:"
        )
        folder.description += (
            "\n- [Croissant](https://mlcommons.org/working-groups/data/croissant/): a leading-edge specification "
            "designed to enhance machine learning and AI workflows through standardized metadata practices"
        )
        folder.description += (
            "\n- [DCAT](https://www.w3.org/TR/vocab-dcat-3/): the W3C's Data Catalog Vocabulary, widely used for "
            "data discovery and cataloging in open data ecosystems"
        )
        folder.description += (
            "\n- [DDI-C](https://ddialliance.org/Specification/DDI-Codebook/2.5/): a lightweight XML-based codebook "
            "specification from the DDI Alliance that supports efficient metadata management for social, behavioral, "
            "and economic sciences"
        )
        folder.description += (
            "\n- [DDI-CDI](https://ddialliance.org/Specification/ddi-cdi): the latest RDF-based Cross-Domain Integration "
            "specification from the DDI Alliance, enabling metadata interoperability across diverse domains"
        )
        folder.description += (
            "\n\nBy leveraging these standards, along with best practices, this folder supports the [FAIR principles]"
            "(https://www.go-fair.org/fair-principles/) (Findable, Accessible, Interoperable, and Reusable data) "
            "and the [Cross-Domain Interoperability Framework](https://cdif.codata.org/). The API endpoints are hosted "
            "by the [High-Value Data Network](https://www.highvaluedata.net) to facilitate broad, cross-functional data utility."
        )
        return folder    

def get_croissant_request(base_url, format=None):    
    # Croissant request
    item = postman_collection.Item()
    item.name = "Croissant"
    if format:
        item.name += f" ({format})"
    item.create_request(f"{base_url}/croissant")
    item.request.url.create_query_parameter('format', value=format, description="The serialization format.", disabled=format is None)
    item.request.description  = "## Croissant"
    item.request.description += (
        "\nReturn the dataset metadata based on the MLCommons Croissant specification."
        "\nFor more information, visit https://mlcommons.org/working-groups/data/croissant/ and https://github.com/mlcommons/croissant"
    )
    return item

def get_dcat_request(base_url, format=None):
    # DCAT request
    item = postman_collection.Item()
    item.name = "DCAT W3C"
    if format:
        item.name += f" ({format})"
    item.create_request(f"{base_url}/dcat")
    item.request.url.create_query_parameter('format', value=format,description="The serialization format.", disabled=format is None)
    item.request.description = "## DCAT"
    item.request.description += (
        "\nReturn the dataset metadata based on the W3C Data Catalog standard."
        "\nFor more infornation, visit https://www.w3.org/TR/vocab-dcat-3/"
    )
    return item

def get_ddi_codebook_request(base_url):
    # DDI-Codebook request
    item = postman_collection.Item()
    item.name = "DDI-Codebook"
    item.create_request(f"{base_url}/ddi/codebook")
    item.request.description = "## DDI Codebook"
    item.request.description += "\nDDI-Codebook (Data Documentation Initiative Codebook), also known as DDI version 2, is a metadata standard designed for describing simple survey data for exchange or archiving in the social, behavioral, and economic sciences. It's an XML-based specification that provides a structured format for documenting various aspects of research data, including variables, coding schemes, methodology, and other relevant information. DDI-Codebook is simpler compared to its counterpart DDI-Lifecycle (version 3), making it suitable for straightforward data documentation needs. It allows researchers and data archivists to create standardized, machine-readable metadata that facilitates data discovery, understanding, and reuse across different research projects and institutions[1][3]."
    item.request.description += "\nFor more information, visit https://ddialliance.org/Specification/DDI-Codebook/2.5/"
    return item

def get_ddi_cdif_request(base_url, format=None):
    # DDI-CDI CDIF request
    item = postman_collection.Item()
    item.name = "DDI-CDI CDIF"
    if format:
        item.name += f" ({format})"
    item.create_request(f"{base_url}/ddi/cdif")
    item.request.url.create_query_parameter('format', value=format, description="The serialization format.", disabled=format is None)
    item.request.description = "## DDI-CDI CDIF"
    item.request.description += "\nFor more information, visit  https://cdif.codata.org/"
    return item


def get_data_folder():
    folder = postman_collection.ItemGroup()
    folder.name = "Data"
    folder.description  = "This folder contains request to query the dataset using the host platform API."
    return folder

def get_code_folder():
    folder = postman_collection.ItemGroup()
    folder.name = "Code Snippets"
    folder.description = (
        "This folder provides API requests that generate code snippets designed to streamline development and data science workflows. "
        "By offering reusable, customizable code samples, this collection helps developers and data scientists to quickly implement "
        "standard tasks, reduce boilerplate code, and improve productivity across projects.."
    )
    return folder
    
def get_sql_folder():
    folder = postman_collection.ItemGroup()
    folder.name = "SQL"
    folder.description  = "This folder contains requests to generate SQL code for loading the dataset in various database environments."
    return folder

def get_ai_folder():
    folder = postman_collection.ItemGroup()
    folder.name = "AI"
    folder.description  = "This folder contains requests to facilitate integration of the dataset with various AI platforms."
    return folder

def get_visualization_folder():
    folder = postman_collection.ItemGroup()
    folder.name = "Visualization"
    folder.description  = "This folder contains requests to facilitate the visualization of the dataset."
    return folder
