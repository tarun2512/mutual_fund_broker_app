import uuid
from datetime import datetime, timedelta

from scripts.constants.common_constants import Secrets
from scripts.db.redis_connection import login_db
from scripts.utils.common_utils import jwt


def create_token(user_id, ip, token, age=Secrets.LOCK_OUT_TIME_MINS, login_token=None):
    """
    This method is to create a cookie
    """
    try:
        uid = login_token
        if not uid:
            uid = str(uuid.uuid4()).replace("-", "")

        payload = {"ip": ip, "user_id": user_id, "token": token, "uid": uid, "age": age}
        exp = datetime.utcnow() + timedelta(minutes=age)
        _extras = {"iss": Secrets.issuer, "exp": exp}
        _payload = {**payload, **_extras}

        new_token = jwt.encode(_payload)

        # Add session to redis
        login_db.set(uid, new_token)
        login_db.expire(uid, timedelta(minutes=age))

        return uid
    except Exception:
        raise
