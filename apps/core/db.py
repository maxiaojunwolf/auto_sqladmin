# -*- coding:utf-8 -*-
from typing import Union, Any

from sqlalchemy import Select, TextClause, Result, CursorResult, Update, Delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from settings import DBSettings
from .tools import singleton


@singleton
class Engine:
    """异步连接engin,单例模式"""

    def __new__(cls, *args, **kwargs):
        return create_async_engine(
            DBSettings.URL,
            echo=DBSettings.ECHO,
            **kwargs
        )


@singleton
class Session:
    """异步session，单例模式"""

    def __new__(cls, engine):
        return sessionmaker(
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            bind=engine
        )


class DynamicBase(DeclarativeBase):
    """动态ORM基类"""
    _orms = dict()


class Base(DeclarativeBase):
    """ORM基类"""
    pass


engine = Engine()
session_factory = Session(engine)


async def session_execute(stmt: Select, **kwargs) -> Result[Any]:
    """使用session查询数据"""
    async with session_factory() as session:
        return await session.execute(stmt, **kwargs)


async def connect_execute(stmt: Union[Select, TextClause, Update, Delete], **kwargs) -> CursorResult[Any]:
    """使用connect执行单条语句并提交"""
    async with engine.begin() as conn:
        return await conn.execute(stmt, **kwargs)
