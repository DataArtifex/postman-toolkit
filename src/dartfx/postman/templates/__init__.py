import os
from dartfx.mtnards import MtnaRdsDataProduct
from dartfx.postmanapi import postman
from dartfx.postmanapi import postman_collection
from dartfx.socrata import SocrataServer
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = os.getenv("DARTFX_POSTMAN_JINJA_TEMPLATES_DIR", os.path.dirname(os.path.abspath(__file__)))

jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
jinja_env.filters['now'] = lambda dummy: datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_code_folder(**kwargs) -> postman_collection.ItemGroup:
    folder = postman_collection.ItemGroup()
    folder.name = "Code Snippets"
    template = jinja_env.get_template("code_folder.md.j2")
    folder.description = template.render(**kwargs)
    return folder

def get_collection_description(markdown, **kwargs) -> str:
        template = jinja_env.get_template("collection_description.md.j2")
        description = template.render(markdown=markdown, **kwargs)
        return description

def get_data_folder(platform:str|None=None, **kwargs) -> postman_collection.ItemGroup:
    folder = postman_collection.ItemGroup()
    folder.name = "Data"
    template = jinja_env.get_template("data_folder.md.j2")
    folder.description = template.render(platform=platform, **kwargs)
    return folder

def get_hvdnet_croissant_request(base_url, format=None, **kwargs) -> postman_collection.Item:    
    # Croissant request
    item = postman_collection.Item()
    item.name = "Croissant"
    if format:
        item.name += f" ({format})"
    item.create_request(f"{base_url}/croissant")
    item.request.url.create_query_parameter('format', value=format, description="The serialization format.", disabled=format is None) # type: ignore
    template = jinja_env.get_template("metadata_croissant_request.md.j2")
    item.request.description = template.render(**kwargs)
    return item

def get_hvdnet_dcat_request(base_url, format=None, **kwargs) -> postman_collection.Item:
    # DCAT request
    item = postman_collection.Item()
    item.name = "DCAT W3C"
    if format:
        item.name += f" ({format})"
    item.create_request(f"{base_url}/dcat")
    item.request.url.create_query_parameter('format', value=format,description="The serialization format.", disabled=format is None) # type: ignore
    template = jinja_env.get_template("metadata_dcat_request.md.j2")
    item.request.description = template.render(**kwargs)
    return item

def get_hvdnet_ddi_codebook_request(base_url, **kwargs) -> postman_collection.Item:
    # DDI-Codebook request
    item = postman_collection.Item()
    item.name = "DDI-Codebook"
    item.create_request(f"{base_url}/ddi/codebook")
    template = jinja_env.get_template("metadata_ddi-c_request.md.j2")
    item.request.description = template.render(**kwargs)
    return item

def get_hvdnet_ddi_cdif_request(base_url, format=None, **kwargs) -> postman_collection.Item:
    # DDI-CDI CDIF request
    item = postman_collection.Item()
    item.name = "DDI-CDI CDIF"
    if format:
        item.name += f" ({format})"
    item.create_request(f"{base_url}/ddi/cdif")
    item.request.url.create_query_parameter('format', value=format, description="The serialization format.", disabled=format is None) # type: ignore
    template = jinja_env.get_template("metadata_ddi-cdif_request.md.j2")
    item.request.description = template.render(**kwargs)
    return item

def get_hvdnet_mtnards_request(base_url, **kwargs) -> postman_collection.Item:
    # MTNA RDS request
    item = postman_collection.Item()
    item.name = "MTNA RDS"
    item.create_request(f"{base_url}/mtnards")
    template = jinja_env.get_template("metadata_mtnards_request.md.j2")
    item.request.description = template.render(**kwargs)
    return item

def get_hvdnet_socrata_request(base_url, **kwargs) -> postman_collection.Item:
    # Socrata request
    item = postman_collection.Item()
    item.name = "Socrata"
    item.create_request(f"{base_url}/socrata")
    template = jinja_env.get_template("metadata_socrata_request.md.j2")
    item.request.description = template.render(**kwargs)
    return item

