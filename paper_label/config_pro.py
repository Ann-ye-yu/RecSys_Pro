import datetime
import os
BASE_DIR = os.path.dirname(__file__)

HIGH_PAPER_POOL_PATH = "/data/cache/aminer/pub.json"
LATEST_PAPER_POOL_PATH = "/data/cache/aminer/meta/latest_paper"
SCHOLAR_POOL_BAT_PATH = "/data/cache/aminer/meta/scholar_pool"
OAGBERT_MODEL = "/data/cache/aminer/meta/embedding/oagbert-v2-sim"
LOAD_PAPER_POOL_FILE_NUMBER_EACH_TIME = 10

CORPUS_BASE_PATH = "corpus"
DAYS_OF_PAPERS = 7
SAVE_FILE_PATH = "corpus/labeled_papers.json"

# active_delta = -1 means get yesterday's paper pool.
ACTIVE_DELTA = -1
START_TIME = datetime.datetime.now() + datetime.timedelta(days=ACTIVE_DELTA)
ACTIVE_START_TIME = START_TIME.strftime('%Y-%m-%d')
# current time
ACTIVE_END_TIME = datetime.datetime.now().strftime('%Y-%m-%d')

# needed match the setting in server.
KEYWORDS_FILE = os.path.join(BASE_DIR,"corpus/duplicate_removal_merge_words_with_floor.json")
DB_NAME = "tracking"
COL_NAME = "paper_label"

IDS2SUBJECT_WORDS_FILE_PATH = os.path.join(BASE_DIR, 'data/index2subject.json')
MILVUS_DB_HOST = '10.10.0.22'
MILVUS_DB_PORT = "19530"
COLLECTION_NAME = 'subject_headings_collection'
INDEX2SUBJECT_FILE_PATH = './data/index2subject.json'
WORD_OAGBER_EMB_FILE_PATH = './data/words_oagbert_embedding.npy'

MILVUS_METRIC_TYPE_FOR_SEARCH = 'L2'  # L2 means Euclidean distance
MILVUE_NPROBE_FOR_SEARCH = 10  #
MIVLUS_SUBJECT_COLLECTION_EMB_FIELD_NAME = 'subject_headings_emb'

LABELED_PAPERS_NUMBERS_EACH_TIME = 20