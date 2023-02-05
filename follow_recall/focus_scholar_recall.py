import gzip
import os, sys
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures._base import TimeoutError
base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(base_dir)
import json
import logging
from common.traceback_error import traceback_with_email
from math import exp
import pyssdb
from config import *
from common.mongo_connection import MongoConnection
from common.mongo_service import get_active_users, get_time_and_citations, \
    get_coauthors_by_follow_person, get_authors_by_paperid, get_follow_author, get_latestPapersDic_fromMongo
from tqdm import tqdm
from common.file_util import get_hindex_set

ssdb_connect = pyssdb.Client(SSDB_HOST, SSDB_POST, socket_timeout=60)
publication_col = MongoConnection(AMINER_MONGODB_SETTINGS).get_publication_dupl_col()
coauthors_col = MongoConnection(AMINER_MONGODB_SETTINGS).get_person_coauthors_col()
scholar_pool_col = MongoConnection(AMINER_MONGODB_SETTINGS).get_scholarPool_col()
logger = logging.getLogger("recallApp.focus_scholar_recall")


def distance(ts: str, citation) -> float:
    """Return a distance value through the citations of a paper and TS time
    Args:
        ts:The storay time of paper
        citation:Citations of papers
    Returns:
        distance:A type of float distance
    """
    if citation is None:
        citation = 0
    if ts.__eq__(str(0)):
        ts_index = 0
    else:

        end = time.mktime(time.strptime(ts, '%Y-%m-%d'))

        if end - DISTANCE_START >= 0:
            ts_index = int((end - DISTANCE_START) / (24 * 60 * 60 * 12))
        else:
            ts_index = 0
    if citation > 8000:
        citation = 8000
    distance_index = ts_index + citation
    distance = float(exp((distance_index) / 10000 - 1))
    return distance


def get_high_cite_paper_from_postgre():
    import psycopg2
    logger.info("fetch hindex papers from postgres.")
    conn = psycopg2.connect(database="feature", user="feature_dev", password="howtodoit12345_*&%", host="10.10.0.39",
                            port="5432")
    try:
        curs = conn.cursor()
        # 编写Sql
        sql = 'select * from high_cite_paper'
        # 数据库中执行sql命令
        curs.execute(sql)
        # 获得数据
        data = curs.fetchall()
        data = [x[0] for x in data]
    except Exception as e:
        conn.rollback()
        logger.error(e)

    # 关闭指针和数据库
    curs.close()
    conn.close()
    return data


def hinPapers_to_dic() -> dict:
    """Create a mapping of author id to paper id for the high citation pool

         Returns:
             A dictionary and it's value of key is author id and the value is [paper_id,paper_id,......]
        """
    # paper_ids = get_hindex_set(HINDEX_PAPERS_FILE)
    paper_ids = get_high_cite_paper_from_postgre()
    hindex_author_dic = get_authors_by_paperid(paper_ids,publication_col)
    return hindex_author_dic

def latestPapers_to_dic() -> dict:
    """Create a mapping of author id to paper id for the dynamic pool of scholar
    Returns:A dictionary and it's key is author id and value is [paper_id,paper_id,......]
    """
    newIndex_author_dic = get_latestPapersDic_fromMongo(LATEST_DELTA, scholar_pool_col)

    return newIndex_author_dic

def get_paper_list_without_topic():
    """
    Returns:

    [
        '61d65e0a5244ab9dcbf15e04',
        '61ea249a5244ab9dcbabc756',
        '620c6b6a5aee126c0fe295b9'
    ]
    """
    if not GLOBAL_NEWEST_POOL:
        return []
    if not os.path.isfile(GLOBAL_NEWEST_POOL):
        return []
    latest_temp = []
    text = open(GLOBAL_NEWEST_POOL, "r", encoding="utf-8-sig")
    for line in text.readlines():
        jsonOne = json.loads(line)
        latest_temp.append(jsonOne['pub_id'])
    return latest_temp

def get_papers_by_uids_from_latest_or_hindex(uid: str, dic: dict, label: str) -> list:
    """Return the latest papers or highly cited papers of scholar according to the kind of dict
    Args:
        uid: Id of scholar
        dic: Dictionary of scholar dynamic pool or highly cited papers pool
        label:Types of recalled scholars
    Returns:
        papers_list:List of latest papers
        example:
        [(paper_id,distance,label),(paper_id,distance,label),(paper_id,distance,label)......]
    """
    papers_of_followed_person = []
    if uid in dic.keys():
        papers_of_followed_person.extend(dic[uid])
    else:
        return []
    # De duplication of paper ID list
    papers_of_followed_person = list(set(papers_of_followed_person))

    paper_list = get_time_and_citations(papers_of_followed_person,
                                        publication_col)  # [[paper_id,ts,citation],[paper_id,ts,citation]...]

    for i in range(len(paper_list)):
        paper_list[i] = (
            paper_list[i][0], distance(paper_list[i][1], paper_list[i][2]), label, paper_list[i][2],uid)

    return paper_list


