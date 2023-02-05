from datetime import datetime
from common.config import POSTGRESQL_SETTING

import psycopg2
import logging

from config import *

logger = logging.getLogger('recallApp.user_profile_construct.db')


class PostgresConnection:
    conn = None
    setting = None

    def __init__(self, setting: dict = POSTGRESQL_SETTING):
        try:
            self.setting = setting
            self.conn = psycopg2.connect(**self.setting)
        except ConnectionError as e:
            logger.error(e)

    # def get_user_action_log_for_test(self, day:int=1, limit: int = 200):
    #     """return a list of user action log.
    #             :param: action_list: list
    #             format [(uid,tc_day, type, query, item), ...]
    #             uid: str, user's identification
    #             tc_day: datetime.datetime, just contains date.
    #             type: str, {'person', 'research_report', 'pub', 'search_pub', 'search_person', 'topic'}
    #             query: str, a text
    #             item: identification.
    #             """
    #     print(f'get user action log in {day} days')
    #     sql = f"SELECT uid, tc_day, type, query, item FROM recsys_usereventlog WHERE(now() - interval '{day} day')::DATE <= tc and tc < now()::DATE and uid is not null"
    #     cursor = self.conn.cursor()
    #     cursor.execute(sql)  # about cost 1 minute.
    #     action_list = list()
    #     while True:
    #         temp = cursor.fetchmany(limit)
    #         if temp:
    #             action_list.extend(temp)
    #         else:
    #             break
    #     return action_list

    def get_user_action_log(self, day_numb: int = 30, limit: int = 200):
        """return a list of user action log.
        :param: action_list: list
        format [(uid, tc, tc_day, type, query, item), ...]
        uid: str, user's identification
        tc: datetime.datetime, clicked time.
        tc_day: datetime.datetime, just contains date.
        type: str, {'person', 'research_report', 'pub', 'search_pub', 'search_person', 'topic'}
        query: str, a text
        item: identification.
        """
        logger.info(f'get user action log in {day_numb} days')
        sql = f"SELECT uid, tc, type, query, item, tc FROM recsys_usereventlog WHERE(now() - interval '{day_numb} day')::DATE <= tc and uid is not null ORDER BY tc ASC"
        cursor = self.conn.cursor()
        cursor.execute(sql)  # about cost 1 minute.
        action_list = list()
        while True:
            temp = cursor.fetchmany(limit)
            if temp:
                action_list.extend(temp)
            else:
                break
        return action_list

    def get_user_action_log_after_target_time(self, target_time:datetime, limit:int = 200):
        logger.info(f'get user action log after {str(target_time)}')
        sql = f"SELECT uid, tc, type, query, item, tc FROM recsys_usereventlog WHERE tc > '{str(target_time)}' and uid is not null ORDER BY tc ASC"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        action_list = list()
        while True:
            temp = cursor.fetchmany(limit)
            if temp:
                action_list.extend(temp)
            else:
                break
        return action_list


if __name__ == '__main__':
    client = PostgresConnection()
    client.get_user_action_log_by_month()
