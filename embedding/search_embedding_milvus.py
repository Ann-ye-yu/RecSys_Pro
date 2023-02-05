import json
import time
from collections import defaultdict
import datetime
import argparse
from embedding.get_paper_embedding.paper_emb.sentence_bert import SBERT_EMb
from embedding.get_paper_embedding.paper_emb.oagbert import OAG_BERT_Emb
from embedding.config import *
from common.misc import func_exec_time
from pymilvus import (
    connections,
    Collection,
)
import os
import sys

from embedding.tfidf_for_oagbert import TfidfGenerator

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
logger = logging.getLogger("recallApp.embedding")

connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
oagbert_embedding = Collection(MILVUS_OAG_EMBEEDING)
oagbert_embedding.load()
tfidf_embedding = Collection(MILVUS_TFIDF_EMBEEDING)
tfidf_embedding.load()
# @func_exec_time
def get_smiliar_papers_by_topic(args):
    topic, bert_model, index2paper, num, model=args[0],args[1],args[2],args[3],args[4]
    """get similar papers by topic.

        Args:
            topic:topic
            bert_model:embedding model
            index2paper:pubs.json
            num:the number of return similar papers
            model:model name

        Returns:
            paper_ids,
            similar score.
        """
    date = datetime.datetime.now() - datetime.timedelta(days=SEARCH_DAYS)
    ts_filter = int(time.mktime(date.timetuple()))
    expr = f"ts >= {ts_filter}"
    search_params = {
        "metric_type": "l2",
        "params": {"nprobe": 10},
        "expr": expr,
    }

    if model == "oag-bert":
        topic = {"title": topic}
        embeddings = [bert_model.get_emb(topic).tolist()]
        result = oagbert_embedding.search(embeddings, "embeded", search_params, limit=num)
    else:
        sentencebert_embedding = Collection(MILVUS_SBERT_EMBEEDING)
        embeddings = [bert_model.get_emb(topic).tolist()]
        sentencebert_embedding.load()
        result = sentencebert_embedding.search(embeddings, "embeded", search_params, limit=num)
    for hits in result:
        paper_ids = list()
        score = list()
        for hit in hits:
            if hit.id in index2paper:
                paper_ids.append(index2paper[hit.id])
                score.append(hit.score)
    return paper_ids, score,topic

def get_smiliar_papers_by_topic_mutil(arg_list):
    """get similar papers by topic.

        Args:
            topic:topic
            bert_model:embedding model
            index2paper:pubs.json
            num:the number of return similar papers
            model:model name

        Returns:
            paper_ids,
            similar score.
        """
    topic, bert_model, index2paper, num, model,paper_id=arg_list[0],arg_list[1],arg_list[2],arg_list[3],arg_list[4],arg_list[5]
    date = datetime.datetime.now() - datetime.timedelta(days=SEARCH_DAYS)
    ts_filter = int(time.mktime(date.timetuple()))
    expr = f"ts >= {ts_filter}"
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
        "expr": expr,
    }

    if model == "oag-bert":
        topic = {"title": topic}
        embeddings = [bert_model.get_emb(topic).tolist()]
        result = oagbert_embedding.search(embeddings, "embeded", search_params, limit=num)
    else:
        sentencebert_embedding = Collection(MILVUS_SBERT_EMBEEDING)
        embeddings = [bert_model.get_emb(topic).tolist()]
        sentencebert_embedding.load()
        result = sentencebert_embedding.search(embeddings, "embeded", search_params, limit=num)
    for hits in result:
        paper_ids = list()
        score = list()
        for hit in hits:
            if hit.id in index2paper:
                paper_ids.append(index2paper[hit.id])
                score.append(hit.score)
    return paper_id, paper_ids, score


