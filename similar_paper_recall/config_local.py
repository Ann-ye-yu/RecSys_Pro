import os
import sys

# Returns the script path
BASEDIR = os.path.dirname(__file__)

CORPUS_FULL_PATH = os.path.join(BASEDIR, "corpus")
if not os.path.exists(CORPUS_FULL_PATH):
    os.makedirs(CORPUS_FULL_PATH)

PUB_JSON_FILE_PATH = os.path.join(CORPUS_FULL_PATH, 'pub1.json')
STORE_FILE_PATH = os.path.join(CORPUS_FULL_PATH, 'result.json')

# here will just recall top5, for the reason that the target paper would exist in the recall list.
RECALL_TOP_K_FROM_MILVUS = 6
RECALL_TOP_K_FROM_MEILI_SEARCH = 6

# setting the keywords number used to recall similar papers from MeiliSearch
KEWORDS_NUMBER_USED_TO_RECALL_SIMILAR_PAPER_FROM_MEILISEARCH = 4

PYMILVUS_CONFIG = {
    'alias' : 'default',
    'host': '10.10.0.22',
    'port': '19530'
}
COLLECTION_NAME = 'oagbert_embedding'