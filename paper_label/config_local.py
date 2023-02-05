import os,sys
path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(path)
import datetime
BASE_DIR = os.path.dirname(__file__)
FATHER_OF_BASE_DIR = os.path.dirname(BASE_DIR)

CORPUS_BASE_PATH = "corpus"
CACHE_BASE_PATH = "cache"
if not os.path.exists(CACHE_BASE_PATH):
    os.makedirs(CACHE_BASE_PATH)
if not os.path.exists(CORPUS_BASE_PATH):
    os.makedirs(CORPUS_BASE_PATH)

HIGH_PAPER_POOL_PATH = os.path.join(BASE_DIR, "corpus/pub.json")
LATEST_PAPER_POOL_PATH = os.path.join(FATHER_OF_BASE_DIR, "latest_paper/corpus")
SCHOLAR_POOL_BAT_PATH = os.path.join(FATHER_OF_BASE_DIR, "scholar_pool/corpus")
KEYWORDS_FILE = os.path.join(BASE_DIR, "corpus/duplicate_removal_merge_words_with_floor.json")
IDS2SUBJECT_WORDS_FILE_PATH = os.path.join(BASE_DIR, 'data/index2subject.json')
LOAD_PAPER_POOL_FILE_NUMBER_EACH_TIME = 10

SAVE_FILE_PATH = os.path.join(BASE_DIR, "corpus/labeled_papers.json")

# active_delta = -1 means get yesterday's paper pool.
ACTIVE_DELTA = -1
START_TIME = datetime.datetime.now() + datetime.timedelta(days=ACTIVE_DELTA)
ACTIVE_START_TIME = START_TIME.strftime('%Y-%m-%d')
# current time
ACTIVE_END_TIME = datetime.datetime.now().strftime('%Y-%m-%d')

DB_NAME = "label"
COL_NAME = "paper_labels"

# OAGBERT_MODEL = os.path.join(FATHER_OF_BASE_DIR, "embedding/saved/oagbert-v2-sim")
OAGBERT_MODEL = 'C:/Users/nijzh/Desktop/saved/oagbert-v2-sim'
OAGBERT_WORDS_EMBEDDING = os.path.join(CACHE_BASE_PATH, "words_oagbert_embedding")
OAGBERT_INDEX2WORDS = os.path.join(CACHE_BASE_PATH, "oag_bert_index2words.json")
OAGBERT_WORDS_INDEX = os.path.join(CACHE_BASE_PATH, "words.hnsw")

MILVUS_DB_HOST = '10.10.0.22'
MILVUS_DB_PORT = "19530"
COLLECTION_NAME = 'subject_headings_collection'
INDEX2SUBJECT_FILE_PATH = './data/index2subject.json'
WORD_OAGBER_EMB_FILE_PATH = './data/words_oagbert_embedding.npy'

MILVUS_METRIC_TYPE_FOR_SEARCH = 'L2'  # L2 means Euclidean distance
MILVUE_NPROBE_FOR_SEARCH = 10  #
MIVLUS_SUBJECT_COLLECTION_EMB_FIELD_NAME = 'subject_headings_emb'

LABELED_PAPERS_NUMBERS_EACH_TIME = 20
