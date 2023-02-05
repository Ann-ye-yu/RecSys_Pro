import logging
import pymilvus

from pymilvus import connections
from pymilvus import Collection
from config import PYMILVUS_CONFIG
from config import COLLECTION_NAME


class PymilvusConnection:
    """
    connection to pymilvus.
    """
    conn = None

    def __init__(self, connection_setting=PYMILVUS_CONFIG):
        logging.info("connect to pymilvus.")
        connections.connect(**connection_setting)

    def get_embedding_collection(self, collection_name=COLLECTION_NAME) -> pymilvus.orm.collection.Collection:
        logging.info(f'connection to {collection_name} in pymilvus')
        self.conn = Collection(collection_name)
        self.conn.load()
        return self.conn

    def __del__(self):
        logging.info('pymilvus disconnect!')
        connections.disconnect(alias='default')
