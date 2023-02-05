from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import json
import numpy
import logging
from concurrent.futures import ProcessPoolExecutor
from get_paper_embedding.paper_emb.sentence_bert import SBERT_EMb
from get_paper_embedding.paper_emb.oagbert import OAG_BERT_Emb
logger = logging.getLogger("recallApp.embedding")
from common.misc import func_exec_time
from config import *
import argparse


def get_paper_text(paper):
    text_list = list()
    for item in paper:
        text = ""
        title = item.get("title")
        if title:
            text += title
        abstract = item.get("abstract")
        if abstract:
            text += abstract
        text_list.append([text, item])
    return text_list


@func_exec_time
def load_pub_data_embedding(data_path, model_path, limit=-1):
    sentecen_bert_model = SBERT_EMb(model_path=model_path)
    embeddings = list()
    index2paperid = dict()
    with open(data_path, "r", encoding="utf-8") as f:
        try:
            i = 0 
            for line in f:
                if i%1000==0:
                    logger.info(f"read {i}")
                paper = json.loads(line)
                paper_id = paper.get("_id", "")
                if paper_id != "":
                    text = get_paper_text(paper)
                    paper_embedding = sentecen_bert_model.get_emb(text).flatten()
                    embeddings.append(paper_embedding)
                    index2paperid[i] = paper_id
                    i += 1
                if limit != -1 and i == limit:
                    break    
        except Exception as e:
            logger.warning(f"file end exceptional, maybe some other programs are writting the {data_path} file")
    embeddings = numpy.array(embeddings)
    return embeddings, index2paperid


def worker(d):
    paper_embedding = OAG_BERT_Emb(OAGBERT_MODEL).get_emb(d).flatten()
    return paper_embedding, d.get("_id")


def worker1(d):
    paper_embedding = SBERT_EMb(SBERT_MODEL).get_emb(d[0]).flatten()
    return paper_embedding, d[1].get("_id")


# @func_exec_time
def load_pub_data_embedding_parallel(data_path, model, cores, limit=-1, cache=False, load_cache_embedding=False):
    if model == "sentence-bert":
        bert_cacheembedding = SBERT_CACHEEMBEDDING
        bert_index2paper = SBERT_INDEX2PAPER
    if model == "oag-bert":
        bert_cacheembedding = OAGBERT_CACHEEMBEDDING
        bert_index2paper = OAGBERT_INDEX2PAPER

    embeddings = list()
    cache_index2paperid = dict()
    papers = list()
    papers_new = list()
    if load_cache_embedding:
        if os.path.isfile(bert_cacheembedding+".npy"):
            embeddings = numpy.load(bert_cacheembedding+".npy").tolist()
            cache_index2paperid = json.load(open(bert_index2paper))

    with open(data_path, "r", encoding="utf-8") as f:
        try:
            i = 0
            for line in f:
                if i%5000==0:
                    logger.info(f"rea0d {i}")
                paper = json.loads(line)
                paper_id = paper.get("_id", "")
                if paper_id != "":
                    i += 1
                    papers.append(paper)
                if limit != -1 and i == limit:
                    break
        except Exception as e:
            logger.warning(f"file end exceptional, maybe some other programs are writting the {data_path} file")
        logger.info(f"total {i} papers")

        for item in papers:
            if item.get("_id") not in cache_index2paperid.values():
                papers_new.append(item)
        logger.info(f"number of new paper is {len(papers_new)}")

        flag = j = len(cache_index2paperid)
        if model == "oag-bert":
            with ProcessPoolExecutor(max_workers=cores) as pool:
                for embedding, paper_id in pool.map(worker, papers_new):
                    embeddings.append(embedding)
                    cache_index2paperid[j] = paper_id
                    j += 1
                    if j % 100 == 0:
                        logger.info(f"new paper total {len(papers_new)}, embedd {j-flag}")
                embeddings = numpy.array(embeddings)
        else:
            with ProcessPoolExecutor(max_workers=cores) as pool:
                for embedding, paper_id in pool.map(worker1, papers_new):
                    embeddings.append(embedding)
                    cache_index2paperid[j] = paper_id
                    j += 1
                    if j % 100 == 0:
                        logger.info(f"new paper total {len(papers_new)}, embedd {j-flag}")
                embeddings = numpy.array(embeddings)

    if cache:
        numpy.save(bert_cacheembedding, embeddings)
    return embeddings, cache_index2paperid


# @func_exec_time
def save_nms_result(embeddings, index2paperid, model):
    index = nmslib.init(method='hnsw', space='cosinesimil')
    # seems id only support num type
    index.addDataPointBatch(embeddings)
    INDEX_TIME_PARAMS = {
            'indexThreadQty': 10,
            'M': 100,    # bigger better, 10~100
            'efConstruction': 2000,  # bigger better, <2000
            'post': 2}
    index.createIndex(INDEX_TIME_PARAMS, print_progress=True)
    if model == "oag-bert":
        index.saveIndex(OAGBERT_NMS)
        json.dump(index2paperid,open(OAGBERT_INDEX2PAPER,"w"))
    if model == "sentence-bert":
        index.saveIndex(SBERT_NMS)
        json.dump(index2paperid, open(SBERT_INDEX2PAPER, "w"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='oag-bert',
                        help='Select a model from \{oag-bert, sentence-bert\}')
    parser.add_argument("--limit", default=-1, type=int)
    parser.add_argument("--cores", default=multiprocessing.cpu_count()//4, type=int)
    parser.add_argument("--cache", action="store_false")
    parser.add_argument("--load_cache", action="store_false")
    args = parser.parse_args()
    logger.info(args)
    args = parser.parse_args()
    embeddings, index2paperid = load_pub_data_embedding_parallel(data_path=PUB_DATA_PATH,
    model=args.model,
    cores=args.cores,
    limit=args.limit,
    cache=args.cache,
    load_cache_embedding=args.load_cache
    )
    logger.info(embeddings.shape)
    logger.info(f"data load ok, embedding len {len(embeddings)}, index len {len(list(index2paperid.keys()))}")
    save_nms_result(embeddings, index2paperid, args.model)


    """
    (['5fc0d2d6d4150a363c5f03fe', '5faa6990d4150a363c8d3e61', '5fae6de5d4150a363cec696e', '5f156ca69e795e540ffd1e88', '5d0a0e7f3a55ac03d0ed9b52', '5d9ed25247c8f76646f6739c', '600fe84ed4150a363c241cc9', '5fe1d5c591e0119a161ede3e', '5ff68a33d4150a363ccc4b40', '600d4944d4150a363c681d9c'], [0.258969783782959, 0.31219303607940674, 0.37358272075653076, 0.3858060836791992, 0.5155153870582581, 0.53859543800354, 0.583733320236206, 0.635879635810852, 0.6563519239425659, 0.6574757099151611])

    """