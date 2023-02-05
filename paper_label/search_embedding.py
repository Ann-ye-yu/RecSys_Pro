import json
import os, sys
abs_path = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(abs_path))
sys.path.append(root_path)
# import nmslib
from paperl import *
from common.load_input_log import get_days_list
from embedding.get_paper_embedding.paper_emb.oagbert import OAG_BERT_Emb
from config import *
from pymilvus import Collection
from common.misc import func_exec_time
import argparse
logger = logging.getLogger("recallApp.embedding")
from pymilvus import connections


def delete_None_in_paper(paper):
    paper_keys = paper.keys()
    for key in paper_keys:
        value = paper[key]
        if isinstance(value,str) and value==None:
            paper[key] = ""
        elif isinstance(value,list):
            for i in range(len(value)):
                if value[i]==None:
                    del value[i]
    return paper


def get_paper_topic_by_mivlus(collection, paper_list, oag_bert_model, top_k:int=2):
    paper_emb_list = [oag_bert_model.get_emb(paper) for paper in paper_list]
    search_params = {"metric_type": MILVUS_METRIC_TYPE_FOR_SEARCH,
                     "params": {"nprobe": MILVUE_NPROBE_FOR_SEARCH}}
    results = collection.search(
        data= paper_emb_list,  # paper embedding
        anns_field=MIVLUS_SUBJECT_COLLECTION_EMB_FIELD_NAME,  # field name used for search.
        param=search_params,
        limit=top_k,
    )

    return results


# @func_exec_time
def get_scholar_pool_papers(pub_id_of_scholar_pool):
    client = MongoConnection(WEB_MONGODB_SETTINGS)  # connect to mongodb
    aminer_client = client.get_db("aminer")
    papers = []
    for i in range(0, len(pub_id_of_scholar_pool), 100):
        child_pub_id_list = pub_id_of_scholar_pool[i:i+100]
        sql = {
            "_id": {"$in": [ObjectId(pub_id) for pub_id in child_pub_id_list]}
        }
        cursor = aminer_client.get_collection("publication_dupl").find(sql,{"_id":1,"keywords":1,"title":1},batch_size=100)
        for pub_json in cursor:
            paper_dic = {}
            if "title" in pub_json.keys():
                if "keywords" in pub_json.keys():
                    paper_dic["keywords"] = pub_json["keywords"]
                paper_dic["title"] = pub_json["title"]
                paper_dic["pub_id"] = pub_json["_id"]
            else:
                paper_id = pub_json["_id"]
                logger.warning(f"there is no title of the paper{paper_id} in publication_dupl coll")
            papers.append(paper_dic)
    return papers


# @func_exec_time
def get_papers_from_pool(high_paper_pool_path: str = HIGH_PAPER_POOL_PATH,
                           latest_paper_pool_abs_path: str = LATEST_PAPER_POOL_PATH,
                           dynamic_scholar_pool_abs_path: str = SCHOLAR_POOL_BAT_PATH,
                           start_time: str = ACTIVE_START_TIME,
                           end_time: str = ACTIVE_END_TIME):
    # print("*"*20)
    # print(high_paper_pool_path)
    # print(latest_paper_pool_abs_path)
    # print(dynamic_scholar_pool_abs_path)
    # print("*" * 20)
    papers_of_high_paper = []
    papers_of_latest_paper = []
    pub_id_of_scholar_pool = []
    days_list = get_days_list(start_time,end_time)
    if os.path.isfile(high_paper_pool_path):
        with open(high_paper_pool_path, "r", encoding="utf-8") as f:
            try:
                for line in f:
                    paper = json.loads(line)
                    paper = delete_None_in_paper(paper)
                    papers_of_high_paper.append(paper)
            except Exception as e:
                logger.warning("read the writting file end")
    else:
        logger.warning("hindex file do not exists")

    if ACTIVE_DELTA == -1:
        days_list = days_list[:-1]

    for day in days_list:
        # get paper  of latest papers
        day = day.replace("-", "_")
        latest_paper_pool_path = latest_paper_pool_abs_path + f'/{day}-latest_paper_pool.json'
        dynamic_scholar_pool_path = dynamic_scholar_pool_abs_path + f'/{day}-scholar_pool.json'
        try:
            with open(latest_paper_pool_path, "r", encoding="utf-8") as f:
                try:
                    for line in f:
                        paper = json.loads(line)
                        paper = delete_None_in_paper(paper)
                        papers_of_latest_paper.append(paper)
                except Exception as e:
                    logger.warning("read the writting file end")
        except:
            logger.warning(
                f"There is no file path of {latest_paper_pool_path},the reason maybe is {day}-latest_pool hasn't be generated")
        # get paper id of dynamic scholar pool
        try:
            with open(dynamic_scholar_pool_path, "r", encoding="utf-8") as f:
                try:
                    for line in f.readlines():
                        d = json.loads(line)
                        key = list(d)[0]
                        li = d[key]
                        for i in li:
                            if "event_pub_id" in i:
                                pub_id_of_scholar_pool.append(i["event_pub_id"])
                except Exception as e:
                    logger.warning("read the writting file end")
        except:
            logger.warning(
                f"There is no file path of {dynamic_scholar_pool_path},the reason maybe is {day}-scholar_pool hasn't be generated")
    papers_of_scholar_pool = get_scholar_pool_papers(pub_id_of_scholar_pool)
    return papers_of_high_paper,papers_of_latest_paper,papers_of_scholar_pool


