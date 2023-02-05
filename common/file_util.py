import gzip
import logging
import json
import os

logger = logging.getLogger("recallAPP.fileutil")
def get_hindex_set_(global_hindex_pool):
    hindex_papers_list = set() #设置一个列表，存放所有高音论文的id
    with gzip.open(global_hindex_pool, "r") as f:
        try:
            for line in f:
                jsonOne = json.loads(line)
                hindex_papers_list.add(jsonOne["_id"])
        except Exception as e:
            logger.warning("hindex file end")
            
    return hindex_papers_list

def get_hindex_set(global_hindex_pool):
    hindex_papers_list = set() #设置一个列表，存放所有高音论文的id
    if not os.path.isfile(global_hindex_pool):
        logger.warning("hindex file not exist")
        return hindex_papers_list
    with open(global_hindex_pool, "r") as f:
        try:
            for line in f:
                jsonOne = json.loads(line)
                hindex_papers_list.add(jsonOne["_id"])
        except Exception as e:
            logger.warning("hindex file end")
            
    return hindex_papers_list