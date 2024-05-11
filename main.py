# # -*- coding:utf-8 -*-
import argparse

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from apps.core import middleware
from apps.core.admin import EntityAdmin, TableAdmin, FieldAdmin, Unique_ConstraintAdmin, \
    Index_ConstraintAdmin, ForeignKey_ConstraintAdmin, RelShipAdmin, ViewConfigAdmin, UserAdmin, RoleAdmin
from apps.core.admin.auth import AdminAuth
from apps.core.admin.base import MyAdmin as Admin
from apps.core.db import engine, session_factory
from settings import ServerSettings, OpenApiSettings



def create_app():
    """创建app实例"""
    app = FastAPI(title=OpenApiSettings.TITLE,
                  description=OpenApiSettings.DESCRIPTION,
                  version=OpenApiSettings.VERSION,
                  on_startup=[middleware.on_startup],
                  on_shutdown=[middleware.on_shutdown],
                  )
    # 中间件：配置跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        # 跨域时，支持cookie
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # 中间件：数据压缩
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    # 使用session
    app.add_middleware(SessionMiddleware, secret_key=ServerSettings.TOKEN_SECRET_KEY)
    # 注册admin
    regist_admin(app)
    return app


def regist_admin(app):
    """注册admin"""
    global admin
    authentication_backend = AdminAuth(secret_key=ServerSettings.TOKEN_SECRET_KEY)
    admin = Admin(app, engine, authentication_backend=authentication_backend, session_maker=session_factory)
    admin.add_view(TableAdmin)
    admin.add_view(EntityAdmin)
    admin.add_view(FieldAdmin)
    admin.add_view(Unique_ConstraintAdmin)
    admin.add_view(Index_ConstraintAdmin)
    admin.add_view(ForeignKey_ConstraintAdmin)
    admin.add_view(RelShipAdmin)
    admin.add_view(ViewConfigAdmin)
    admin.add_view(RoleAdmin)
    admin.add_view(UserAdmin)
    app._admin = admin



admin = None
app = create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='服务启动参数')
    parser.add_argument('--host', type=str, dest='host')
    parser.add_argument('--port', type=int, dest='port')
    parmeters = parser.parse_args()
    uvicorn.run("main:app",
                host=parmeters.host or ServerSettings.HOST,
                port=parmeters.port or ServerSettings.PORT,
                workers=ServerSettings.WORKERS)
