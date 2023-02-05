import concurrent
import datetime
import logging
import time
import aiohttp
import asyncio
import json
from asyncio.log import logger

import pyssdb
import redis
from bson import ObjectId
from dateutil import parser

from common.api_operator import APIOperator
from common.db import PostgresConnection
from common.load_input_log import get_days_list
from common.mongo_connection import MongoConnection
from tqdm import tqdm
from common.config import RETRY_TIMES, WEB_MONGODB_SETTINGS, AMINER_MONGODB_SETTINGS, semaphore, SSDB_HOST, SSDB_POST, REDIS_HOST, \
    REDIS_PORT, REDIS_PASSWORD, INPUT_LOG_DATA,semaphore_ac

from common.config import SIM_AUTHORS_API, SIM_AUTHORS_NUM, COOPERATION_NUM
import concurrent.futures
from multiprocessing.dummy import Pool as ThreadPool

ssdb_client = pyssdb.Client(host=SSDB_HOST, port=SSDB_POST, socket_timeout=60)
redis_connection = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

logger = logging.getLogger("recallApp.mongo")

def multi_thread_exec(f, args_mat, pool_size=5, desc=None):
    if len(args_mat) == 0: return []
    results = [None for _ in range(len(args_mat))]
    with tqdm(total=len(args_mat), desc=desc) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=pool_size) as executor:
            try:
                futures = {executor.submit(f, args): i for i, args in enumerate(args_mat)}
                for future in concurrent.futures.as_completed(futures):
                    i = futures[future]
                    ret = future.result()
                    results[i] = ret
                    pbar.update(1)
            except Exception as e:
                logger.info("Exception {}".format(e))
    return results
    
def get_active_users(active_start_time, active_end_time):
    """
    查询指定时间内的活跃用户
    """
    postgres_operator = PostgresConnection()
    action_list = postgres_operator.get_user_action_log(day_numb=30)
    uid_list = list(set([row[0] for row in action_list if ObjectId.is_valid(row[0])]))
    return uid_list

def get_authors_by_paperid(ids: list,pub_col) -> (dict):
    """Obtain the author ID through the paper ID
        Args:
            ids: paper_ids
        Returns:
            hindex_author_dic: a dict   {author_id:paper_id}
        """
    objectIds = []
    hindex_author_dic = {}
    for index,i in enumerate(ids):
        if ((index+1) % 1000 ==0) or ((index+1) == len(ids)):
            results = pub_col.find({"_id": {"$in": objectIds}},{"authors._id":1})
            for each_paper in results:
                if "authors" in each_paper and each_paper["authors"] is not None:
                    authors = each_paper["authors"]
                    for each_author in authors:
                        if "_id" in each_author and each_author["_id"] is not None:
                            if str(each_author["_id"]) in hindex_author_dic.keys():
                                hindex_author_dic[str(each_author["_id"])].append(str(each_paper["_id"]))
                            else:
                                hindex_author_dic[str(each_author["_id"])] = [str(each_paper["_id"])]
            objectIds = []
        else:
            objectIds.append(ObjectId(i))
    
    return hindex_author_dic
def get_latestPapersDic_fromMongo(LATEST_DELTA, scholar_pool_col) -> dict:
    """Create a mapping of author id to paper id for the dynamic pool of scholar
        Returns:A dictionary and it's key is author id and value is [paper_id,paper_id,......]
        """
    newIndex_author_dic = {}
    # scholar_pool_col.create_index("event_date")
    begin_date = (datetime.date.today() - datetime.timedelta(days=LATEST_DELTA)).strftime("%Y-%m-%d")
    end_date = time.strftime("%Y-%m-%d", time.localtime())
    begin_date = parser.parse(begin_date)
    end_date = parser.parse(end_date)
    results = scholar_pool_col.find(
        {"$and": [{"event_date": {"$gt": begin_date}}, {"event_date": {"$lt": end_date}}]}).batch_size(10)
    for each in results:
        author_id = each['person_id']
        if "event_pub_id" in each.keys() and "event_type" in each.keys():
            if "published".__eq__(each["event_type"]):
                paper_id = each["event_pub_id"]
                if author_id in newIndex_author_dic.keys():
                    newIndex_author_dic[author_id].append(paper_id)
                else:
                    newIndex_author_dic[author_id] = [paper_id]
        else:
            logger.debug(
                "author id {} has missing key of 'event_pub_id' or 'event_type' in dynamic pool!".format(
                    author_id))
    return newIndex_author_dic
