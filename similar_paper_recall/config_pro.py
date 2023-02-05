import os
import sys

# Returns the script path
BASEDIR = os.path.dirname(__file__)


PUB_JSON_FILE_PATH = '/data/cache/aminer/pub.json'

# here will just recall top5, for the reason that the target paper would exist in the recall list.
RECALL_TOP_K_FROM_MILVUS = 6
RECALL_TOP_K_FROM_MEILI_SEARCH = 6

# setting the keywords number used to recall similar papers from MeiliSearch
KEWORDS_NUMBER_USED_TO_RECALL_SIMILAR_PAPER_FROM_MEILISEARCH = 4