def get_concern_author_papers(concern_au_id: str, hindex_dic: dict, nindex_dic: dict) -> (list, list):
    """Obtain latest paper list and highly cited paper list of followed scholars by the followed scholar's id
    Args:
        concern_authors: Id of followed scholars
        hindex_dic: The dictionary of highly cited papers pool
        nindex_dic: The dictionary of latest papers pool
    Returns:
        concern_high_papers:Highly cited papers of followed scholars
        concern_new_papers:Latest papers of followed scholars
    """
    concern_high_papers = get_papers_by_uids_from_latest_or_hindex(concern_au_id, dic=hindex_dic,
                                                                   label='followed_scholar')
    concern_new_papers = get_papers_by_uids_from_latest_or_hindex(concern_au_id, dic=nindex_dic,
                                                                  label='followed_scholar')
    concern_high_papers = sorted(concern_high_papers, key=lambda paper: paper[1], reverse=True)[
                          :RECALL_NUMBER_OF_HIGH]
    concern_new_papers = sorted(concern_new_papers, key=lambda paper: paper[1], reverse=True)[
                         :RECALL_NUMBER_OF_NEW]
    return concern_high_papers, concern_new_papers


def get_coauthor_papers(concern_au_id: str, author_coauthors_dict:dict,hindex_dic: dict, nindex_dic: dict) -> (list, list):
    """Obtain latest paper list and highly cited paper list of coauthors of followed scholars by the followed scholar's id
    Args:
        concern_authors: ID of followed scholars
        hindex_dic: The dictionary of highly cited papers pool
        nindex_dic: The dictionary of latest papers pool
    Returns:
        coauthors_hindex_papers:Highly cited papers of scholars
        coauthors_new_papers:Latest papers of scholars
    """

    coauthors_hindex_papers = []
    coauthors_new_papers = []
    if concern_au_id in author_coauthors_dict.keys():
        coauthors_uids = author_coauthors_dict[concern_au_id]
    else:
        return [],[]
    for coauthors_uid in coauthors_uids:
        coauthors_Hpapers_list = get_papers_by_uids_from_latest_or_hindex(coauthors_uid, dic=hindex_dic,
                                                                          label='cooperation_scholar')
        coauthors_Npapers_list = get_papers_by_uids_from_latest_or_hindex(coauthors_uid, dic=nindex_dic,
                                                                          label='cooperation_scholar')
        coauthors_hindex_papers.extend(coauthors_Hpapers_list)
        coauthors_new_papers.extend(coauthors_Npapers_list)
    coauthors_hindex_papers = list(set(coauthors_hindex_papers))
    coauthors_new_papers = list(set(coauthors_new_papers))
    coauthors_hindex_papers = sorted(coauthors_hindex_papers, key=lambda paper: paper[1], reverse=True)[
                          :RECALL_NUMBER_OF_HIGH]
    coauthors_new_papers= sorted(coauthors_new_papers, key=lambda paper: paper[1], reverse=True)[
                         :RECALL_NUMBER_OF_NEW]
    return coauthors_hindex_papers, coauthors_new_papers


def get_similar_author_papers(concern_au_id: str, author_sim_dict:dict,hindex_dic: dict, nindex_dic: dict) -> (list, list):
    """Obtain a list of similar scholars' papers by following the list of scholars' ID
    Args:
        concern_authors: ID list of scholars concerned
        hindex_dic: The dictionary of highly cited papers pool
        nindex_dic: The dictionary of latest papers pool
    Returns:
        concern_sim_list:List of papers based on recall of similar scholars
    """
    if concern_au_id in author_sim_dict.keys():
        sim_auids = author_sim_dict[concern_au_id]
    else:
        return [],[]
    sim_hindex_papers = []
    sim_new_papers = []
    for sim_auid in sim_auids:
        sim_hpapers_list = get_papers_by_uids_from_latest_or_hindex(sim_auid, dic=hindex_dic,
                                                                    label='similar_scholar')
        sim_npapers_list = get_papers_by_uids_from_latest_or_hindex(sim_auid, dic=nindex_dic,
                                                                    label='similar_scholar')
        sim_hindex_papers.extend(sim_hpapers_list)
        sim_new_papers.extend(sim_npapers_list)
    sim_hindex_papers = list(set(sim_hindex_papers))
    sim_new_papers = list(set(sim_new_papers))
    sim_hindex_papers = sorted(sim_hindex_papers, key=lambda paper: paper[1], reverse=True)[
                          :RECALL_NUMBER_OF_HIGH]
    sim_new_papers = sorted(sim_new_papers, key=lambda paper: paper[1], reverse=True)[
                         :RECALL_NUMBER_OF_NEW]
    return sim_hindex_papers, sim_new_papers


