# -*- coding:utf-8 -*-
from .admin.load import dynamic_view
from .db import engine


async def on_startup():
    """服务启动时"""
    await dynamic_view()


async def on_shutdown():
    """服务关闭时"""

    await engine.dispose()
