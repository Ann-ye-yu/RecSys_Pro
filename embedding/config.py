from common.config import *
if ENV == "local":
    from embedding.config_local import *
elif ENV == "pro":
    from embedding.config_pro import *
else:
    print("error env variable")