def get_metadata_folder(**kwargs) -> postman_collection.ItemGroup:
        folder = postman_collection.ItemGroup()
        folder.name = "Metadata"
        template = jinja_env.get_template("metadata_folder.md.j2")
        folder.description = template.render(**kwargs)
        return folder

def get_markdown_request(base_url, **kwargs) -> postman_collection.Item:
    # Markdown request
    item = postman_collection.Item()
    item.name = "Markdown"
    item.create_request(f"{base_url}/markdown")
    template = jinja_env.get_template("metadata_markdown_request.md.j2")
    item.request.description = template.render(**kwargs)
    template = jinja_env.get_template("metadata_markdown_request_visualizer.js.j2")
    item.add_test_script(template.render(**kwargs))
    return item

def get_mtnards_collection_folder(markdown:str, **kwargs) -> postman_collection.ItemGroup:
        folder = postman_collection.ItemGroup()
        folder.name = "MTNA RDS"
        template = jinja_env.get_template("mtnards_collection_folder.md.j2")
        folder.description = template.render(markdown=markdown, **kwargs)
        return folder

def get_mtnards_metadata_folder(**kwargs) -> postman_collection.ItemGroup:
        folder = postman_collection.ItemGroup()
        folder.name = "Metadata (MTNA RDS)"
        template = jinja_env.get_template("mtnards_metadata_folder.md.j2")
        folder.description = template.render(**kwargs)
        return folder

def get_mtnards_regression_request(data_product: MtnaRdsDataProduct, **kwargs) -> postman_collection.Item:
    item = postman_collection.Item()
    item.name = "Run regression (bivariate)"
    item.request = item.create_request(f"{data_product.tabulate_api_url}")
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
    template = jinja_env.get_template("mtnards_tabulate_request.md.j2")
    item.request.description = template.render(**kwargs)
    return item


def get_mtnards_select_request(data_product: MtnaRdsDataProduct, **kwargs) -> postman_collection.Item:
    item = postman_collection.Item()
    item.name = "Select records"
    item.request = item.create_request(f"{data_product.select_api_url}")
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
    template = jinja_env.get_template("mtnards_select_request.md.j2")
    item.request.description = template.render(**kwargs)
    return item

def get_mtnards_tabulate_request(data_product: MtnaRdsDataProduct, **kwargs) -> postman_collection.Item:
    item = postman_collection.Item()
    item.name = "Create table"
    item.request = item.create_request(f"{data_product.tabulate_api_url}")
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
    template = jinja_env.get_template("mtnards_tabulate_request.md.j2")
    item.request.description = template.render(**kwargs)
    return item

def get_sql_folder(**kwargs) -> postman_collection.ItemGroup:
    folder = postman_collection.ItemGroup()
    folder.name = "SQL"
    template = jinja_env.get_template("sql_folder.md.j2")
    folder.description = template.render(**kwargs)
    return folder

def get_ai_folder(**kwargs) -> postman_collection.ItemGroup:
    folder = postman_collection.ItemGroup()
    folder.name = "AI"
    template = jinja_env.get_template("ai_folder.md.j2")
    folder.description = template.render(**kwargs)
    return folder

def get_visualization_folder(**kwargs) -> postman_collection.ItemGroup:
    folder = postman_collection.ItemGroup()
    folder.name = "Visualization"
    template = jinja_env.get_template("visualization_folder.md.j2")
    folder.description = template.render(**kwargs)
    return folder

def initialize_socrata_workspace(server: SocrataServer, postman_api: postman.PostmanApi, workspace_id: str|None = None, workspace_type:str ="public") -> postman.WorkspaceManager:
    """Initialize a workspace for a Socrata server instance."""
    template = jinja_env.get_template("socrata_workspace.md.j2")
    description = template.render(name=server.name, home=server.host_url) 
    # create a new workspace (if not specified)
    if workspace_id is None:
        name = server.name or server.host
        name += " (experimental)"
        workspace_id = postman_api.create_workspace(name, type=workspace_type, description=description)
    # retrieve the workspace
    manager = postman.WorkspaceManager(postman_api, workspace_id)
    manager.refresh_workspace()
    manager.description = description
    manager.update_workspace()
    # check content and update as needed
    # TODO
    return manager
