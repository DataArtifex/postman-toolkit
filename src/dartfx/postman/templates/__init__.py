import os
from dartfx.postmanapi import postman_collection
from jinja2 import Environment, FileSystemLoader


TEMPLATES_DIR = os.getenv("DARTFX_POSTMAN_JINJA_TEMPLATES_DIR",os.path.dirname(os.path.abspath(__file__)))

jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def get_metadata_folder():
        folder = postman_collection.ItemGroup()
        folder.name = "Metadata"
        template = jinja_env.get_template("metadata_folder.md.j2")
        folder.description = template.render()
        return folder

def get_croissant_request(base_url, format=None):    
    # Croissant request
    item = postman_collection.Item()
    item.name = "Croissant"
    if format:
        item.name += f" ({format})"
    item.create_request(f"{base_url}/croissant")
    item.request.url.create_query_parameter('format', value=format, description="The serialization format.", disabled=format is None)
    template = jinja_env.get_template("metadata_croissant_request.md.j2")
    item.request.description = template.render()
    return item

def get_dcat_request(base_url, format=None):
    # DCAT request
    item = postman_collection.Item()
    item.name = "DCAT W3C"
    if format:
        item.name += f" ({format})"
    item.create_request(f"{base_url}/dcat")
    item.request.url.create_query_parameter('format', value=format,description="The serialization format.", disabled=format is None)
    template = jinja_env.get_template("metadata_dcat_request.md.j2")
    item.request.description = template.render()
    return item

def get_ddi_codebook_request(base_url):
    # DDI-Codebook request
    item = postman_collection.Item()
    item.name = "DDI-Codebook"
    item.create_request(f"{base_url}/ddi/codebook")
    template = jinja_env.get_template("metadata_ddi-c_request.md.j2")
    item.request.description = template.render()
    return item

def get_ddi_cdif_request(base_url, format=None):
    # DDI-CDI CDIF request
    item = postman_collection.Item()
    item.name = "DDI-CDI CDIF"
    if format:
        item.name += f" ({format})"
    item.create_request(f"{base_url}/ddi/cdif")
    item.request.url.create_query_parameter('format', value=format, description="The serialization format.", disabled=format is None)
    template = jinja_env.get_template("metadata_ddi-cdif_request.md.j2")
    item.request.description = template.render()
    return item

def get_data_folder():
    folder = postman_collection.ItemGroup()
    folder.name = "Data"
    template = jinja_env.get_template("data_folder.md.j2")
    folder.description = template.render()
    return folder

def get_code_folder():
    folder = postman_collection.ItemGroup()
    folder.name = "Code Snippets"
    template = jinja_env.get_template("code_folder.md.j2")
    folder.description = template.render()
    return folder
    
def get_sql_folder():
    folder = postman_collection.ItemGroup()
    folder.name = "SQL"
    template = jinja_env.get_template("sql_folder.md.j2")
    folder.description = template.render()
    return folder

def get_ai_folder():
    folder = postman_collection.ItemGroup()
    folder.name = "AI"
    template = jinja_env.get_template("ai_folder.md.j2")
    folder.description = template.render()
    return folder

def get_visualization_folder():
    folder = postman_collection.ItemGroup()
    folder.name = "Visualization"
    template = jinja_env.get_template("visualization_folder.md.j2")
    folder.description = template.render()
    return folder