import sys
from pymongo import MongoClient
import logging

logger = logging.getLogger("recallApp.mongo_connection")
class MongoConnection:

    def __init__(self,mongo_setting:dict):
        self.user = mongo_setting["USER"]
        self.password = mongo_setting["PASSWORD"]
        self.auth_source = mongo_setting["AUTH_SOURCE"]
        self.host = mongo_setting["HOST"]
        self.port = mongo_setting["PORT"]
        self.client = None


    # def __del__(self):
    #     self.client.close()

    def get_aminer_db(self):
        self.client = MongoClient(host=self.host, port=self.port, username=self.user, 
        password=self.password, authSource=self.auth_source,serverSelectionTimeoutMS=20000, socketTimeoutMS=20000)
        return self.client['aminer']

    def get_db(self,db):
        if self.client is None:
            logger.debug(f"make mongo connection")
            self.client = MongoClient(host=self.host, port=self.port, username=self.user, 
            password=self.password, authSource=self.auth_source,serverSelectionTimeoutMS=20000, socketTimeoutMS=20000)
        return self.client[db]

    def get_web_db(self):
        self.client = MongoClient(host=self.host, port=self.port, username=self.user, 
        password=self.password, authSource=self.auth_source,serverSelectionTimeoutMS=20000, socketTimeoutMS=20000)
        return self.client['web']

    def get_publication_dupl_col(self):
        db = self.get_db("aminer")
        return db['publication_dupl']

    def get_person_coauthors_col(self):
        db = self.get_db("aminer")
        return db['person_coauthors']

    def get_social_activity_col(self):
        db = self.get_db("aminer")
        return db['social_activity']

    def get_user_event_log_col(self):
        db = self.get_db("web")
        return db['user_event_log']

    def get_usr_col(self):
        db = self.get_db("aminer")
        return db['usr']

    def get_topic_col(self):
        db = self.get_db("aminer")
        return db['topic']

    def get_person_col(self):
        db = self.get_db("aminer")
        return db['person']
    def get_scholarPool_col(self):
        db = self.get_web_db()
        return db['scholar_paper_pool']


if __name__ == '__main__':
    conn = MongoConnection({
    "USER": "aminer_platform_reader",
    "PASSWORD": "Reader@123",
    "AUTH_SOURCE": "aminer",
    "HOST": "192.168.6.208",
    "PORT": 37017
})
    print(conn.get_db("aminer").list_collection_names())
