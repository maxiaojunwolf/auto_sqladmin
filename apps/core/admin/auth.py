# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from starlette.requests import Request
from starlette.responses import RedirectResponse

from apps.core.db import session_execute
from apps.core.dependencies import encrypt_token, Current_User
from apps.core.models.entity import Entity
from apps.core.models.role import User2Role
from apps.core.models.user import User
from apps.core.models.view_config import ViewConfig, Role2ViewConfig
from apps.core.tools import encrypt_password
from settings import ServerSettings


class AdminAuth(AuthenticationBackend):
    """登录认证"""

    async def visible_menus(self, user: User) -> list[str]:
        """查询用户的可见菜单"""
        menus = []
        stmt = select(Entity.name).join(ViewConfig).join(Role2ViewConfig).join(User2Role, onclause=(
                User2Role.role_id == Role2ViewConfig.role_id)).where(User2Role.user_id == user.id)
        result = await session_execute(stmt)
        for r in result.unique().fetchall():
            menus.append(r.name)
        return menus

    async def login(self, request: Request) -> bool:
        """登录"""
        form = await request.form()
        username, password = form["username"], form["password"]
        # Validate
        stmt = select(User).where(User.login == username, User.is_active == True)
        result = await session_execute(stmt)
        user = result.scalar()
        # 验证密码,激活
        if not (user and user.password == encrypt_password(str(user.login), password)):
            return False
        # 查询可见菜单
        visible_menus = await self.visible_menus(user)
        # 生成用户token信息
        token_data = {"id": user.id,
                      "name": user.name,
                      "is_superuser": user.is_superuser,
                      "visible_menus": visible_menus
                      }
        token = encrypt_token(token_data, expires=datetime.now(ServerSettings.TIMEZONE) + timedelta(
            seconds=ServerSettings.COOKIE_EXPIRES))
        request.session.update({"token": token})
        return True

    async def logout(self, request: Request) -> bool:
        """退出登录"""
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        """认证"""
        token = request.session.get("token")
        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=301)
        try:
            payload = jwt.decode(token,
                                 ServerSettings.TOKEN_SECRET_KEY,
                                 algorithms=ServerSettings.TOKEN_ALGORITHM,
                                 issuer=ServerSettings.ISSUER,
                                 audience=ServerSettings.AUDIENCE)
            current_user = Current_User(id=payload['id'],
                                        name=payload['name'],
                                        is_superuser=payload["is_superuser"],
                                        visible_menus=payload["visible_menus"],
                                        )

            request._current_user = current_user
            return True
        except (jwt.JWTError, jwt.ExpiredSignatureError, KeyError):
            request.session.update({"token": ''})
            return RedirectResponse(request.url_for("admin:login"), status_code=301)