async def asyc_get_similar(id):
    '''Asynchronous request for similar information
        Args:
            id: scholar id
        Returns:
            id: scholar id
            sim_auids:List of similar scholars
    '''
    async with semaphore_ac:
        for i in range(RETRY_TIMES):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(SIM_AUTHORS_API + str(id)) as response:
                        if response.status == 200:
                            result = await response.json(content_type=None)
                            sim_auids = []  # ID list of similar scholars
                            similar_au_list = result[:SIM_AUTHORS_NUM]
                            for each_author in similar_au_list:
                                if "id" in each_author:
                                    sim_auids.append(each_author["id"])
                            if i >0:
                                logger.debug("simliar api retry success")
                            return str(id), sim_auids
                        else:
                            return str(id), []
            except Exception as e:
                if i+1 == RETRY_TIMES:
                    logger.warning("all retry failed")
                    return str(id),[]
            

def get_similar(loop,concern_authors):
    '''Obtain a list of similar scholar IDS corresponding to each author in the author ID list
        Args:
            concern_authors: concern_authors list
        Returns:
            sim_dic:{concern_author:List of similar scholars}

    '''
    # loop = asyncio.get_event_loop()
    # asyncio.set_event_loop(loop)
    # # loop = asyncio.get_event_loop()
    async_tasks_func = list()
    for each_concern_author in concern_authors:
        async_tasks_func.append(asyc_get_similar(each_concern_author))

    async_tasks_func_run = list()
    for task in async_tasks_func:
        async_tasks_func_run.append(loop.create_task(task))

    for task in async_tasks_func_run:
        loop.run_until_complete(task)
    sim_dic = {}
    all_similar_author_ids = []
    for task in async_tasks_func_run:
        sim_dic[task.result()[0]] = task.result()[1]
        all_similar_author_ids.extend(task.result()[1])
    return sim_dic,all_similar_author_ids

def get_papers_zone(loop,paper_ids:list)->dict:
    '''Asynchronous request to get the paper and the corresponding partition
    Args:
        ids:list of papers
    Returns:
        papers_zone_dict
        {"paper_id":"zone"}
    '''
    operator = APIOperator()
    async_tasks_func = list()
    for each_paper_id in paper_ids:
        async_tasks_func.append(operator.async_fetch_paper_sci_info(pub_id=each_paper_id))
    async_tasks_func_run = list()
    for task in async_tasks_func:
        async_tasks_func_run.append(loop.create_task(task))
    for task in async_tasks_func_run:
        loop.run_until_complete(task)
    papers_zone_dict = {}
    for task in async_tasks_func_run:
        papers_zone_dict[task.result()[0]] = task.result()[1]
    return papers_zone_dict

def get_papers_pv(pub_ids: list) -> dict:
    id_to_pv_dic = {}
    client = pyssdb.Client(host=SSDB_HOST, port=SSDB_POST, socket_timeout=60)
    redis_connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
    # for pub_id in tqdm(iterable=pub_ids,total=len(pub_ids),desc="get pv"):
    #     key = "PAGE_VIEWED::PUB"
    #     redis_key = "{}:{}".format(key, pub_id)
    #     redis_value = redis_connection.get(redis_key)
    #     if redis_value:
    #         value_temp = bytes.decode(redis_value)
    #         redis_value = int(value_temp)
    #         id_to_pv_dic[pub_id] = redis_value
    #         continue
    #     value = client.zget(key, pub_id)
    #     if not value:
    #         # logger.warning("can't get num viewed for {}, {}".format(key, pub_id))
    #         id_to_pv_dic[pub_id] = 0
    #         continue
    #     # logger.info("pub {} num viewed is {}".format(key, value))
    #     redis_connection.setex(redis_key, 3600 * 24 * 7, value)
    #     id_to_pv_dic[pub_id] = value
    def process(pub_id):
        key = "PAGE_VIEWED::PUB"
        redis_key = "{}:{}".format(key, pub_id)
        redis_value = redis_connection.get(redis_key)
        if redis_value:
            value_temp = bytes.decode(redis_value)
            redis_value = int(value_temp)
            id_to_pv_dic[pub_id] = redis_value
        else:
            value = client.zget(key, pub_id)
            if not value:
                # logger.warning("can't get num viewed for {}, {}".format(key, pub_id))
                id_to_pv_dic[pub_id] = 0
            else:
                # logger.info("pub {} num viewed is {}".format(key, value))
                redis_connection.setex(redis_key, 3600 * 24 * 7, value)
                id_to_pv_dic[pub_id] = value
    results = multi_thread_exec(process,pub_ids,desc="get pv")
    return id_to_pv_dic

