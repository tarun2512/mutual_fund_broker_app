import time

import bcrypt

from scripts.config import Security
from scripts.constants.common_constants import Secrets
from scripts.db.mongo import mongo_client
from scripts.db.mongo.user_meta_store.user_collection import User
from scripts.errors import TooManyRequestsError, InvalidPasswordError
from scripts.errors.exception_codes import DefaultExceptionsCode
from scripts.logging import logger
from scripts.utils.common_utils import CommonUtils


class UserHandlerHelper:
    def __init__(self):
        self.permanent_token = Secrets.token
        self.user_con = User(mongo_client=mongo_client)
        self.max_age_in_mins = Security.COOKIE_MAX_AGE_IN_MINS
        self.common_utils = CommonUtils()

    async def reset_login_attempts(self, user_record, reset=True):
        user_id = user_record.get("user_id")
        try:
            user_locked = False
            failed_attempts = 0
            failed_login = None
            if not reset:
                failed_attempts = user_record.get("failed_attempts") or 0
                failed_attempts = int(failed_attempts) + 1
                last_failed_login = user_record.get("last_failed_login")
                _t_ = int(time.time())
                failed_login = _t_
                if failed_attempts >= Security.MAX_LOGIN_ATTEMPTS:
                    user_locked = True
                if last_failed_login and (_t_ - last_failed_login) < 10:
                    raise TooManyRequestsError(DefaultExceptionsCode.DE004)

            await self.user_con.update_one(
                query={"user_id": user_id},
                data={
                    "failed_attempts": failed_attempts,
                    "is_user_locked": user_locked,
                    "last_logged_in": int(time.time()),
                    "last_failed_login": failed_login,
                },
            )
        except TooManyRequestsError:
            raise
        except Exception as e:
            logger.exception(str(e))

    async def validate_password(self, password, user_record):
        if not user_record.get("password") or user_record.get("password") == "null":
            await self.reset_login_attempts(user_record=user_record, reset=False)
            raise InvalidPasswordError(msg=DefaultExceptionsCode.DEIL)
        if not bcrypt.checkpw(
            password.encode("utf-8"), user_record["password"].encode("utf-8")
        ):
            await self.reset_login_attempts(user_record=user_record, reset=False)
            raise InvalidPasswordError(msg=DefaultExceptionsCode.DEIP)
        return True

    async def set_login_token(self, response, user_record, client_ip, lockout_time):
        login_token = self.common_utils.create_token(
            user_id=user_record.get("user_id"),
            ip=client_ip,
            age=lockout_time,
        )
        logger.info(f"space_id while creating login token {login_token}")
        response.set_cookie(
            "login-token",
            login_token,
            samesite="strict",
            httponly=True,
            max_age=lockout_time * 60,
            secure=Security.SECURE_COOKIE,
        )
        response.headers["login-token"] = login_token

    @staticmethod
    async def set_user_id(response, user_id):
        response.set_cookie(
            "user_id",
            user_id,
            httponly=True,
            secure=Security.SECURE_COOKIE,
        )
        response.set_cookie(
            "userId",
            user_id,
            httponly=True,
            secure=Security.SECURE_COOKIE,
        )
        return response
