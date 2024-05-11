# -*- coding: utf-8 -*-
import hmac
import os.path
from configparser import ConfigParser
from datetime import datetime

from settings import ServerSettings


def singleton(cls):
    """单例装饰器"""
    _instance = {}

    def inner(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return inner


def encrypt_password(secret: str, password: str) -> str:
    """密码加密"""
    return hmac.new(secret.encode('utf-8'), password.encode('utf-8'), 'sha1').hexdigest()


def local_datetime(timezone=ServerSettings.TIMEZONE):
    """本地时间"""
    return datetime.now(tz=timezone)


def get_versions_path() -> str:
    """获取版本文件路径"""
    conf = ConfigParser()
    conf.read(os.path.normpath(os.path.join(ServerSettings.ROOT_PATH, "alembic.ini")))
    script_location = conf['alembic']['script_location']
    return os.path.join(ServerSettings.ROOT_PATH, script_location, "versions")


def format_datetime(value):
    """日期格式化"""
    if value:
        return datetime.strftime(value, ServerSettings.DATETIME_FORMAT)


def get_column_label(property):
    """获取属性描述文字:relationship的doc内容需要通过_doc访问"""
    return getattr(property, "doc", None) or getattr(property, "_doc", None)


if __name__ == '__main__':
    print(encrypt_password("admin", "admin"))
