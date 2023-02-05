import asyncio
from asyncio.log import logger
import time

import aiohttp
from async_timeout import timeout

import config
import json
import requests
import logging

semaphore_faiss = asyncio.Semaphore(15)
logger = logging.getLogger("recallApp.APIOperator")
class APIOperator:
    """Handle network requests, generate tokens, access APIs,
    and return content.
    """
    data_token = None  # store token
    create_at = None  # start at! 

    def __init__(self):
        self.create_at = time.time()
        self.fetch_data_token()

    def fetch_scholar_pool(self, start_time, end_time, offset):
        """According to the pub_id returns the sci strength
        information of the paper.

        Args:
            end_time:
            start_time:
            offset:

        Returns:
        """

        if not self.data_token:
            self.fetch_data_token()
        if not self.data_token:
            print("token is null")
            return {}
        if self.time_interval_scholar():
            # print("更新token令牌")
            self.fetch_data_token()

        url = "http://gateway.private.aminer.cn/private/api/v2/paper/na_pubs"
        params = {"start_time": start_time, "end_time": end_time, "offset": offset, "limit": 100}
        header = {
            "Authorization": "Bearer {}".format(self.data_token),
            "accept": "application/json"
        }
        r = requests.get(url, params, headers=header)
        # print(r.status_code)
        logging.debug(r.status_code)
        return r.text

    def fetch_data_token(self):
        """get token first.
        """
        url = "https://oauth.aminer.cn/api/v2/oauth/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": "a227299c-0fa4-4cbe-95a8-a8af7ce4837c",
            "client_secret": "db74429f-8a68-4e33-8dc9-a2349bfac401",
            "login_type": "login",
            "kind": "1",
            "username": "aminer",
            "password": "a2f24a50-8c49-4572-90c1-017339b51a9c",
        }
        header = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        r = requests.post(url, data=params, headers=header)
        if r.status_code != 200:
            print("fetch {}, params {}, response status code {} "
                  "is not 200".format(url, params, r.status_code))
            return
        self.create_at = time.time()
        self.data_token = r.json()["access_token"]

    async def fetch_data_token_async(self,session):
        """get token first.
        """
        url = "https://oauth.aminer.cn/api/v2/oauth/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": "a227299c-0fa4-4cbe-95a8-a8af7ce4837c",
            "client_secret": "db74429f-8a68-4e33-8dc9-a2349bfac401",
            "login_type": "login",
            "kind": "1",
            "username": "aminer",
            "password": "a2f24a50-8c49-4572-90c1-017339b51a9c",
        }
        header = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        async with session.post(url, data=params, headers=header) as r:
            if r.status != 200:
                print("fetch {}, params {}, response status code {} "
                    "is not 200".format(url, params, r.status_code))
                return
            self.create_at = time.time()
            self.data_token = r.json()["access_token"]

    def time_interval_scholar(self):
        """The token will be updated every fifteen hours
        Returns:

        """
        if time.time() - self.create_at >= config.CYCLE_OF_UPDATE_TOKEN_SCHOLAR:
            return True
        return False

    def time_interval(self):
        """The token will be updated every fifteen hours
        Returns:

        """
        if time.time() - self.create_at >= config.CYCLE_OF_UPDATE_TOKEN:
            return True
        return False

    def fetch_paper_sci_info(self, pub_id: str) -> str:
        """According to the pub_id returns the sci strength
        information of the paper.

        Args:
            pub_id:

        Returns:
        """

        if not self.data_token:
            self.fetch_data_token()
        if not self.data_token:
            print("token is null")
            return {}

        if self.time_interval():
            # print("更新token令牌")
            self.fetch_data_token()

        url = "http://gateway.private.aminer.cn/private/api/v2/venue/SCIQ"

        params = {"id": pub_id}
        header = {
            "Authorization": "Bearer {}".format(self.data_token),
            "accept": "application/json",
        }
        r = requests.get(url, params, headers=header)
        # print(r.status_code)
        logging.debug(r.status_code)
        return r.json()["data"]

    async def async_fetch_paper_sci_info(self, pub_id: str):

        if not self.data_token:
            self.fetch_data_token()
        if not self.data_token:
            print("token is null")
            return pub_id,[]
        if self.time_interval():
            # print("更新token令牌")
            self.fetch_data_token()
        url = "http://gateway.private.aminer.cn/private/api/v2/venue/SCIQ"
        params = {"id": pub_id}
        header = {
            "Authorization": "Bearer {}".format(self.data_token),
            "accept": "application/json",
        }
        async with config.semaphore_zone:
            async with aiohttp.ClientSession(headers=header) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json(content_type=None)
                        result = data["data"]
                        if result is not None:
                            k, v = result.popitem()
                            return pub_id,v
                        else:
                            return pub_id,[]
                    else:
                        return pub_id,[]

    def fetch_pub_venue(self, venue: str):
        """
        :param venue:
        :return:
            {
                Name: str,
                Short: str
            }
        """
        if not self.data_token:
            self.fetch_data_token()

        if not self.data_token:
            print("token is null")
            return {}

        url = "https://test-datacenter.aminer.cn/api/v1/venue/short"
        params = {"alias": venue}
        header = {
            "Authorization": "Bearer {}".format(self.data_token),

        }
        r = requests.get(url, params, headers=header)
        return r.json()['data']

    def fetch_paper_list(self,paper_title=None,paper_keywords=None,golbal_faiss_query_for_recall_paper_count=100):
    
        if not self.data_token:
            self.fetch_data_token()
        if not self.data_token:
            print("token is null")
            return {}

        if self.time_interval():
            self.fetch_data_token()

        paper_title="machine"

        if paper_keywords == None:
            payload = json.dumps({
                "pub": {
                    "title": paper_title

                },
                "count": golbal_faiss_query_for_recall_paper_count
            })
            #print('只有一个关键词')
        else:
            payload = json.dumps({
                "pub": {
                    "title": paper_title,
                    "keywords": paper_keywords
                },
                "count": golbal_faiss_query_for_recall_paper_count
            })
            #print('有俩个关键词')

        #print('传送token：',self.data_token)
        headers = {
            "Authorization": "Bearer {}".format(self.data_token),
            "accept": "application/json",
        }

        #print(payload)
        global_faiss_query_for_recall_url='http://10.30.0.118/recall/'
        response = requests.request("POST", global_faiss_query_for_recall_url, headers=headers, data=payload)
        if response.status_code==200:
            result_get = json.loads(response.text)
            result_papers = result_get['papers']
            return result_papers
        else:
            print('faiss_query_for_recall,failed!')
            print(response.text)
            faiss_wrong=[]
            return faiss_wrong


