# from cProfile import label
import json
import os.path
from pymongo import MongoClient
from config import *
from common.mongo_connection import MongoConnection
from common.load_input_log import get_days_list
from bson.objectid import ObjectId
from tqdm import tqdm
from pymongo import UpdateOne

logger = logging.getLogger("recallApp.label")
db = MongoConnection(LABEL_MONGODB_SETTINGS).get_db(DB_NAME)
coll = db[COL_NAME]


def get_paper_id_from_pool(high_paper_pool_path: str = HIGH_PAPER_POOL_PATH,
                           latest_paper_pool_abs_path: str = LATEST_PAPER_POOL_PATH,
                           dynamic_scholar_pool_abs_path: str = SCHOLAR_POOL_BAT_PATH,
                           start_time: str = ACTIVE_START_TIME,
                           end_time: str = ACTIVE_END_TIME):
    """
    Args:
        high_paper_pool_path:
        latest_paper_pool_path:
        dynamic_scholar_pool_path:
        start_time:
        end_time:

    Returns:
        pub_ids: [pub_id, ...]
    """
    pub_id_of_high_paper = []
    pub_id_of_latest_paper = []
    pub_id_of_scholar_pool = []
    days_list = get_days_list(start_time, end_time)
    # get paper id of highly cited papers
    if os.path.isfile(high_paper_pool_path):
        with open(high_paper_pool_path, "r", encoding="utf-8") as f:
            try:
                for line in f:
                    line = json.loads(line)
                    if "_id" in line:
                        pub_id_of_high_paper.append(line["_id"])
            except Exception as e:
                logger.warning("read the writting file end")
    else:
        logger.warning("hindex file do not exists")
    #
    if ACTIVE_DELTA == -1:
        days_list = days_list[:-1]

    for day in days_list:
        # get paper id of latest papers
        # YESTERDAY_TAG = (datetime.date.today() - datetime.timedelta(days=day + 1)).strftime("%Y_%m_%d")
        day = day.replace("-", "_")
        latest_paper_pool_path = latest_paper_pool_abs_path + f'/{day}-latest_paper_pool.json'
        dynamic_scholar_pool_path = dynamic_scholar_pool_abs_path + f'/{day}-scholar_pool.json'
        try:
            with open(latest_paper_pool_path, "r", encoding="utf-8") as f:
                try:
                    for line in f:
                        line = json.loads(line)
                        if "pub_id" in line:
                            pub_id_of_latest_paper.append(line["pub_id"])
                except Exception as e:
                    logger.warning("read the writting file end")
        except:
            logger.info(
                f"There is no file path of {latest_paper_pool_path},the reason maybe is {day}-scholar_pool hasn't be generated")
        # get paper id of dynamic scholar pool
        try:
            with open(dynamic_scholar_pool_path, "r", encoding="utf-8") as f:
                try:
                    for line in f.readlines():
                        d = json.loads(line)
                        key = list(d)[0]
                        li = d[key]
                        for i in li:
                            if "pub_id" in i:
                                pub_id_of_scholar_pool.append(i["pub_id"])
                except Exception as e:
                    logger.warning("read the writting file end")
        except:
            logger.info(
                f"There is no file path of {dynamic_scholar_pool_path},the reason maybe is {day}-scholar_pool hasn't be generated")
    return pub_id_of_high_paper + pub_id_of_latest_paper + pub_id_of_scholar_pool


def load_keywords_pool(file: str = KEYWORDS_FILE):
    """加载json文件，返回文件中的keywords的set对象。
    :param file:
    :return:
    """
    # 1. load file.
    try:
        with open(file, "r", encoding="utf-8") as f:
            words_json_list = json.load(f)["words"]
        # 2. look up each json obj.
        keywords_set = set()
        for row in words_json_list:
            if "name" in row.keys():
                keywords_set.add(row["name"])
        # 3. return set.
        return keywords_set
    except Exception as e:
        logger.info(str(e))
        return set()


def format_keywords(word: str):
    return word.replace("-", " ").strip().lower()


def labeled_paper_by_keywords(paper_keywords_list: list, keywords_pools: set):
    """返回paper_keywords_list中存在于keywords_pools的keywords列表。
    :param paper_keywords_list:
    :param keywords_pools:
    :return:
    """
    labeled_list = list()

    for words in paper_keywords_list:

        words = format_keywords(words)

        if words in keywords_pools:
            labeled_list.append(words)
    return labeled_list


def save_json_file(pub_json_list: list, filename=SAVE_FILE_PATH):
    """
    :param pub_json_list:
        json obj format:
            {pub_id: str, keywors: list}
    :param filename:
    :return:
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(pub_json_list, f, indent=3, ensure_ascii=False)


def write_database(json_list: list):
    # test db
    client = MongoClient(host='localhost', port=27017)
    db = client['label']
    coll = db['label']
    with tqdm(total=len(json_list)) as pbar:
        pbar.set_description("Writting data to mongo ")
        for i in range(0, len(json_list), 1000):
            batch_json_list = json_list[i:i + 1000]
            arr = []
            for i, obj in enumerate(batch_json_list):
                id = obj["pub_id"]
                # upsert=True perform an insert if no documents match the filter
                time_str = datetime.datetime.now()
                arr.append(UpdateOne({"_id": ObjectId(id)},
                                     {"$set": {"pub_id": id, "labels": obj["labels"], "modify_time": time_str},
                                      "$setOnInsert": {"create_time": time_str}},
                                     upsert=True))
            coll.bulk_write(arr)
            pbar.update(len(batch_json_list))


def label_paper_by_strong_match():
    pub_id_list = get_paper_id_from_pool()
    pub_json_list = list()  # json list for local store.
    client = MongoConnection(WEB_MONGODB_SETTINGS)  # connect to mongodb
    aminer_client = client.get_db("aminer")
    # 1. load keywords_pool
    keywords_set = load_keywords_pool(file=KEYWORDS_FILE)
    # 2. look up each paper obj. from db.
    with tqdm(total=len(pub_id_list)) as pbar:
        pbar.set_description("Processing")
        for i in range(0, len(pub_id_list), 1000):
            child_pub_id_list = pub_id_list[i:i + 1000]
            sql = {
                "_id": {"$in": [ObjectId(pub_id) for pub_id in child_pub_id_list]}
            }
            cursor = aminer_client.get_collection("publication_dupl").find(sql,
                                                                           {"_id": 1, "keywords": 1},
                                                                           batch_size=1000)  # just select _id & keywords
            for pub_json in cursor:
                # pub_json = cursor.next()
                # 2.1 get paper info.
                # pub_json = client.get_paper_detail_by_pub_id(pub_id)
                # 2.2 labeled this paper.
                labeled_list = list()
                if "keywords" in pub_json.keys():
                    # print(pub_json["keywords"])
                    labeled_list = labeled_paper_by_keywords(pub_json["keywords"], keywords_set)
                # 2.3 add one json obj.
                pub_json_list.append({
                    "pub_id": str(pub_json["_id"]),
                    "keywords": labeled_list,
                })
            # write_database(pub_json_list)
            pbar.update(len(child_pub_id_list))
    write_database(pub_json_list)
    logger.info("Paper label(run.py) program ran successfully!")


if __name__ == '__main__':
    label_paper_by_strong_match()
