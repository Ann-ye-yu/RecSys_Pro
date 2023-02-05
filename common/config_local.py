import os
# MongoDB INFO
# aminer db
AMINER_MONGODB_SETTINGS = {
    "USER": "aminer_platform_reader",
    "PASSWORD": "Reader@123",
    "AUTH_SOURCE": "aminer",
    "HOST": "192.168.6.208",
    "PORT": 37017
}

WEB_MONGODB_SETTINGS = {
    "USER": "aminer_platform_reader",
    "PASSWORD": "Reader@123",
    "AUTH_SOURCE": "aminer",
    "HOST": "192.168.6.208",
    "PORT": 37017
}

# postgresql setting
POSTGRESQL_SETTING = {
    'host': '10.10.0.39',
    'port': 5432,
    'user': 'reporter',
    'password': 'report_1232*()',
    'database': 'rms'
}
POSTGRESQL_SETTING_FOR_FEATURE = {
    'host': '10.10.0.39',
    'port': 5432,
    'user': 'feature_dev',
    'password': 'howtodoit12345_*&%',
    'database': 'feature'
}

AMINER_MONGODB_SETTINGS_FOR_MINI_PROGRAM = {
    "username": "aminer_platform_reader",
    "password": "Reader@123",
    "authSource": "aminer",
    "host": "192.168.6.208",
    "port": 37017,
}

LABEL_MONGODB_SETTINGS = {
    "USER": "keger",
    "PASSWORD": "9734659835d9f5aeababb8d3d2389d94",
    "AUTH_SOURCE": "label",
    "HOST": "121.22.248.8",
    "PORT": 12307
}

PUBLICATION_COLLECTION = "publication_dupl"  # Source table
BATCH_SIZE = 100  # cursor batch_size
# The cycle of updating the token
CYCLE_OF_UPDATE_TOKEN = 5000  # each 5000 sec..
CYCLE_OF_UPDATE_TOKEN_SCHOLAR = 3000
# logging
import asyncio
import logging
LOG_LEVEL = logging.DEBUG

# 第三方 SMTP 服务
# MAIL_HOST="smtp.qiye.aliyun.com"  #设置服务器
# MAIL_PORT = 465
# MAIL_USER="support@aminer.cn"    #用户名
# MAIL_PASS="Temp123!@#"   #口令 
MAIL_HOST="smtp.qq.com"  #设置服务器
MAIL_PORT = 25
MAIL_USER="964684108@qq.com"    #用户名
MAIL_PASS="gcfwzqbsythqbchg"   #口令 

SENDER = '964684108@qq.com'
# SENDER = 'support@aminer.cn'
RECEIVERS = ['1051532098@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
# RECEIVERS = ['1051532098@qq.com', "zhaoyi.hb@gmail.com"]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

IS_TEST= False

SSDB_HOST = "10.10.0.23"
SSDB_POST = 12000

REDIS_HOST = "10.10.0.28"
REDIS_PORT = 6379
REDIS_SSL = False
REDIS_PASSWORD = "UEWA21CzY3Gwclf5pTXPdpsEUehFFiNQF+tl6NwADl4="

SEMAPHORE = 15
semaphore = asyncio.Semaphore(SEMAPHORE)

SEMAPHORE_ZONE = 100
semaphore_zone = asyncio.Semaphore(SEMAPHORE_ZONE)

SEMAPHORE_AC = 300
semaphore_ac = asyncio.Semaphore(SEMAPHORE_AC)



BASE_DIR = os.path.dirname(__file__)
# INPUT_LOG_DATA_BASE =  os.path.join(BASE_DIR,"../active_user/corpus")
# if not os.path.exists(INPUT_LOG_DATA_BASE):
#     os.makedirs(INPUT_LOG_DATA_BASE)
# INPUT_LOG_DATA = os.path.join(INPUT_LOG_DATA_BASE,"input_log_data.json")

# INPUT_LOG_DATA = 'E:/Aminer/aminer数据集/input_log_data.json'
INPUT_LOG_DATA = 'C:/Users/86134/Desktop/data/input_log_data.json'
RETRY_TIMES = 3

LOGGING_FILE_PATH="rms_recall.log"

SIM_AUTHORS_API = "https://api.aminer.cn/api/person/similar/"
SIM_AUTHORS_NUM = 10
COOPERATION_NUM = 10

# connect to pymilvus
PYMILVUS_CONFIG = {
    'alias' : 'default',
    'host': '10.10.0.22',
    'port': '19530'
}
COLLECTION_NAME = 'oagbert_embedding'