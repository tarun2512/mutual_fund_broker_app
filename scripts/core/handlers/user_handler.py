import json
import time
from fastapi.responses import JSONResponse

import bcrypt
import shortuuid
from fastapi import Request, Response

from scripts.config import Security
from scripts.core.engine.password_strength_check import validate_password_strength
from scripts.core.engine.user_handler_helper import UserHandlerHelper
from scripts.db.mongo import mongo_client
from scripts.db.mongo.user_meta_store.user_collection import User
from scripts.db.redis_connection import login_db
from scripts.errors import CustomError, TooManyRequestsError, InvalidPasswordError, UserNotFound
from scripts.errors.exception_codes import DefaultExceptionsCode, UserExceptions
from scripts.logging import logger
from scripts.schemas.user_schema import UserRegister
from scripts.utils.common_utils import CommonUtils


class UserHandler:
    def __init__(self):
        self.user_con = User(mongo_client=mongo_client)
        self.user_handler_helper = UserHandlerHelper()
        self.common_utils = CommonUtils()
        self.login_redis = login_db


    def register_user(self, request_data: UserRegister):
        try:
            request_data.email = request_data.email.lower()
            existing_user_name = self.user_con.find_user(username=request_data.username)

            if request_data.user_id:
                return self.edit_user(
                    request_data,
                    existing_user_name,
                )
            else:
                return self.add_user(existing_user_name, request_data)
        except Exception as e:
            logger.exception(str(e))
            raise

    def edit_user(self, input_data: UserRegister, existing_user_name):
        input_data.updated_on = int(time.time())
        user_id = input_data.user_id
        if existing_user_name and (
            existing_user_name.user_id != input_data.user_id
            or existing_user_name.email != input_data.email
        ):
            raise CustomError("Given User name or email id already exists")
        if "password" not in input_data or not input_data.password:
            existing_user = self.user_con.find_user(user_id=user_id)
            existing_user = existing_user.dict() if bool(existing_user) else existing_user
            input_data.password = existing_user["password"]
        self.user_con.update_one_user({"user_id": input_data.user_id}, data=input_data.model_dump())
        return input_data.user_id

    def add_user(self, existing_user_name, input_data):
        if existing_user_name.username:
            raise CustomError("The username entered already exists")
        if not input_data.password:
            raise CustomError("Please provide a password")
        if existing_user_name and existing_user_name.email == input_data.email:
            raise CustomError("The email entered already exists")
        if input_data.password:
            if not validate_password_strength(input_data.password):
                message = (
                    "Password should contain minimum of 8 characters with at least a symbol, "
                    "one upper and one lower case letters and a number"
                )
                raise CustomError(message)
            hash_pass = bcrypt.hashpw(input_data.password.encode("utf-8"), bcrypt.gensalt())
            if isinstance(hash_pass, bytes):
                hash_pass = hash_pass.decode()
            input_data.password = hash_pass
        input_data.user_id = shortuuid.uuid()
        input_data.created_on = int(time.time())
        user_data = input_data.model_dump()
        self.user_con.insert_one_user(input_data.model_dump())
        return user_data.get("user_id")

    def login_flow(
        self, login_request, request: Request, response: Response, bg_task=None
    ):
        try:
            # Get user details
            user_record = self.get_user_record(username=login_request.username)
            # Check for failed login attempts
            if user_record.get("is_user_locked", False):
                raise CustomError(UserExceptions.USER_INACTIVE)
            auth = self.user_handler_helper.validate_password(
                password=login_request.password,
                user_record=user_record,
            )
            if not auth:
                self.user_handler_helper.reset_login_attempts(user_record, reset=False)
                raise InvalidPasswordError(msg=DefaultExceptionsCode.DEIP)
            client_ip = request.client.host
            # Login Response
            self.common_method_login_token(
                response=response,
                user_record=user_record,
                client_ip=client_ip,
            )
            self.user_con.update_one_user(
                data={"last_logged_in": int(time.time()), "last_failed_login": None},
                query={"user_id": user_record.get("user_id")},
            )
            bg_task.add_task(
                self.user_handler_helper.reset_login_attempts,
                user_record,
            )
            return user_record
        except TooManyRequestsError:
            logger.exception(DefaultExceptionsCode.DE004)
            raise
        except InvalidPasswordError:
            logger.exception(DefaultExceptionsCode.DEIP)
            return False
        except UserNotFound:
            logger.exception(DefaultExceptionsCode.DE001)
            return False
        except CustomError as e:
            logger.exception(str(e))
            return {"status": "failed", "message": str(e)}

    def get_user_record(self, username):
        try:
            user_record = self.user_con.find_user(username=username, filter_dict={"_id": 0})

            if not bool(user_record):
                raise UserNotFound(msg="Failed to login! User unauthorised!")
            else:
                user_record = user_record.dict()
            return user_record
        except Exception as e:
            logger.exception(f"{e}")
            raise

    def common_method_login_token(
        self, response, user_record, client_ip
    ):
        refresh_age = Security.REFRESH_TOKEN_DURATION
        refresh_token = self.common_utils.create_token(
            user_id=user_record.get("user_id"), ip=client_ip, age=refresh_age * 60
        )
        response.set_cookie(
            "refresh-token",
            refresh_token,
            samesite="strict",
            httponly=True,
            max_age=refresh_age * 60 * 60,
            secure=Security.SECURE_COOKIE,
        )
        lockout_time = Security.LOCK_OUT_TIME_MINS
        login_token = self.user_handler_helper.set_login_token(
            response, user_record, client_ip, lockout_time
        )
        login_exp_time = str(int(time.time() + lockout_time * 60) * 1000)
        response.set_cookie(
            "login_exp_time",
            login_exp_time,
            samesite="strict",
            httponly=True,
            max_age=Security.LOCK_OUT_TIME_MINS * 60,
            secure=Security.SECURE_COOKIE,
        )
        self.user_handler_helper.set_user_id(response=response, user_id=user_record.get("user_id"))

    def reset_password(self, request_data):
        try:
            logger.debug("Resetting password ")
            user_record = self.user_con.find_user(username=request_data["userName"])
            if not user_record:
                response = {"status": "success", "message": "User not found"}
                return JSONResponse(status_code=401, content=response)
            for each_record in user_record:
                if each_record["username"] != request_data["userName"]:
                    continue
                # Decrypt encrypted password
                if validate_password_strength(request_data["new_password"]):
                    hash_pass = bcrypt.hashpw(
                        request_data["new_password"].encode("utf-8"),
                        bcrypt.gensalt(),
                    )
                    new_values = {"password": hash_pass.decode(), "password_added_on": int(time.time())}
                    self.user_con.update_one_user(
                        query={"username":request_data["userName"]},
                        data=new_values,
                    )

                    resp_json = {
                        "status": "success",
                        "message": "Password reset successfully",
                    }
                    self.user_handler_helper.reset_login_attempts(each_record)
                    logger.info("Login attempts reset successful")
                else:
                    error_msg = (
                        "Password should contain minimum of 8 characters and a maximum of 64 characters,"
                        "with at least a symbol, one upper and one lower case letters and a number"
                    )
                    logger.error(f"Error occurred while occurred while resetting password : {error_msg}")
                    resp_json = {
                        "status": "failed",
                        "message": error_msg,
                    }

                resp = JSONResponse(status_code=200, content=resp_json)
                resp.set_cookie(
                    "user_id",
                    expires=0,
                    httponly=Security.HTTP_FLAG,
                    secure=Security.SECURE_COOKIE,
                )

                try:
                    del resp.headers["user_id"]
                    del resp.headers["user_role"]
                except Exception as e:
                    logger.info(f"Unable to delete {str(e)}")
                return resp
        except Exception as e:
            logger.exception(f"Error occurred while resetting password : {str(e)}")
            return {"status": "failed", "message": str(e)}

    def logout(self, session_id, login_token, refresh_token):
        final_json = {"status": "failed", "message": "Logout failed"}
        try:
            logger.debug(session_id)
            final_json["status"] = "success"
            final_json["message"] = "Logout Successfully"
            resp = Response(content=json.dumps(final_json), media_type="application/json")
            resp.set_cookie("user_id", "", expires=0, secure=Security.SECURE_COOKIE, httponly=Security.HTTP_FLAG)
            resp.set_cookie("login-token", "", expires=0, secure=Security.SECURE_COOKIE, httponly=Security.HTTP_FLAG)
            resp.set_cookie("userId", "", expires=0, secure=Security.SECURE_COOKIE, httponly=Security.HTTP_FLAG)
            resp.set_cookie("refresh-token", "", expires=0, secure=Security.SECURE_COOKIE, httponly=Security.HTTP_FLAG)
            self.login_redis.delete(login_token)
            self.login_redis.delete(refresh_token)
            return resp
        except Exception as e:
            logger.exception(f"Exception while logging out ->{str(e)}")
            return final_json