# -*- coding:utf-8 -*-
import os
from urllib.parse import quote_plus

import pytz
from dotenv import load_dotenv

# 加载配置
load_dotenv(verbose=True)


class BaseSettings:
    """基础配置"""
    # 项目根路径
    ROOT_PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
    # 时区
    TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', default='Asia/Shanghai'))
    # datetime日期格式
    DATETIME_FORMAT = os.getenv('DATETIME_FORMAT', default="%Y-%m-%d %H:%M:%S")
    # date日期格式
    DATE_FORMAT = os.getenv('DATE_FORMAT', default="%Y-%m-%d")

    @classmethod
    def makesure_path(cls, path):
        """路径不存在则新建"""
        if path.startswith('.'):
            path = os.path.abspath(path)
        path = os.path.normpath(path)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return path


class OpenApiSettings(BaseSettings):
    """文档接口设置"""
    TITLE = "Auto Sqladmin"
    DESCRIPTION = "Auto Sqladmin"
    VERSION = "1.0.0"


class ServerSettings(BaseSettings):
    """服务设置"""
    # 主服务IP地址
    HOST = os.getenv('HOST', default="127.0.0.1")
    # 主服务端口号
    PORT = int(os.getenv('PORT', default=8000))
    # 是否自动重载
    RELOAD = True
    # 进程数
    WORKERS = int(os.getenv('WORKERS', default=1))
    # api接口前缀
    URL_PREFIX = os.getenv('URL_PREFIX', default="/v1")
    # cookie有效期/秒
    COOKIE_EXPIRES = int(os.getenv('COOKIE_EXPIRES', default=60 * 60 * 24 * 30))
    # token
    TOKEN_SECRET_KEY = os.getenv('TOKEN_SECRET_KEY')
    TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM')
    ISSUER = os.getenv('ISSUER')
    AUDIENCE = os.getenv('AUDIENCE')
    # 数据存储路径
    DATA_ROOT = BaseSettings.makesure_path(os.getenv('DATA_ROOT'))


class DBSettings(BaseSettings):
    """数据库设置"""
    URL = os.getenv('SQLITE_URL')
    # 是否打印执行日志
    ECHO = bool(int(os.getenv('ECHO')))
    if not URL:
        # 名称
        DB = os.getenv('MYSQL_DB')
        # 字符编码
        CHARSET = os.getenv('MYSQL_CHARSET')
        # 排序
        COLLECTION = os.getenv('MYSQL_COLLECTION')
        # 数据库服务地址
        SERVER = "mysql+aiomysql://{}:{}@{}:{}".format(os.getenv('MYSQL_USER'),
                                                       quote_plus(os.getenv('MYSQL_PWD')),
                                                       os.getenv('MYSQL_HOST', default="0.0.0.0"),
                                                       os.getenv('MYSQL_PORT', default=3306)
                                                       )
        # 数据库链接
        URL = "{}/{}".format(SERVER, DB)


class NameSettings(BaseSettings):
    """系统名称配置"""
    CORE_TABLE_PREFIX = "core"
