import os, sys
abs_path = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(abs_path))
sys.path.append(root_path)
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import json
# import nmslib
import numpy
import logging
from embedding.get_paper_embedding.paper_emb.oagbert import OAG_BERT_Emb
logger = logging.getLogger("recallApp.embedding")
from common.misc import func_exec_time
from config import *
import argparse


def get_words_embedding_parallel(data_path,cores,limit=-1,cache = True,load_cache_embedding=False):
    oag_bert_model = OAG_BERT_Emb(OAGBERT_MODEL)
    embeddings = list()
    index2words = dict()
    words = list()

    def worker(word):
        word_embedding = oag_bert_model.get_emb(word).flatten()
        return word_embedding, word.get("title")

    if load_cache_embedding:
        embeddings = numpy.load(OAGBERT_WORDS_EMBEDDING + ".npy")
        index2words = json.load(open(OAGBERT_INDEX2WORDS))
    else:
        with open(data_path, "r", encoding="utf-8") as f:
            try:
                words_json_list = json.load(f)["words"]
                i = 0
                for row in words_json_list:
                    if i % 100 == 0:
                        logger.info(f"read {i}")
                    if "name" in row.keys() and len(row["name"])>0:
                        word = {"title": row["name"]}
                        i += 1
                        words.append(word)
                        if limit != -1 and i == limit:
                            break
            except Exception as e:
                logger.warning(f"file end exceptional, maybe some other programs are writting the {data_path} file")
        logger.info(f"total {i} words")
        with ThreadPoolExecutor(max_workers=cores) as ex:
            j = 0
            for embedding, word_title in ex.map(worker, words):
                embeddings.append(embedding)
                index2words[j] = word_title
                j += 1
                if j % 100 == 0:
                    logger.info(f"total {i}, embedd {j}")
            embeddings = numpy.array(embeddings)
    if cache:
        numpy.save(OAGBERT_WORDS_EMBEDDING, embeddings)
    # save to disk
    numpy.save(OAGBERT_WORDS_EMBEDDING, embeddings)
    with open(OAGBERT_INDEX2WORDS, 'w', encoding='utf-8') as f:
        json.dump(index2words, f, ensure_ascii=False, indent=1)

    return embeddings, index2words


# def save_nms_result(data,index2words):
#     index = nmslib.init(method='hnsw', space='cosinesimil')
#     # seems id only support num type
#     index.addDataPointBatch(data)
#     INDEX_TIME_PARAMS = {
#             'indexThreadQty': 10,
#             'M': 100,    # bigger better, 10~100
#             'efConstruction': 2000,  # bigger better, <2000
#             'post': 2}
#
#     index.createIndex(INDEX_TIME_PARAMS, print_progress=True)
#     index.saveIndex(OAGBERT_WORDS_INDEX)
#     json.dump(index2words, open(OAGBERT_INDEX2WORDS,"w"))


def get_words_index():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", default=-1, type=int)
    parser.add_argument("--cores", default=multiprocessing.cpu_count() // 2, type=int)
    parser.add_argument("--cache", action="store_false")
    parser.add_argument("--load_cache", action="store_true")
    args = parser.parse_args()
    logger.info(args)
    args = parser.parse_args()
    embeddings, index2words = get_words_embedding_parallel(data_path=KEYWORDS_FILE, cores=args.cores,
                                                           limit=args.limit,
                                                           cache=args.cache,
                                                           load_cache_embedding=args.load_cache)
    logger.info(embeddings.shape)
    logger.info(f"data load ok, embedding len {len(embeddings)}, index len {len(list(index2words.keys()))}")
    # save_nms_result(embeddings, index2words)


if __name__ == "__main__":
    # get_words_index()
    pass