def papers_list_to_dic_list(papers_list:list,pool_temp:list,papers_pv_dict:dict,papers_zone_dict:dict,authors_name_en_dict:dict,authors_name_zh_dict:dict):
    '''Convert paper ID list to dictionary list
    Args:
        papers_list: List of papers
        [[paper_id,distance,label],[]......]
    Returns:
        papers_dic_list: List of paper Dictionaries
        [[paper_id:" ",distance:" ",label:""],[]......]
    '''

    papers_dic_list = []
    for paper in papers_list:
        paper_dic = {}
        paper_dic["paper_id"] = paper[0]
        paper_dic["distance"] = paper[1]
        paper_dic["label"] = paper[2]
        if paper[0] in pool_temp:
            paper_dic["new"] = True
        else:
            paper_dic["new"] = False
        paper_dic["n_citation"] = paper[3]
        paper_dic["author_id"] = paper[4]
        if paper[4] in authors_name_en_dict.keys():
            paper_dic["author_name_en"] = authors_name_en_dict[paper[4]]
        else:
            paper_dic["author_name_en"] = ""
        if paper[4] in authors_name_zh_dict.keys():
            paper_dic["author_name_zh"] = authors_name_zh_dict[paper[4]]
        else:
            paper_dic["author_name_zh"] = ""
        if paper[0] in papers_pv_dict.keys():
            paper_dic["pv"] = papers_pv_dict[paper[0]]
        else:
            paper_dic["pv"] = 0
        if paper[0] in papers_zone_dict.keys():
            paper_dic["zone"] = papers_zone_dict[paper[0]]
        else:
            paper_dic["zone"] =[]
        papers_dic_list.append(paper_dic)
    return papers_dic_list


def get_papers_by_follow_person(uid: str, concern_authors: list, authors_name_en_dict: dict,author_coauthors_dict:dict,author_sim_dict:dict,  papers_pv_dict:dict,papers_zone_dict:dict,hindex_dic: dict,
                                nindex_dic: dict,latest_temp:list,authors_name_zh_dict:dict) -> dict:
    """Recall papers of three kind of scholars based on followed scholars by user
    Args:
        uid: user id
        concern_authors:List of scholar IDS followed by users
        hindex_dic:{"paper author" : paper_ids} dictionary from high cited
        nindex_dic:{"paper author" : paper_ids} dictionary from scholar_pool
    Returns:
        uid_dic:

    """
    uid_dic = {}
    concern_paper_list = []

    if len(concern_authors) != 0:
        for concern_au_id in concern_authors:
            if concern_au_id in authors_name_en_dict.keys() or concern_au_id in authors_name_zh_dict.keys():
                concern_au_dic = {}
                concern_au_dic['id_of_followed_author'] = concern_au_id
                if concern_au_id in authors_name_en_dict.keys():
                    concern_au_dic['name_of_followed_author'] = authors_name_en_dict[concern_au_id]
                else:
                    concern_au_dic['name_of_followed_author'] = authors_name_zh_dict[concern_au_id]
                if concern_au_id in authors_name_zh_dict.keys():
                    concern_au_dic['chinese_name_of_followed_author'] = authors_name_zh_dict[concern_au_id]
                else:
                    concern_au_dic['chinese_name_of_followed_author'] = authors_name_en_dict[concern_au_id]
                    
                concern_au_dic['papers'] = {}

                # (1) Pay attention to the latest published papers and highly cited papers of scholars
                # 返回最新论文列表和高引论文列表,共50条
                concern_high_list, concern_new_list = get_concern_author_papers(concern_au_id, hindex_dic=hindex_dic,
                                                                                nindex_dic=nindex_dic)

                # (2) 获取关注学者的合作者、师生关系的[(paper_id,distance,label)]50条 ,根据学者的uid获取合作者、师生的uid
                concern_co_high_list, concern_co_new_list = get_coauthor_papers(concern_au_id, author_coauthors_dict,hindex_dic=hindex_dic,
                                                                                nindex_dic=nindex_dic)

                # (3) 获得相似学者的[(paper_id,distance,label)]50条, 根据关注学者uid获得相似学者的uid,之后传入函数
                concern_sim_high_list, concern_sim_new_list = get_similar_author_papers(concern_au_id,author_sim_dict,
                                                                                        hindex_dic=hindex_dic,
                                                                                        nindex_dic=nindex_dic)

                concern_high_papers = concern_high_list + concern_co_high_list + concern_sim_high_list
                concern_new_papers = concern_new_list + concern_co_new_list + concern_sim_new_list

                # concern_au_dic['papers']['highly_cited_papers'] = papers_list_to_dic_list(concern_high_papers,
                #                                                                           latest_temp, papers_pv_dict,
                #                                                                           papers_zone_dict)
                # concern_au_dic['papers']['latest_papers'] = papers_list_to_dic_list(concern_new_papers, latest_temp,
                #                                                                     papers_pv_dict, papers_zone_dict)
                # concern_paper_list.append(concern_au_dic)

                highly_cited_papers_list = papers_list_to_dic_list(concern_high_papers, latest_temp, papers_pv_dict, papers_zone_dict,authors_name_en_dict,authors_name_zh_dict)
                latest_papers_list = papers_list_to_dic_list(concern_new_papers, latest_temp, papers_pv_dict, papers_zone_dict,authors_name_en_dict,authors_name_zh_dict)
                if len(highly_cited_papers_list) > 0:
                    concern_au_dic['papers']['highly_cited_papers'] = highly_cited_papers_list
                if len(latest_papers_list) > 0:
                    concern_au_dic['papers']['latest_papers'] = latest_papers_list
                if concern_au_dic['papers'] != {}:
                    concern_paper_list.append(concern_au_dic)

    else:
        concern_paper_list = []


    uid_dic[uid] = concern_paper_list


    return uid_dic

