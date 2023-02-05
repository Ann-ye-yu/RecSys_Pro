import asyncio
import datetime
import json
import logging
import os
import sys

import aiohttp

from common import config
from common.config import semaphore, INPUT_LOG_DATA

logger = logging.getLogger("recallApp.load_input_log")

def get_days_list(date_start_str: str, date_end_str: str) -> list:
    """Get day_str list over 30 days

       Args:
           date_start_str:start time
           date_end_str:end time

       Returns:
           list:The day_str list

       """
    days_list = []
    date_start = datetime.datetime.strptime(date_start_str + " 0:0:0", "%Y-%m-%d %H:%M:%S")
    date_end = datetime.datetime.strptime(date_end_str + " 0:0:0", "%Y-%m-%d %H:%M:%S")
    if date_start <= date_end:
        while date_start <= date_end:
            date_str = date_start.strftime("%Y-%m-%d")
            days_list.append(date_str)
            date_start += datetime.timedelta(days=1)
        return days_list
    else:
        logger.warning("The start time should be less than the end time")
        return days_list

async def get_hot_list(day_str):
    """Get hot_list by day_str list, Access APIs asynchronously

           Args:
               day_str:list

           Returns:
               list:The hot_list(items)

           """
    hot_list = []
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            input_url = config.INPUT_LOG_URL + day_str + "-log.json"
            async with session.get(input_url, timeout=999999) as resp:
                try:
                    resp = await resp.json()
                    for each in resp:
                        if "type" in each:
                            if each["type"] == "pub" and "uid" in each:
                                each["time"] = day_str
                                hot_list.append(each)
                    logger.info(str(input_url) + ' generated successfully')
                except Exception as e:
                    logger.warning(str(input_url) + ' generated failed')
    return hot_list

def run_cold_start(date_start_str: str, date_end_str: str):
    """Get log over time

    Args:
    Returns:
        list:The data over 90 days dictionary list

    """
    days_list = get_days_list(date_start_str, date_end_str)
    tasks = [asyncio.ensure_future(get_hot_list(day_str)) for day_str in days_list]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    result_list = []
    for task in tasks:
        for res in task.result():
            result_list.append(res)
    browse_data_location = INPUT_LOG_DATA
    with open(browse_data_location, "w") as fp:
        fp.write(json.dumps(result_list, indent=4))
        logger.info('cold start data generated successfully')

def del_oldest_data(path, day_list):
    """Delete data from 30 days ago

         Args:
             path:data path
             day_list:Data between day_list

         Returns:

         """
    with open(path, 'r', encoding='utf-8') as load_f:
        load_dict = json.load(load_f)
        result_list = []
        for each in load_dict:
            if each['time'] in day_list[0:-1]:
                result_list.append(each)
        with open(path, 'w') as f:
            f.write(json.dumps(result_list, indent=4))
            logger.info('delete successfully')

def load_input_log_everyday(date_start_str: str, date_end_str: str):
    """Get log over time

    Args:
        date_start_str:start time
        date_end_str:end time

    Returns:
        list:The data over 30 days dictionary list

    """
    days_list = get_days_list(date_start_str, date_end_str)
    tasks = [asyncio.ensure_future(get_hot_list(day_str)) for day_str in days_list]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    result_list = []
    hot_spot_data_location = INPUT_LOG_DATA
    with open(hot_spot_data_location, 'r', encoding='utf-8') as load_f:
        load_dict = json.load(load_f)
        for each in load_dict:
            result_list.append(each)
    for task in tasks:
        for res in task.result():
            result_list.append(res)
    with open(hot_spot_data_location, "w") as fp:
        fp.write(json.dumps(result_list, indent=4))

def run_everyday():
    browse_data_location = INPUT_LOG_DATA
    if not os.path.exists(browse_data_location):
        logger.warning('Please start cold first to generate browse data')
        sys.exit(0)
    start = datetime.datetime.now() - datetime.timedelta(days=config.DAYS_OF_INPUT_LOG)
    start_time = f"{start.year}-{start.month}-{start.day}"
    end = datetime.datetime.now() - datetime.timedelta(days=1)
    end_time = f"{end.year}-{end.month}-{end.day}"
    days_list = get_days_list(start_time, end_time)
    del_oldest_data(browse_data_location, days_list)
    load_input_log_everyday(days_list[-1],days_list[-1])

# if __name__ == '__main__':
#     # run_cold_start("2022-04-01","2022-04-06")
#     run_everyday()
