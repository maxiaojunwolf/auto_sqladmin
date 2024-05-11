# -*- coding: utf-8 -*-
from typing import Any

from sqlalchemy import inspect, select
from starlette.requests import Request

from apps.core.admin.base import CoreModelView
from apps.core.models.user import User
from apps.core.tools import encrypt_password, get_column_label


class UserAdmin(CoreModelView, model=User):
    """类"""
    # Internals
    category = "组织"
    # Metadata
    name = "用户"
    name_plural = "用户"
    icon = "fa-solid fa-user"

    # List page
    column_list = ["id",
                   "name",
                   "login",
                   "gender",
                   "department",
                   "title",
                   "mail",
                   "is_active",
                   "is_superuser",
                   ]

    column_searchable_list = ["name"]
    column_soruser_list = ["name"]
    column_default_sort = [("id", True)]

    # detail page
    column_details_list = ["id",
                           "icon",
                           "name",
                           "login",
                           "password",
                           "gender",
                           "department",
                           "title",
                           "mail",
                           "mobile",
                           "is_active",
                           "is_superuser",
                           "roles",
                           "creator",
                           "create_date",
                           "updater",
                           "update_date"]

    # General options 自动从ORM获取doc作为属性标签
    column_labels = {i: get_column_label(i) for i in inspect(User).mapper.attrs}
    # Form options
    form_widget_args_edit = {"login": {"readonly": True}}
    form_ajax_refs = {
        "roles": {
            "fields": ("name",),
            "order_by": "name",
        },
    }

    async def insert_model(self, request: Request, data: dict) -> Any:
        data["password"] = encrypt_password(data["login"], data["password"])
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: str, data: dict) -> Any:
        async with self.session_maker() as session:
            stmt = select(User.password).where(User.id == int(pk))
            password = await session.scalar(stmt)
            if password != data["password"]:
                data["password"] = encrypt_password(data["login"], data["password"])
        return await super().update_model(request, pk, data)
