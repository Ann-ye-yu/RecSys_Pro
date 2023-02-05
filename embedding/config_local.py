# The path of pub.json
# PUB_DATA_PATH = "/Users/yizhao/Downloads/pub.json"
PUB_DATA_PATH = "D:/Develop/0411/rms_recall/pub.json"

# The path of sentence-bert model
# SBERT_MODEL = "/Users/yizhao/Downloads/sbert-model-en-256seq"
SBERT_MODEL = "D:/Develop/0411/rms_recall/sbert-model-en-256seq"

# The path of oag-bert model
# OAGBERT_MODEL = "/Users/yizhao/Downloads/oagbert-v2-sim"
OAGBERT_MODEL = "D:/Develop/0411/rms_recall/embedding/saved/oagbert-v2-sim"

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