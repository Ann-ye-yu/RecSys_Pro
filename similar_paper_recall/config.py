from common.config import *

if ENV == "local":
    from config_local import *
elif ENV == "pro":
    from config_pro import *
else:
    print("error env variable")
