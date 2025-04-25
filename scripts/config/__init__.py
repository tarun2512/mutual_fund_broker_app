import os
import pathlib
import shutil
import sys
from typing import Optional, Any

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings, Field, root_validator

load_dotenv()

PROJECT_NAME = "pinacle_assignment"


class _Service(BaseSettings):
    MODULE_NAME: str = Field(default="assignment")
    APP_NAME: str = Field(default="assignment")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=5112)
    LOG_LEVEL: str = Field(default="INFO")
    ENABLE_FILE_LOG: Optional[Any] = False
    ENABLE_CONSOLE_LOG: Optional[Any] = True

    @root_validator(allow_reuse=True)
    def validate_values(cls, values):
        values["LOG_LEVEL"] = values["LOG_LEVEL"] or "INFO"
        print(f"Logging Level set to: {values['LOG_LEVEL']}")
        return values


class _PathToStorage(BaseSettings):
    BASE_PATH: pathlib.Path = Field(None, env="BASE_PATH")
    MOUNT_DIR: pathlib.Path = Field(None, env="MOUNT_DIR")
    MODULE_PATH: Optional[pathlib.Path]

    @root_validator(allow_reuse=True)
    def assign_values(cls, values):
        values["LOGS_MODULE_PATH"] = os.path.join(values.get("BASE_PATH"), "logs", values.get("MOUNT_DIR"))
        values["MODULE_PATH"] = os.path.join(values.get("BASE_PATH"), values.get("MOUNT_DIR"))
        return values

    @root_validator(allow_reuse=True)
    def validate_values(cls, values):
        if not values["BASE_PATH"]:
            print("Error, environment variable BASE_PATH not set")
            sys.exit(1)
        if not values["MOUNT_DIR"]:
            print("Error, environment variable MOUNT_DIR not set")
            sys.exit(1)
        return values


class _KeyPath(BaseSettings):
    KEYS_PATH: Optional[pathlib.Path] = Field(default="data/keys")
    PUBLIC: Optional[pathlib.Path]
    PRIVATE: Optional[pathlib.Path]

    @root_validator(allow_reuse=True)
    def assign_values(cls, values):
        if not os.path.isfile(os.path.join(values.get("KEYS_PATH"), "public")) or not os.path.isfile(
            os.path.join(values.get("KEYS_PATH"), "private")
        ):
            if not os.path.exists(values.get("KEYS_PATH")):
                os.makedirs(values.get("KEYS_PATH"))
            shutil.copy(os.path.join("assets", "keys", "public"), os.path.join(values.get("KEYS_PATH"), "public"))
            shutil.copy(os.path.join("assets", "keys", "private"), os.path.join(values.get("KEYS_PATH"), "private"))
        values["PUBLIC"] = os.path.join(values.get("KEYS_PATH"), "public")
        values["PRIVATE"] = os.path.join(values.get("KEYS_PATH"), "private")
        return values


class _Databases(BaseSettings):
    MONGO_URI: Optional[str]
    REDIS_URI: Optional[str]
    REDIS_LOGIN_DB: Optional[int] = 14

    @root_validator(allow_reuse=True)
    def validate_values(cls, values):
        if not values["MONGO_URI"]:
            print("Error, environment variable MONGO_URI not set")
            sys.exit(1)
        if not values["REDIS_URI"]:
            print("Error, environment variable REDIS_URI not set")
            sys.exit(1)
        return values

class _Security(BaseSettings):
    SECURE_COOKIE: bool = Field(default=True) in ["True", "true", True]
    COOKIE_MAX_AGE_IN_MINS: int = Field(default=60)
    MAX_LOGIN_ATTEMPTS: int = Field(default=10)
    REFRESH_TOKEN_DURATION: int = Field(default=168)
    LOCK_OUT_TIME_MINS: int = Field(default=2880)
    RAPID_API_KEY: str = Field(default="3f0431550cmsh20b4f0436520890p1b4958jsn8a32be0b0618")
    HTTP_FLAG: bool = Field(default=True) in ["True", "true", True]


Service = _Service()
PathToStorage = _PathToStorage()
KeyPath = _KeyPath()
DBConf = _Databases()
Security = _Security()

__all__ = [
    "PROJECT_NAME",
    "Service",
    "PathToStorage",
    "KeyPath",
    "DBConf",
    "Security"
]