def get_papers_pv_(pub_ids: list,ssdb_client,redis_connection) -> dict:
    """
    Return:
    {pubid:pv}
    """
    id_to_pv_dic = {}
    for pub_id in tqdm(iterable=pub_ids,total=len(pub_ids),desc="get pv"):
        key = "PAGE_VIEWED::PUB"
        redis_key = "{}:{}".format(key, pub_id)
        redis_value = redis_connection.get(redis_key)
        if redis_value:
            value_temp = bytes.decode(redis_value)
            redis_value = int(value_temp)
            id_to_pv_dic[pub_id] = redis_value
            continue
        value = ssdb_client.zget(key, pub_id)
        if not value:
            # logger.warning("can't get num viewed for {}, {}".format(key, pub_id))
            id_to_pv_dic[pub_id] = 0
            continue
        # logger.info("pub {} num viewed is {}".format(key, value))
        redis_connection.setex(redis_key, 3600 * 24 * 7, value)
        # if id_to_pv_dic[pub_id]
        id_to_pv_dic[pub_id] = value
    return id_to_pv_dic


async def get_papers_pv_async(loop,executor,pub_ids: list,ssdb_client,redis_connection) -> dict:
    """
    Return:
    {pubid:pv}
    """
    id_to_pv_dic = {}
    def inner(pub_id):
        key = "PAGE_VIEWED::PUB"
        redis_key = "{}:{}".format(key, pub_id)
        redis_value = redis_connection.get(redis_key)
        if redis_value:
            value_temp = bytes.decode(redis_value)
            redis_value = int(value_temp)
            id_to_pv_dic[pub_id] = redis_value
            return
        value = ssdb_client.zget(key, pub_id)
        if not value:
            # logger.warning("can't get num viewed for {}, {}".format(key, pub_id))
            id_to_pv_dic[pub_id] = 0
            return
        # logger.info("pub {} num viewed is {}".format(key, value))
        redis_connection.setex(redis_key, 3600 * 24 * 7, value)
        # if id_to_pv_dic[pub_id]
        id_to_pv_dic[pub_id] = value
    tasks = [loop.run_in_executor(executor,inner,pub_id) for pub_id in pub_ids]
    comleted,pending = await asyncio.wait(tasks)
    return id_to_pv_dic

def get_authors_name(uids):
    '''Query author name
    Args:
        objectIds:

    Returns:
        authors_name_dict:
    '''
    person_col = MongoConnection(AMINER_MONGODB_SETTINGS).get_person_col()
    authors_name_dict = {}
    authors_namez_zh_dict = {}
    for x in tqdm(range(0, len(uids), 1000)):
        sub_ids = uids[x:x + 1000]
        authors_doc = person_col.find({"_id": {"$in": [ObjectId(x) for x in sub_ids]}})
        # for each_author in authors_doc:
        #     if "name" in each_author :
        #         if each_author["name"] != "":
        #             authors_name_dict[str(each_author["_id"])] = str(each_author["name"])
        #     if "name_zh" in each_author:
        #         if each_author["name_zh"] != "":
        #             authors_namez_zh_dict[str(each_author["_id"])] = str(each_author["name_zh"])
        def process(item):
            if "name" in item:
                if item["name"] != "":
                    authors_name_dict[str(item["_id"])] = str(item["name"])
            if "name_zh" in item:
                if item["name_zh"] != "":
                    authors_namez_zh_dict[str(item["_id"])] = str(item["name_zh"])

        pool = ThreadPool()
        pool.map(process, authors_doc)
        pool.close()
        pool.join()
    return authors_name_dict,authors_namez_zh_dict

def iter_fetch_data(batch_size,ids,func,nil_result):
    """iter fetch data use func by batch_size
    Args:
        batch_size:
        ids:
        func: method iterly
        nil_reulst: nil result
    Return:
        result: same type with nil_result
    """
    for x in range(0,len(ids),batch_size):
        sub_ids = ids[x:x+batch_size]
        sub_result = func(sub_ids)
        if isinstance(sub_result,list) and isinstance(nil_result,list):
            list.extend(nil_result,sub_result)
        elif isinstance(sub_result,dict) and isinstance(nil_result,dict):
            dict.update(nil_result,sub_result)
        else:
            raise TypeError("unsupoort action")
    return nil_result


