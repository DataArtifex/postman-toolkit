
from src.dartfx.postman import postman_collection as pc
import os


def get_output_dir():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_dir, "output")

def test_hello_world():
    # Collection
    collection = pc.Collection()
    collection.info.name="Hello World"
    # Item
    item = pc.Item(name="Hello World")
    collection.item.append(item)
    # Request
    request = pc.Request(method="POST", url="https://postman-echo.com/post")
    request.body = pc.Body(mode="raw", raw='{"message": "Hello, World!"}')
    request.add_header("Content-Type", "application/json")
    item.request = request
    # save
    filename = os.path.join(get_output_dir(), "hello_world.json")
    collection.save(filename)
    assert collection.info.name == "Hello World"