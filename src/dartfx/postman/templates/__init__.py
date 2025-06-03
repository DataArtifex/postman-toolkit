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
    folder.name = "Code Generators"
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
    folder.name = "MTNA RDS Postman"
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
    template = jinja_env.get_template("mtnards_tabulate_request.md.j2")
    item.request.description = template.render(**kwargs)
    return item


def get_mtnards_select_request(data_product: MtnaRdsDataProduct, **kwargs) -> postman_collection.Item:
    item = postman_collection.Item()
    item.name = "Select records"
    item.request = item.create_request(f"{data_product.select_api_url}")
    template = jinja_env.get_template("mtnards_select_request.md.j2")
    item.request.description = template.render(**kwargs)
    return item

def get_mtnards_tabulate_request(data_product: MtnaRdsDataProduct, **kwargs) -> postman_collection.Item:
    item = postman_collection.Item()
    item.name = "Create table"
    item.request = item.create_request(f"{data_product.tabulate_api_url}")
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
