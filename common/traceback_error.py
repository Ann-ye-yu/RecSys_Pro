# -*- encoding: utf-8 -*-
'''
@Description:
@Date:2022/03/12 13:42:21
@Author:赵祎
@version:1.0
'''
import logging
from common.email_util import EmailUtil
from .config import RECEIVERS
import traceback
import socket

logger = logging.getLogger("recallApp.trackback")


def traceback_with_email(func):
    def wrapper(*args, **kargs):
        try:
            logger.info("start traceback email service")
            func(*args, **kargs)
        except Exception as e:
            for email in RECEIVERS:
                EmailUtil(traceback.format_exc(), "aminer",
                          email, "报错信息").send_email()
            logger.error(e)
    return wrapper


def traceback_with_var_email(receivers: list, title="["+socket.gethostname()+"]: rms_recall报错信息", send_person="aminer"):
    """Use a decorator to raise an alarm when a function is abnormal
    content
    Args:
    receivers:
        persons who receives the email   
    title:
        The subject of the email
    send_person:
        The sender's nickname 

    Returns:
        return wrapper funciton
    example:
        @traceback_with_var_email(receivers=["1051532098@qq.com"],title="",send_person="")
        def cal(a,b):
            # time.sleep(50)
            return a/b
    Raise:
        None
    """
    def traceback_with_email_(func):
        def wrapper(*args, **kargs):
            try:
                logger.info("start traceback email service")
                func(*args, **kargs)
            except Exception as e:
                for email in receivers:
                    EmailUtil(traceback.format_exc(), send_person,
                              email, title).send_email()
                logger.error(e)
        return wrapper
    return traceback_with_email_