async def get_faiss_paper_list(session,url,count,paper_title=None, paper_keywords=None):
    '''
    根据订阅的领域来获取相似的论文列表(根据单个关键词)
    输入:文章title(必填项)，文章的keywords(选填项)
    输出[相似文章的id,distance]
    '''
    """
    根据订阅的领域来获取相似的论文列表。
    相似领域论文的获得接口为:"http://10.10.0.30/recall/"
    Args:
        paper_title: 接口需要的文章title参数，此处可以传入关键词。（必填项）
        paper_keywords: 接口需要的文章 keywords 参数，此处需要传入关键词。（选填项）
    Returns:
        输出[相似文章的id,distance]
        For example:
        [
            ('61dcf5485244ab9dcb1fb505', 18.0), 
            ('61e7cb03d18a2b1f275826c9', 19.0), 
        ]
    """
    if paper_title== None or paper_title.strip() == "":
        return {}
    if paper_keywords == None:
        payload = json.dumps({
            "pub": {
                "title": paper_title
            },
            "count": count
        })

    else:
        payload = json.dumps({
            "pub": {
                "title": paper_title,
                "keywords":[paper_keywords]
            },
            "count": count
        })

    headers = {
        'Content-Type': 'text/plain'
    }
    async with semaphore_faiss:
        async with session.post(url,headers=headers,data=payload) as response:
            if response.status == 200:
                text = await response.text()
                result_get = json.loads(text)
                if result_get.get("papers"):
                    logger.warning(f"faiss recall {paper_title} result no papers")
                result_papers = result_get.get('papers',[])
                return {paper_title:result_papers}
            else:
                logger.warning(f'faiss_query_for_recall,failed-{response.status} -{payload}')
                return {}






