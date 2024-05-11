# -*- coding: utf-8 -*-
from typing import Any

from sqladmin.exceptions import SQLAdminException
from sqlalchemy import inspect, select, func
from starlette.exceptions import HTTPException
from starlette.requests import Request
from wtforms import ValidationError

from apps.core.admin.base import CoreModelView
from apps.core.enums import FieldTypes
from apps.core.models.entity import Entity
from apps.core.models.field import Field
from apps.core.tools import get_column_label


class FieldAdmin(CoreModelView, model=Field):
    """属性"""
    # Internals
    category = "管理"
    # Metadata
    name = "属性"
    name_plural = "属性"
    icon = "fa-solid fa-table-columns"

    # List page
    column_list = ["id",
                   "name",
                   "entity_name",
                   "field_type",
                   "label",
                   "create_date",
                   "update_date"]

    column_searchable_list = ["name"]
    column_sortable_list = ["name"]
    column_default_sort = [("id", True)]

    # detail page
    column_details_list = ["id",
                           "name",
                           "entity_name",
                           "entity",
                           "field_type",
                           "default_",
                           "length",
                           "autoincrement",
                           "primary_key",
                           "nullable",
                           "creator",
                           "create_date",
                           "updater",
                           "update_date",
                           ]

    # General options
    column_labels = {i: get_column_label(i) for i in inspect(Field).mapper.attrs}
    form_excluded_columns = ["entity_name", *CoreModelView.form_excluded_columns]
    form_widget_args_edit = {"name": {"readonly": True}, "field_type": {"readonly": True}}
    # Form options
    form_ajax_refs = {

        "entity": {
            "fields": ("name",),
            "order_by": "name",
        }
    }

    async def check_primary_key(self,entity_id:int,exclude_field_id:int):
        """校验类必须包含主键列"""
        stmt = select(func.count()).where(Field.entity_id==entity_id,Field.primary_key==True)
        if exclude_field_id:
            stmt = stmt.where(Field.id!=exclude_field_id)
        result = await self._run_query(stmt)
        return result[0]


    async def insert_model(self, request: Request, data: dict) -> Any:
        """新建时保存类名称"""
        stmt = select(Entity.name).where(Entity.id == int(data["entity"]))
        result = await self._run_query(stmt)
        data["entity_name"] = result[0]
        return await super().insert_model(request, data)

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        """新建或修改时，校验"""
        if data["field_type"] == FieldTypes.Enum.value:
            if not data["choices"]:
                raise ValidationError("Enum类型，可选值不能为空")
            else:
                if data["default_"] and (data["default_"] in data["choices"].split(",")):
                    raise ValidationError("默认值不在可选值中")
        await super().on_model_change(data, model, is_created, request)

    async def update_model(self, request: Request, pk: str, data: dict) -> Any:
        """更新时"""
        if not data["primary_key"]:
            has_primary_key = await self.check_primary_key(int(data["entity"]), int(pk))
            if not has_primary_key:
                raise ValidationError("类必须包含主键列")
        return await super().update_model(request, pk, data)



