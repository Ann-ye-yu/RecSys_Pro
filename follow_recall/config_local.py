import os
import time
import datetime
from dateutil.parser import parse
import logging
from common.config import *

logger = logging.getLogger("recallApp.focus_scholar_recall.config")
BASEDIR = os.path.dirname(__file__)
# test
# HINDEX_PAPERS_FILE = os.path.join(BASEDIR, '/Users/yizhao/workspace/workstations/vscode/rms_recall_zy/hindex_pub.json')
# dev
HINDEX_PAPERS_FILE = 'D:\Aminer\\aminer数据集/pub.json'

YESTERDAY_TAG = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y_%m_%d")
# test
# NEW_PAPERS_FILE = "/Users/yizhao/workspace/workstations/vscode/rms_recall_zy/rms_recall/create_scholar_pool/corpus/2022_1_5 - scholar_pool.json"
# dev
NEW_PAPERS_FILE_BASE = '/data/cache/aminer/meta/scholar_pool'
# if os.path.exists(f'/data/cache/aminer/meta/scholar_pool/{YESTERDAY_TAG}-scholar_pool.json'):
#     NEW_PAPERS_FILE = f'/data/cache/aminer/meta/scholar_pool/{YESTERDAY_TAG}-scholar_pool.json'
# else:
#     logger.info(YESTERDAY_TAG + '-scholar_pool.json not exists')
#     sys.exit(0)
TIME_TAG = time.strftime("%Y_%m_%d", time.localtime())
# test
# FOCUS_SCHOLAR_RECALL_PATH = os.path.join(BASEDIR, f'corpus/followed_scholar_recall-{TIME_TAG}.json')
# dev




FOCUS_SCHOLAR_RECALL_PATH_BASE = "D:\Aminer\\aminer数据集/followed_scholar_recall"
if os.path.exists(f'D:\Aminer\\aminer数据集/{YESTERDAY_TAG}-latest_paper_pool.json'):
    GLOBAL_NEWEST_POOL = f'D:\Aminer\\aminer数据集/{YESTERDAY_TAG}-latest_paper_pool.json'
else:
    GLOBAL_NEWEST_POOL = None
    logger.info(YESTERDAY_TAG + '-latest_paper_pool.json not exists')

if not os.path.exists(FOCUS_SCHOLAR_RECALL_PATH_BASE):
    os.makedirs(FOCUS_SCHOLAR_RECALL_PATH_BASE)
FOCUS_SCHOLAR_RECALL_PATH = f'{FOCUS_SCHOLAR_RECALL_PATH_BASE}-{TIME_TAG}.json'
SIM_AUTHORS_API = "https://api.aminer.cn/api/person/similar/"

DISTANCE_START_TIME = '2000-01-01'  # Start time for calculating distance
DISTANCE_START = time.mktime(time.strptime(DISTANCE_START_TIME, '%Y-%m-%d'))

# active time of users
# Start time of active user judgment default: 90 days
ACTIVE_DELTA = -30
LATEST_DELTA = 30
START_TIME = datetime.datetime.now() + datetime.timedelta(days=ACTIVE_DELTA)
ACTIVE_START_TIME = START_TIME.strftime('%Y-%m-%d')
# current time
ACTIVE_END_TIME = datetime.datetime.now().strftime('%Y-%m-%d')

# Temporary note: you can freely control the time range of active users through these two lines of code
# ACTIVE_START_TIME = parse('2022-03-01T23:00:00.000000')
# ACTIVE_END_TIME = parse('2022-03-05T00:00:00.000000')


# number of recalled papers which you can set by yourself
SIM_AUTHORS_NUM = 10
RECALL_NUMBER_OF_HIGH = 25
RECALL_NUMBER_OF_NEW = 25

# Connect to SSDB database
SSDB_HOST = "10.10.0.23"
SSDB_POST = 12002

RECALLED_DAYS_OF_NEW_PAPERS = 90

COOPERATION_NUM = 10
SEMAPHORE = 300 

# delete history files config
LOG_SAVE_DAYS = 3
LOG_SAVE_PATH = "D:\Aminer\\aminer数据集"