def iter_fetch_follow(batch_size,ids,func,nil_dict,nil_list):
    """iter fetch data use func by batch_size
        Args:
            batch_size:
            ids:
            func: method iterly
            nil_reulst: nil result
        Return:
            result: same type with nil_result
        """
    for x in range(0,len(ids),batch_size):
        sub_ids = ids[x:x+batch_size]
        following_ids_dict,author_ids_list = func(sub_ids)
        dict.update(nil_dict, following_ids_dict)
        list.extend(nil_list, author_ids_list)
    return nil_dict,nil_list

def get_follow_author_(uids):
    results = MongoConnection(AMINER_MONGODB_SETTINGS).get_social_activity_col().find({"uid": {"$in": uids}})
    following_ids_dict = {}
    author_ids_list = []
    for each_id in uids:
        following_ids_dict[each_id] = []
    for x in results:
        following_ids_dict[x["uid"]].extend(x["tids"])
        author_ids_list.extend((x["tids"]))
    return following_ids_dict,author_ids_list

def get_follow_author(loop,uids: list, ssdb_connect,hindex_dic:dict, nindex_dic:dict) -> (dict, dict):
    """Obtain the list of scholars' IDs of interest according to the user ID
    Args:
        uids: User IDs
    Returns:
        following_ids_dict
        authors_dict:{author_id:author_name}
    """

    following_ids_dict,author_ids_list = iter_fetch_follow(1000, uids, get_follow_author_, {},[])
    author_ids_list = list(set(author_ids_list))  # List de duplication
    logger.info("Follow author id list generated successfully")
    author_coauthors_dict,all_coauthors_id = get_coauthors_by_follow_person(author_ids_list, ssdb_connect,MongoConnection(AMINER_MONGODB_SETTINGS).get_person_coauthors_col())
    logger.info("Author ID, coauthors id dictionary generated successfully")
    author_sim_dict,all_similar_author_ids = get_similar(loop,author_ids_list)
    logger.info("Author ID, Similar scholars id dictionary generated successfully")
    all_author_id = author_ids_list + all_coauthors_id + all_similar_author_ids
    authors_name_en_dict,authors_name_zh_dict = get_authors_name(all_author_id)
    logger.info("Author ID, name dictionary generated successfully")
    papers_ids = list()
    for each_author_id in all_author_id:
        if each_author_id in hindex_dic.keys():
            papers_ids.extend(hindex_dic[each_author_id])
        if each_author_id in nindex_dic.keys():
            papers_ids.extend(nindex_dic[each_author_id])
    papers_ids = list(set(papers_ids))
    logger.info(f"follow recall {len(papers_ids)} papers")
    # papers_pv_dict = get_papers_pv(papers_ids)
    papers_pv_dict = {}
    logger.info("Paper ID, pv  dictionary generated successfully")
    # papers_zone_dict = get_papers_zone(loop, papers_ids)
    papers_zone_dict = {}
    logger.info("Paper ID, zone  dictionary generated successfully")
    return following_ids_dict, authors_name_en_dict, author_coauthors_dict, author_sim_dict,papers_pv_dict,papers_zone_dict,authors_name_zh_dict

def get_time_and_citations(ids: list, col) -> (list):
    """Through the list of paper ID, query the database,Obtain information about the paper
    Args:
        ids:List of paper ids
    Returns:
        paper_list:list of [paperid,ts,citation]
        example:
                [[paperid,ts,citation],[paperid,ts,citation]......]
    """
    paper_list = []
    for x in range(0, len(ids), 500):
        sub_ids = ids[x:x + 500]
        results = col.find({"_id": {"$in": [ObjectId(x) for x in sub_ids]}})
        for each in results:
            if "n_citation" in each and each["n_citation"] is not None:
                citation = each["n_citation"]
            else:
                citation = None
            if "ts" in each and each["ts"] is not None:
                time = each["ts"].strftime("%Y-%m-%d")
            else:
                time = str(0)
            paper_list.append([str(each["_id"]), time, citation])
    return paper_list

