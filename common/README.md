# common utils
## content
### log
The logging module is used to ensure the consistency of log behavior, provide log formatting and log file writing functions
### email report error
Mail alarm module is used to handle when the program occurs abnormal notification developers
## usage

### email report error
Mail alarm decorator with no arguments
~~~
from common.traceback_error import traceback_with_email
@traceback_with_email
def cal(a,b):
    return a/b
~~~
Mail alarm decorator with no arguments
~~~
from common.traceback_error import traceback_with_var_email
@traceback_with_var_email(receivers=["1051532098@qq.com"],title="",send_person="")
def cal(a,b):
    # time.sleep(50)
    return a/b
~~~
### log
Sub-module log service
~~~
import logging

logger = logging.getLogger("recallApp.xxxxx")
logger.info("xxx")
~~~
