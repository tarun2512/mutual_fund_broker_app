from scripts.config import DBConf
from scripts.utils.mongo_util import MongoConnect

mongo_client = MongoConnect(uri=DBConf.MONGO_URI)()