# @func_exec_time
def get_topics_embedding_from_oagbert(topics_list:list,models):
    """get topics embedding use oag-bert.

        Args:
            topics_list:a list of topic
            oag_bert_model:oag bert model

        Returns:
            topic2embedding.
    """
    topic2embedding=defaultdict(list)
    for item_topic in topics_list:
        topic = {"title": item_topic}
        try:
            # embeddings = oag_bert_model.get_emb(topic).tolist()
            embeddings = models[0].get_emb(topic).tolist()
            tfidf_embeded = models[1].generate_idf_vector(paper=topic)[0]
            embeddings.extend(tfidf_embeded)
            topic2embedding[item_topic]=embeddings
        except Exception as e:
            print(f"Getting embedding of the topic   {item_topic}  failed!")
            print(e)

    return topic2embedding


@func_exec_time
def init_env(model):
    """init env.

        Args:
            model:bert model name

        Returns:
            bert_model:bert model.
            papers:pub.json
    """
    papers = dict()
    with open(PUB_DATA_PATH, "r", encoding="utf-8") as f:
        try:
            for line in f:
                paper = json.loads(line)
                paper_id = paper.get("_id", "")
                paper_pid = paper.get("id_of_mysql", "")
                if paper_id != "":
                    papers[paper_pid] = paper_id
        except Exception as e:
            logger.warning(f"file end exceptional, maybe some other programs are writting the {PUB_DATA_PATH} file")
    if model == "sentence-bert":
        bert_model = SBERT_EMb(model_path=SBERT_MODEL)
    if model == "oag-bert":
        bert_model = OAG_BERT_Emb(model_path=OAGBERT_MODEL)
    if model == "tfidf":
        bert_model = [0,0]
        bert_model[0] = OAG_BERT_Emb(model_path=OAGBERT_MODEL)
        bert_model[1] = TfidfGenerator()
    return  bert_model, papers

# subscribe_oag
def get_smiliar_papers_subscribe_oag(args):
    topic, bert_model, index2paper, num, model=args[0],args[1],args[2],args[3],args[4]
    """get similar papers by topic.

        Args:
            topic:topic
            bert_model:embedding model
            index2paper:pubs.json
            num:the number of return similar papers
            model:model name

        Returns:
            paper_ids,
            similar score.
        """

    date = datetime.datetime.now() - datetime.timedelta(days=SEARCH_DAYS)
    ts_filter = int(time.mktime(date.timetuple()))
    expr = f"ts >= {ts_filter}"
    search_params = {
        "metric_type": "l2",
        "params": {"nprobe": 10},
        "expr": expr,
    }

    if model == "oag-bert":
        topic = {"title": topic}
        embeddings = [bert_model.get_emb(topic).tolist()]
        result = oagbert_embedding.search(embeddings, "embeded", search_params, limit=num)
    elif model=="tfidf":
        topic = {"title": topic}
        try:
            embeddings = bert_model[0].get_emb(topic).tolist()
        except Exception as e:
            topic = {"title": "unknown"}
            embeddings = bert_model[0].get_emb(topic).tolist()
        tfidf_embeded = bert_model[1].generate_idf_vector(paper=topic)[0]
        embeddings.extend(tfidf_embeded)
        result = tfidf_embedding.search([embeddings], "embeded", search_params, limit=num)
    else:
        sentencebert_embedding = Collection(MILVUS_SBERT_EMBEEDING)
        embeddings = [bert_model.get_emb(topic).tolist()]
        sentencebert_embedding.load()
        result = sentencebert_embedding.search(embeddings, "embeded", search_params, limit=num)
    for hits in result:
        paper_ids = list()
        score = list()
        for hit in hits:
            if hit.id in index2paper:
                paper_ids.append(index2paper[hit.id])
                score.append(hit.score)
    return paper_ids, score,topic

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='oag-bert',
                        help='Select a model from \{oag-bert, sentence-bert\}')
    parser.add_argument("--topk", default=10, type=int)
    parser.add_argument("--topic", default="machine learning", type=str)
    args = parser.parse_args()
    logger.info(args.topic)
    bert_model, index2paper = init_env(args.model)
    neighbours = get_smiliar_papers_by_topic(args.topic, bert_model, index2paper, args.topk, args.model)
    logger.info(neighbours)
