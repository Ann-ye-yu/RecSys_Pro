import os
import sys
import datetime
sys.path.append(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])

from bson import ObjectId
from common import WEB_MONGODB_SETTINGS, LABEL_MONGODB_SETTINGS
from common.mongo_connection import MongoConnection, logger
from paper_label.paperl import load_keywords_pool, labeled_paper_by_keywords, write_database
from pathlib import Path

import json

from config import HIGH_PAPER_POOL_PATH, SCHOLAR_POOL_BAT_PATH,SAVE_FILE_PATH, LATEST_PAPER_POOL_PATH, KEYWORDS_FILE, LOAD_PAPER_POOL_FILE_NUMBER_EACH_TIME
from tqdm import tqdm


def generate_paper_pool_abs_path_list():
    # print(os.path.abspath(os.path.join(os.getcwd(), "..")))
    latest_paper_abs_path = list()
    scholar_pool_abs_path = list()
    high_paper_pool_abs_path = list()
    if Path(LATEST_PAPER_POOL_PATH).exists():
        latest_paper_abs_path = [os.path.join(LATEST_PAPER_POOL_PATH, row) for row in os.listdir(LATEST_PAPER_POOL_PATH)]
    else:
        logger.info(f"{LATEST_PAPER_POOL_PATH} not exists.")
    if Path(SCHOLAR_POOL_BAT_PATH).exists():
        scholar_pool_abs_path = [os.path.join(SCHOLAR_POOL_BAT_PATH, row) for row in os.listdir(SCHOLAR_POOL_BAT_PATH)]
    else:
        logger.info(f"{SCHOLAR_POOL_BAT_PATH} not exists.")

    if Path(HIGH_PAPER_POOL_PATH).exists():
        high_paper_pool_abs_path = [HIGH_PAPER_POOL_PATH]
    else:
        logger.info(f"{HIGH_PAPER_POOL_PATH} not exists.")

    return latest_paper_abs_path + scholar_pool_abs_path + high_paper_pool_abs_path


def parse_latest_paper_file(path):
    ids_list = list()
    with open(path, "r", encoding="utf-8") as f:
        for row in f.readlines():
            ids_list.append(eval(row)["pub_id"])
    return ids_list


def parse_scholar_pool(path):
    ids_list = list()
    with open(path, "r", encoding="utf-8") as f:
        for row in f.readlines():
            papers = list(json.loads(row).values())[0]
            for p in papers:
                # print(p)
                if "pub_id" in p.keys():
                    ids_list.append(p["pub_id"])
    return ids_list


def parse_high_paper_pool(path: str):
    ids_list = list()
    with open(path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            line = json.loads(line)
            if "_id" in line:
                ids_list.append(line["_id"])
    return ids_list


def get_pub_id_by_load_file(path_list: list):

    pub_id_list = list()
    for path in path_list:
        if "latest_paper_pool.json" in path:
            pub_id_list += parse_latest_paper_file(path)
        elif "scholar_pool.json" in path:
            pub_id_list += parse_scholar_pool(path)
        elif "pub.json" in path:
            pub_id_list += parse_high_paper_pool(path)
    return pub_id_list


def main(paper_pool_abs_path_list):
    # 1.1. load key
    keywords_set = load_keywords_pool(file=KEYWORDS_FILE)

    # 1.2 connect to aminer db.
    client = MongoConnection(WEB_MONGODB_SETTINGS)  # connect to mongodb
    aminer_client = client.get_db("aminer")
    # 2. load json file
    for i in range(0, len(paper_pool_abs_path_list), LOAD_PAPER_POOL_FILE_NUMBER_EACH_TIME):
        # 2.1 remember pub_id
        temp_abs_path = paper_pool_abs_path_list[i:i + LOAD_PAPER_POOL_FILE_NUMBER_EACH_TIME]
        pub_id_list = get_pub_id_by_load_file(temp_abs_path)
        logger.info(f"{temp_abs_path} has {len(pub_id_list)} papers")
        pub_json_list = list()
        with tqdm(total=len(pub_id_list)) as pbar:
            pbar.set_description(f"Papers needed label: ")
            # 2.2 search keywords by pub_id in db
            for i in range(0, len(pub_id_list), 1000):
                sql = {
                    "_id": {"$in": [ObjectId(pub_id) for pub_id in pub_id_list[i:i + 1000]]}
                }
                cursor = aminer_client.get_collection("publication_dupl").find(sql,
                                                                               {"_id": 1, "keywords": 1},
                                                                               batch_size=100)  # just select _id & keywords
                # look up each result.
                for pub_json in cursor:
                    # 2.3 labeled this paper
                    labeled_list = list()
                    if "keywords" in pub_json.keys():
                        labeled_list = labeled_paper_by_keywords(pub_json["keywords"], keywords_set)
                    # 2.4 add one json result.
                    pub_json_list.append({
                        "pub_id": str(pub_json["_id"]),
                        "keywords": labeled_list,
                    })
                pbar.update(len(pub_id_list[i:i + 1000]))
        # 2.4 update database
        write_database(pub_json_list)
        logger.info("Paper label(cold_start) program ran successfully!")


if __name__ == '__main__':
    # 1. paper pool absolute path list!
    paper_pool_abs_path_list = generate_paper_pool_abs_path_list()
    if len(paper_pool_abs_path_list) == 0:
        logger.warning("There are none paper pool json's files in disk")
    else:
        main(paper_pool_abs_path_list)