# env [local,dev]
import os
if os.environ.get('RECALL_ENV'):
    ENV  = os.environ.get('RECALL_ENV')
else:
    ENV = "pro"
if ENV == "local":
    from common.config_local import *
elif ENV == "pro":
    from common.config_pro import *
else:
    print("error env variable")
print(f"env load ok . ENV = {ENV}")


INPUT_LOG_URL = "http://120.131.0.100:10808/aminer/input_log/"

# The time range of the data
DAYS_OF_INPUT_LOG = 90