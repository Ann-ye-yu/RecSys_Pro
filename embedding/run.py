import os
import sys

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from embedding.tfidf_for_oagbert import TfidfGenerator
import json
import time
import argparse
from concurrent.futures import ProcessPoolExecutor
from get_paper_embedding.paper_emb.sentence_bert import SBERT_EMb
from get_paper_embedding.paper_emb.oagbert import OAG_BERT_Emb
from common.misc import func_exec_time
from config import *
from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)

logger = logging.getLogger("recallApp.embedding")



def get_paper_text(paper):
    """Change the paper format to match the sentence-bert model input.

        Return the new format.

        Args:
            paper:row of pubs.json

        Returns:
            Returns the new format of paper data .
    """
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


def worker(d):
    """Get an embedding for each paper use oag-bert model.

        Return the embedding, id_of_mysql, ts for each paper .

        Args:
            d:paper

        Returns:
            Returns embedding, id_of_mysql, ts .
    """
    paper_embedding = OAG_BERT_Emb(OAGBERT_MODEL).get_emb(d).flatten()
    return paper_embedding, d.get("id_of_mysql"), d.get("ts")

def worker_tfidf(arg_list):
    """Get an embedding for each paper use oag-bert model.

        Return the embedding, id_of_mysql, ts for each paper .

        Args:
            d:paper

        Returns:
            Returns embedding, id_of_mysql, ts .
    """
    d = arg_list[0]
    bert_model = arg_list[1]
    embeddings = bert_model[0].get_emb(d).flatten().tolist()
    d_title = {}
    d_title["title"] = d["title"]
    tfidf_embeded = bert_model[1].generate_idf_vector(paper=d_title)[0].tolist()
    embeddings.extend(tfidf_embeded)
    return embeddings, d.get("id_of_mysql"), d.get("ts")

def worker1(d):
    """Get an embedding for each paper use sentence-bert model.

        Return the embedding, id_of_mysql, ts for each paper .

        Args:
            d:paper

        Returns:
            embedding,
            id_of_mysql,
            ts .
    """
    paper_embedding = SBERT_EMb(SBERT_MODEL).get_emb(d[0]).flatten()
    return paper_embedding, d.get("id_of_mysql"), d.get("ts")


def save_nms_result(embeddings, mysql_id_list, ts_list, model):
    """Save the generated embedding and other information to the milvus database.

        Args:
            embeddings:papers embedding
            mysql_id_list:papers mysql_id
            ts_list:papers ts
            model:select table name

    """
    if len(mysql_id_list) == len(embeddings) == len(ts_list):
        entities = [
            mysql_id_list,
            embeddings,
            ts_list
        ]
        if model == "tfidf":
            oagbert_tfidf_embedding.insert(entities)

# @func_exec_time
def load_pub_data_embedding_parallel(data_path, model, cores, limit=-1):
    """Incremental, multi-process training of paper's embedding.

        Args:
            data_path:paper's store place
            model:model name
            cores:the number of processes
            limit:

        Returns:
            embeddings,
            mysql_id_list,
            ts_list .
    """
    embeddings = list()
    mysql_id_list = list()
    ts_list = list()
    papers = list()
    papers_new = list()
    sql_dict = {}
    new_paper_mysqls = list()

    with open(data_path, "r", encoding="utf-8") as f:
        try:
            i = 0
            for line in f:
                if i % 10000 == 0:
                    logger.info(f"read {i}")
                paper = json.loads(line)
                paper_id = paper.get("_id", "")
                id_of_mysql = paper.get("id_of_mysql", -1)
                if paper_id != "" and id_of_mysql != -1:
                    i += 1
                    papers.append(paper)
                    sql_dict[id_of_mysql] = paper
                    new_paper_mysqls.append(id_of_mysql)
                if limit != -1 and i == limit:
                    break
        except Exception as e:
            logger.warning(f"file end exceptional, maybe some other programs are writting the {data_path} file")
        logger.info(f"pub.json total {i} papers")

        res = oagbert_tfidf_embedding.query(expr="pid>0", output_fields=["pid"])
        pid_old = []
        for row in res:
            pid_old.append(row['pid'])

        new_mysql_id = list(set(new_paper_mysqls) - set(pid_old))
        for id in new_mysql_id:
            papers_new.append(sql_dict[id])
        logger.info(f"number of new paper is {len(papers_new)}")
        if len(papers_new) == 0:
            logger.info("no new papers, program exit")
            sys.exit()

        j = 0
        with ProcessPoolExecutor(max_workers=cores) as pool:
            if model == "oag-bert":
                work = worker
            elif model == "tfidf":
                bert_model = [OAG_BERT_Emb(model_path=OAGBERT_MODEL), TfidfGenerator()]
                work = worker_tfidf
                papers_new = [[id,bert_model] for id in papers_new]
            elif model == "sentence-bert":
                work = worker1
            for embedding, mysql_id, ts in pool.map(work, papers_new):
                embeddings.append(np.array(embedding))
                mysql_id_list.append(mysql_id)
                ts_list.append(int(time.mktime(time.strptime(ts, '%Y-%m-%d %H:%M:%S'))))
                j += 1
                if j % 100 == 0:
                    logger.info(f"new paper total {len(papers_new)}, embedd {j}")
                    if j % 1000 == 0:
                        save_nms_result(embeddings, mysql_id_list, ts_list, model)
                        mysql_id_list = []
                        embeddings = []
                        ts_list = []
                        logger.info(f"new paper total {len(papers_new)}, insert {j}")

    return embeddings, mysql_id_list, ts_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='tfidf',
                        help='Select a model from \{oag-bert, sentence-bert, tfidf\}')
    parser.add_argument("--limit", default=-1, type=int)
    parser.add_argument("--cores", default=1, type=int)
    parser.add_argument("--cache", action="store_false")
    parser.add_argument("--load_cache", action="store_false")
    args = parser.parse_args()
    logger.info(args)
    connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
    oagbert_tfidf_embedding = Collection(MILVUS_TFIDF_EMBEEDING)
    oagbert_tfidf_embedding.load()
    embeddings, mysql_id_list, ts_list = load_pub_data_embedding_parallel(data_path=PUB_DATA_PATH,
    model=args.model,
    cores=args.cores,
    limit=args.limit
    )
    if len(embeddings) > 0:
        save_nms_result(embeddings, mysql_id_list, ts_list, args.model)
    logger.info(f"Updated successfully")

