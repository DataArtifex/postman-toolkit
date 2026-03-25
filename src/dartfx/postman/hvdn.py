"""
Integration with High-Value Data Network
"""


class Credentials:
    account: str
    password: str

    def __init__(self, account, password):
        self.account = account
        self.password = password


class MongoRegistry:
    host: str
    port: int = 27017

    def __init__(self, host, port: int = 27017):
        self.host = host
        self.port = port

    def register_postman_collection(self, collection_id: str):
        pass
