# -*- coding: utf-8 -*-
from typing import Any

from sqlalchemy import inspect, select
from starlette.requests import Request

from apps.core.admin.base import CoreModelView
from apps.core.admin.load import dynamic_view
from apps.core.models.entity import Entity
from apps.core.models.view_config import ViewConfig
from apps.core.tools import get_column_label


class ViewConfigAdmin(CoreModelView, model=ViewConfig):
    """视图设置"""
    # Internals
    category = "管理"
    # Metadata
    name = "视图"
    name_plural = "视图"
    icon = "fa-solid fa-gear"

    # List page
    column_list = ["id",
                   "entity",
                   "can_create",
                   "can_edit",
                   "can_delete",
                   "can_view_details",
                   "can_export",
                   ]

    column_searchable_list = ["entity"]
    column_sortable_list = ["entity"]
    column_default_sort = [("id", True)]

    # detail page
    column_labels = {i: get_column_label(i) for i in inspect(ViewConfig).mapper.attrs}

    # Form options
    form_excluded_columns = ["entity_name", *CoreModelView.form_excluded_columns]
    form_widget_args_edit = {"entity": {"readonly": True}}
    form_ajax_refs = {
        "entity": {
            "fields": ("name",),
            "order_by": "name",
        }
    }

    async def insert_model(self, request: Request, data: dict) -> Any:
        """新建时保存类名称"""
        stmt = select(Entity.name).where(Entity.id == int(data["entity"]))
        result = await self._run_query(stmt)
        data["entity_name"] = result[0]
        return await super().insert_model(request, data)

    async def after_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        """配置变化时自动更新View"""
        await super().after_model_change(data, model, is_created, request)
        await dynamic_view()

    async def after_model_delete(self, model: Any, request: Request) -> None:
        """配置变化时自动更新View"""
        await super().after_model_delete(model, request)
        await dynamic_view()
