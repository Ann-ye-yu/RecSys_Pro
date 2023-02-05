import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
import logging
import pymilvus
import requests

from config import PUB_JSON_FILE_PATH, RECALL_TOP_K_FROM_MILVUS, \
    RECALL_TOP_K_FROM_MEILI_SEARCH, KEWORDS_NUMBER_USED_TO_RECALL_SIMILAR_PAPER_FROM_MEILISEARCH
from common.pymilvus_connection import PymilvusConnection


def load_file_from_disk(path=PUB_JSON_FILE_PATH) -> dict:
    """
    :param path:
    :return:
    {
        id_of_mysql: paper_obj, ...
    }
    """
    with open(path, 'r', encoding='utf-8') as f:
        raw_list = f.readlines()
    obj_list = [json.loads(row.strip()) for row in raw_list]
    logging.info('similar_paper_recall: load pub.json from disk!')
    return {obj['id_of_mysql']: obj for obj in obj_list}


def search_similar_paper_by_vector(results: list, collection: pymilvus.orm.collection.Collection,
                                   top_k=RECALL_TOP_K_FROM_MILVUS) -> dict:
    """
    return top_k similar papers from db.
    :param results:
    [{
    pid: int,
    embeded: list,
    }, ...]
    :param collection:
    :param top_k:
        the number of similar paper returned.
    :return:
    """
    # 设置搜索参数
    #     L2: means Euclidean distance.
    #     nprobe: IVF_FLAT将向量数据分成nlist簇单元，
    #     然后比较目标输入向量与每个簇中心的距离。
    #     根据系统设置要查询的簇的数量(nprobe)，
    #     相似性搜索结果只基于目标输入和最相似簇中
    #     的向量之间的比较来返回——这大大减少了查询时间
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    # 1. search by vector
    similar_paper_list = collection.search(
        data=[row['embeded'] for row in results],
        anns_field='embeded',
        param=search_params,
        limit=top_k,
    )
    # 2. sorted results.
    results_sorted_by_distance = dict()
    idx = 0
    for result in similar_paper_list:
        results_sorted_by_distance[results[idx]['pid']] = \
            sorted(zip(result.ids, result.distances), key=lambda d: d[1])
        idx += 1
    return results_sorted_by_distance


def get_similar_paper_from_milvus(pid: int,  collection: pymilvus.orm.collection.Collection):
    """

    Args:
        pid: paper pid, but in pub.json, it will be id_of_mysql.
        collection: target collection in milvus.

    Returns:
        {
        pid : [(pid, distance), (), ....], # the first one is target paper itself.
        }
    """
    # 1. get embedding of target paper by pid.
    logging.info(f"get similar paper from milvus pid={pid}")
    res = collection.query(
        expr=f'pid in {[pid]}',
        output_fields=['pid', 'embeded'],
        consistency_level='Strong',
    )
    # 2. get similar papers by vector.
    results_sorted_by_distance_dict = search_similar_paper_by_vector(res, collection)
    return results_sorted_by_distance_dict


def get_paper_similar_keyword_from_api(content):
    url = "https://nlp.top3-talent.com/extract_keywords"
    payload = json.dumps({
        'texts': [content],
        'lang': 'en'
    })
    headers = {
        'Content-Type': 'application/json'
    }
    resp = requests.request('POST', url, headers=headers,data=payload)
    return [row[0] for row in json.loads(resp.text)['data'][0]]


def get_similar_paper_by_keywords(pid_list: list, pid_mapping_paper_content: dict) -> dict:
    """

    :param pid_list:  a list of pid
    [pid, pid, pid, ..]
    :param pid_mapping_paper_content:
    {
    pid: paper content, ...
    }
    :return:
    {
        pid : [similar paper0, ..., ] #
    }
    """

    similar_paper_dict = dict()
    # 1. 遍历字典内容
    for k, v in pid_mapping_paper_content.items():
        # 2. 若paper存在keywords则直接使用原来的keywords召回相似论文
        keywords = list()
        if 'keywords' in v:
            keywords = v['keywords']
        # 2.1. 不存在则使用接口获取论文的keywords
        if len(keywords) == 0:
            temp_list = list()
            if 'title' in v:
                temp_list.append(v['title'])
            if 'abstract' in v:
                temp_list.append(v['abstract'])
            keywords = get_paper_similar_keyword_from_api(" ".join(temp_list))
        # 3. get similar papers by paper keywords from meiliSearch.
        similar_paper_dict[k] = get_similar_paper_from_meili_search(
            keywords[0:KEWORDS_NUMBER_USED_TO_RECALL_SIMILAR_PAPER_FROM_MEILISEARCH])
    ret_similar_paper = dict()
    # 4. remove the target paper in returned list.
    for k, v in similar_paper_dict.items():
        temp_list = list()
        for obj in v:
            if k not in obj:
                temp_list.append(obj)
        if len(temp_list) == RECALL_TOP_K_FROM_MEILI_SEARCH:
            temp_list = temp_list[:RECALL_TOP_K_FROM_MEILI_SEARCH-1]
        ret_similar_paper[k] = temp_list
    return ret_similar_paper


def get_similar_paper_from_meili_search(keywords, limit=RECALL_TOP_K_FROM_MEILI_SEARCH) -> list:
    """
    get similar paper from meiliSearch.
    :param keywords:  list
        keywords list used to search related papers.
    :param limit: int
        limit the papers number.
    :return: list
    [{
        _id: str,
        tags: list, # ['SCI']
        title: str,
        ...
    }, ]
    """
    url = "http://10.10.0.38:7700/indexes/paper/search"
    payload = json.dumps({
        "attributesToHighlight": [
            "*"
        ],
        "limit": limit,
        "q": " ".join(keywords),

    })
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-HK,zh-CN;q=0.9,zh-TW;q=0.8,zh;q=0.7,en-US;q=0.6,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json'
    }
    resp = requests.request('POST', url, headers=headers, data=payload)
    return json.loads(resp.text)['hits']


def run(pid, pub_json_dict, collection: pymilvus.orm.collection.Collection) -> list:
    """
    get similar papers according to target id.
    Attention, we use two ways to recall similar papers.
    1) recall top5 papers from milvus which have the smaller distances. (calculated by L2)
    2) recall top5 papers from MeiliSearch which relies on keywords to recall similar paper,
        therefore, if a paper does not exist keywords, we also need to calculate the related keywords.
    Args:
        pid: the primary key of a paper.
        pub_json_dict:
        collection: collection in milvus.
    Returns:
        a list of similar papers.
        for example, [recall by keywords(about 5), recall by milvus(about 6, sorted by distance. ASC)]
    """

    # 1. get similar papers from milvus.
    results_sorted_by_distance_dict = get_similar_paper_from_milvus(pid, collection)
    # 2. get similar papers from MeiliSearch.
    similar_papers_recall_by_meili_search_dict = get_similar_paper_by_keywords([pid], {pid: pub_json_dict[pid]})

    return similar_papers_recall_by_meili_search_dict[pid] + \
           [pub_json_dict[row[0]] for row in results_sorted_by_distance_dict[pid][1:]]


if __name__ == '__main__':
    # 1. load pub.json & map as dict. {pid: obj, ...}
    pub_json_obj = load_file_from_disk()
    milvus = PymilvusConnection()
    conn = milvus.get_embedding_collection()
    # 2. get similar papers from milvus&MeiliSearch.
    similar_papers_list = run(pid=526760, pub_json_dict=pub_json_obj, collection=conn)
    conn.release()
    print(similar_papers_list)