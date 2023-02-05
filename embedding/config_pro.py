# The path of pub.json
PUB_DATA_PATH = "/data/cache/aminer/pub.json"

# The path of sentence-bert model
SBERT_MODEL = "/data/cache/aminer/meta/embedding/sbert-model-en-256seq"

# The path of oag-bert model
OAGBERT_MODEL = "/data/cache/aminer/meta/embedding/oagbert-v2-sim"

# Config of embedding store place
MILVUS_HOST= "10.10.0.22"
MILVUS_PORT = "19530"

# Table name
MILVUS_OAG_EMBEEDING = "oagbert_embedding"
MILVUS_SBERT_EMBEEDING = "sentencebert_embedding"
MILVUS_TFIDF_EMBEEDING = "oagbert_tfidf_embedding"
# The search returns data for 365 days
SEARCH_DAYS = 365

FEATURES_PATH = '/data/cache/aminer/meta/embedding/tfidf-200/feature.pkl'
TF_IDF_PATH = '/data/cache/aminer/meta/embedding/tfidf-200/tfidf.pkl'
SVD_PATH = '/data/cache/aminer/meta/embedding/tfidf-200/svd.p'