def get_coauthors_by_follow_person(concern_authors: list, ssdb_connect,person_coauthor_col) -> dict:
    """Query the data table to obtain the list of similar scholars in the database
    Args:
        follow_au_id :list of Concerned scholar ID

    Returns:
        author_coauthors_dict:dict
    """
    author_coauthors_dict = {}
    all_coauthors_id = []
    for x in tqdm(range(0, len(concern_authors), 500)):
        sub_ids = concern_authors[x:x + 500]
        myquery = {"_id": {"$in": [ObjectId(x) for x in sub_ids]}}
        coauthors_info = person_coauthor_col.find(myquery)
        for each_concern_coauthors in coauthors_info:
            coauthors_uids = []
            if each_concern_coauthors is not None and "coauthors" in each_concern_coauthors:
                person_coauthors = each_concern_coauthors["coauthors"]
                # The collaborators are ranked by N, hindex value (cooperation closeness)
                for each_person_coauthor in person_coauthors:
                    if "n" not in each_person_coauthor:
                        each_person_coauthor["n"] = 0
                    if "hindex" not in each_person_coauthor:
                        each_person_coauthor["hindex"] = 0
                person_coauthors_sort = sorted(person_coauthors, key=lambda person_coauthors: (
                person_coauthors["n"], person_coauthors["hindex"]), reverse=True)
                # Slice and take the top ten co authors
                person_coauthors_sort = person_coauthors_sort[:COOPERATION_NUM]
                for each_person_coauthor in person_coauthors_sort:
                    each_person_coauthor_uid = str(each_person_coauthor['id'])
                    if each_person_coauthor_uid != str(each_concern_coauthors["_id"]):
                        coauthors_uids.append(each_person_coauthor_uid)
                author_coauthors_dict[str(each_concern_coauthors["_id"])] = coauthors_uids
                all_coauthors_id.extend(coauthors_uids)

    def process(item):
        coauthors_uids_advisee = []
        key = 'CACHE::EGO::' + str(item)
        if '"boleCode":1' in str(ssdb_connect.get(key)):
            v = json.loads(str(ssdb_connect.get(key), 'utf-8'))
            if 'nodes' in v:
                for each_node in v['nodes']:
                    if each_node['boleCode'] == 1:
                        coauthors_uids_advisee.append(each_node['id'])
        all_coauthors_id.extend(coauthors_uids_advisee)
        if str(item) in author_coauthors_dict.keys():
            coauthors_uids = coauthors_uids_advisee + author_coauthors_dict[str(item)]
            coauthors_uids_duplication = list(set(coauthors_uids))  # List de duplication
            coauthors_uids_duplication.sort(key=coauthors_uids.index)
            coauthors_uids_duplication_num = coauthors_uids_duplication[:COOPERATION_NUM]
            author_coauthors_dict[str(item)] = coauthors_uids_duplication_num
        else:
            author_coauthors_dict[str(item)] = coauthors_uids_advisee

    results = multi_thread_exec(process, concern_authors, desc="get coauthors from ssdb")
    # with tqdm(total=len(concern_authors)) as bar:  # total表示预期的迭代次数
    #     for each_concern_author in concern_authors:
    #         coauthors_uids_advisee = []
    #         key = 'CACHE::EGO::' + str(each_concern_author)
    #         if '"boleCode":1' in str(ssdb_connect.get(key)):
    #             v = json.loads(str(ssdb_connect.get(key), 'utf-8'))
    #             if 'nodes' in v:
    #                 for each_node in v['nodes']:
    #                     if each_node['boleCode'] == 1:
    #                         coauthors_uids_advisee.append(each_node['id'])
    #         all_coauthors_id.extend(coauthors_uids_advisee)
    #         if str(each_concern_author) in author_coauthors_dict.keys():
    #             coauthors_uids = coauthors_uids_advisee + author_coauthors_dict[str(each_concern_author)]
    #             coauthors_uids_duplication = list(set(coauthors_uids))  # List de duplication
    #             coauthors_uids_duplication.sort(key=coauthors_uids.index)
    #             coauthors_uids_duplication_num = coauthors_uids_duplication[:COOPERATION_NUM]
    #             author_coauthors_dict[str(each_concern_author)] = coauthors_uids_duplication_num
    #         else:
    #             author_coauthors_dict[str(each_concern_author)] = coauthors_uids_advisee
    #         bar.update(1)

    all_coauthors_id = list(set(all_coauthors_id))  # List de duplication
    return author_coauthors_dict,all_coauthors_id