def load_ids2subject_words_dict_from_disk(path:str=IDS2SUBJECT_WORDS_FILE_PATH):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def tqdm_labeled_paper(paper_list, collection, oag_bert_model, ids2subject_words_dict, desc:str, pub_id='_id'):
    pub_json_list = list()
    with tqdm(total=len(paper_list)) as pbar:
        pbar.set_description(desc)
        for ids in range(0, len(paper_list), LABELED_PAPERS_NUMBERS_EACH_TIME):
            results_list = get_paper_topic_by_mivlus(collection, paper_list[ids:ids+LABELED_PAPERS_NUMBERS_EACH_TIME], oag_bert_model)
            for i in range(len(results_list)):
                # print(paper_list[ids+i]['_id'], [ids2subject_words_dict[str(j)] for j in results_list[i].ids])
                pub_json_list.append({
                    'pub_id': paper_list[ids + i][pub_id],
                    'labels': [ids2subject_words_dict[str(j)] for j in results_list[i].ids],
                })
            pbar.update(len(results_list))
    return pub_json_list


def label_paper_by_oag():
    pub_json_list = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--topk", default=2, type=int)
    args = parser.parse_args()
    # 0. load ids2subject_words from disk.
    ids2subject_words_dict = load_ids2subject_words_dict_from_disk()
    # 1. load oag-bert from disk.
    oag_bert_model = OAG_BERT_Emb(OAGBERT_MODEL)
    # 2. connect to milvus collection which is used for recalling paper subject.
    connections.connect(alias='default', host=MILVUS_DB_HOST, port=MILVUS_DB_PORT)
    collection = Collection(COLLECTION_NAME)
    # 2.1 load target collection.
    collection.load()
    # 3. get paper from pool included [high-cited, scholar-pool, latest-paper]
    papers_of_high_cited, papers_of_latest, papers_of_scholars = get_papers_from_pool()

    pub_json_list += tqdm_labeled_paper(paper_list=papers_of_high_cited, collection=collection,
                                        oag_bert_model=oag_bert_model,
                                        ids2subject_words_dict=ids2subject_words_dict,
                                        desc="labeling the high cited papers ")
    pub_json_list += tqdm_labeled_paper(paper_list=papers_of_latest, collection=collection,
                                        oag_bert_model=oag_bert_model,
                                        ids2subject_words_dict=ids2subject_words_dict,
                                        desc="labeling the latest papers ", pub_id='pub_id')
    pub_json_list += tqdm_labeled_paper(paper_list=papers_of_scholars, collection=collection,
                                        oag_bert_model=oag_bert_model,
                                        ids2subject_words_dict=ids2subject_words_dict,
                                        desc="labeling the papers of scholars ", pub_id='pub_id')

    # 3. write db.
    write_database(pub_json_list)
    collection.release()
    connections.disconnect(alias='default')


if __name__ == "__main__":
    label_paper_by_oag()