def delete_old_files():
    '''
        Delete past build files
    '''
    logs_names_list = []
    for day in range(0,LOG_SAVE_DAYS):
        yesterday_tag = (datetime.date.today() - datetime.timedelta(days=day)).strftime("%Y_%m_%d")
        followed_logs_name = f'followed_scholar_recall-{yesterday_tag}.json'
        logs_names_list.append(followed_logs_name)
    for root, dirs, files in os.walk(LOG_SAVE_PATH):
        for filename in files:
            if "followed_scholar_recall" in filename and filename.endswith('.json') and  filename not in logs_names_list:
                os.remove(LOG_SAVE_PATH+filename)
                logger.info(filename + " delete successfully")

@traceback_with_email
def get_papers_by_follow_active_persons(active_start_time, active_end_time):
    """Get the list of active users, and then get the papers recalled by each user
    """
    hindex_dic = hinPapers_to_dic()
    logger.info(f"high_cite_paper load successfully")
    nindex_dic = latestPapers_to_dic()
    logger.info(f"new_papers load successfully")
    latest_temp = get_paper_list_without_topic()
    active_users = get_active_users(active_start_time, active_end_time)
    logger.info(f"find {len(active_users)} active users")
    loop = asyncio.get_event_loop()
    active_users_follow,authors_name_en_dict,author_coauthors_dict,author_sim_dict,papers_pv_dict,papers_zone_dict,authors_name_zh_dict= get_follow_author(loop,active_users,ssdb_connect,hindex_dic, nindex_dic)

    if len(active_users_follow.keys()) > 0:
        with tqdm(total=len(active_users_follow.keys())) as bar:  # total表示预期的迭代次数
            with ThreadPoolExecutor() as ex:
                futures = []
                with open(FOCUS_SCHOLAR_RECALL_PATH, 'w') as f:
                    for k, v in active_users_follow.items():
                        concern_authors = list(set(v))  # List de duplication
                        args = [k, concern_authors, authors_name_en_dict,author_coauthors_dict,author_sim_dict,papers_pv_dict,papers_zone_dict,hindex_dic, nindex_dic,latest_temp,authors_name_zh_dict]
                        futures.append(ex.submit(lambda p: get_papers_by_follow_person(*p), args))
                    try:
                        for future in as_completed(futures, timeout=3600):
                            r = future.result()
                            if r:
                                bar.update(1)  # 每次更新进度条的长度
                            else:
                                continue
                            if len(list(r.values())[0]) >0:
                                json.dump(r, f,ensure_ascii=False)
                                f.writelines("\n")
                    except TimeoutError as e:
                        logger.warning("timeout {}".format(e))

    else:
        logger.info("There are no active users, so can't recall any papers!")
    logger.info("end")


