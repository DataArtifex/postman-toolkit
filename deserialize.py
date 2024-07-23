import logging
import os
from src.dartfx.postman import postman_collection as pc

loglevel = getattr(logging, "INFO", None)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=loglevel)

script_dir = os.path.dirname(os.path.realpath(__file__))
filename = "DAndD5editionAPI.postman_collection.json"
filename = "Hello World.postman_collection.json"
collection = pc.Collection.load(os.path.join(script_dir, f"tests/data/{filename}"))
collection.save(os.path.join(script_dir, f"tests/output/{filename}"))

      


