import uuid
from datetime import datetime, timedelta
from scripts.db.mongo import mongo_client
from scripts.constants.common_constants import Secrets, CommonKeys
from scripts.db.mongo.user_meta_store.unique_id import UniqueId, UniqueIdSchema

from scripts.db.redis_connection import login_db
from scripts.utils.security_utils.jwt_util import JWT
jwt = JWT()


class CommonUtils(CommonKeys):
    def __init__(self):
        self.unique_con = UniqueId(mongo_client)

    def get_next_id(self, _param):
        my_dict = UniqueIdSchema(key=_param)
        my_doc = self.unique_con.find_one_record(key=_param)
        if not my_doc.id:
            my_dict.id = "100"
            return self.unique_con.insert_record(my_dict)
        else:
            count_value = str(int(my_doc.id) + 1)
            my_dict.id = count_value
            return self.unique_con.update_record(my_dict)

    def create_token(self, user_id, ip, age=Secrets.LOCK_OUT_TIME_MINS, login_token=None):
        """
        This method is to create a cookie
        """
        uid = login_token
        if not uid:
            uid = str(uuid.uuid4()).replace("-", "")

        payload = {"ip": ip, "user_id": user_id, "uid": uid, "age": age}
        exp = datetime.utcnow() + timedelta(minutes=age)
        _extras = {"iss": Secrets.issuer, "exp": exp}
        _payload = {**payload, **_extras}

        new_token = jwt.encode(_payload)

        # Add session to redis
        login_db.set(uid, new_token)
        login_db.expire(uid, timedelta(minutes=age))

        return uid
