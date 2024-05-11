# -*- coding:utf-8 -*-
from collections import namedtuple

from fastapi import Depends, Cookie, HTTPException
from jose import jwt
from starlette.requests import Request

from settings import ServerSettings

"""登录认证"""

# 当前用户
Current_User = namedtuple("Current_User",
                          ['id', 'name', 'is_superuser', "visible_menus"])


def encrypt_token(data: dict,
                  expires,
                  secret_key: str = ServerSettings.TOKEN_SECRET_KEY) -> str:
    """
    token加密
    :param data: 需要进行JWT令牌加密的数据
    :param expires_delta: 令牌有效期
    :return: token
    """
    data.update({"exp": expires, 'iss': ServerSettings.ISSUER, 'aud': ServerSettings.AUDIENCE})
    return jwt.encode(data, secret_key, algorithm=ServerSettings.TOKEN_ALGORITHM)


def decrypt_token(request: Request, token: str = Cookie(None)) -> dict:
    """token解析"""
    if token is None:
        token = request.headers.get('token', request.query_params.get('token'))
    if not token:
        raise HTTPException(status_code=403,detail="token missing")
    try:
        return jwt.decode(token,
                          ServerSettings.TOKEN_SECRET_KEY,
                          algorithms=ServerSettings.TOKEN_ALGORITHM,
                          issuer=ServerSettings.ISSUER,
                          audience=ServerSettings.AUDIENCE)
    except (jwt.JWTError, jwt.ExpiredSignatureError):
        raise HTTPException(status_code=403,detail="authentication failed")


async def authenticated(request: Request, payload: dict = Depends(decrypt_token)) -> None:
    """身份认证"""

    current_user = Current_User(id=payload['id'],
                                name=payload['name'],
                                is_superuser=payload["is_superuser"],
                                visible_menus=payload["visible_menus"]
                                )
    request._current_user = current_user


async def get_current_user(request: Request) -> Current_User:
    """获取当前用户"""
    return request._current_user


async def get_super_user(request: Request) -> Current_User:
    """获取超级用户"""
    if request._current_user.is_superuser:
        return request._current_user
    else:
        raise HTTPException(status_code=403,detail="not supperuser")
