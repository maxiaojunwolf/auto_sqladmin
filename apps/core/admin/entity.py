# -*- coding: utf-8 -*-
import os
import re
import shutil
import subprocess
from typing import Any

from sqladmin import action
from sqlalchemy import text, inspect, update, select
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from apps.core.admin.base import CoreModelView
from apps.core.admin.load import dynamic_view
from apps.core.db import connect_execute
from apps.core.enums import FieldTypes
from apps.core.models.entity import Entity
from apps.core.models.field import Field
from apps.core.models.table import Table
from apps.core.tools import get_versions_path, get_column_label


class EntityAdmin(CoreModelView, model=Entity):
    """类"""
    # Internals
    pk_columns = ["name"]
    category = "管理"
    form_include_pk = True
    # Metadata
    name = "类"
    name_plural = "类"
    icon = "fa-solid fa-landmark"

    # List page
    column_list = ["name",
                   "label",
                   "table_name",
                   "compiled",
                   "create_date",
                   "update_date"]

    column_searchable_list = ["name"]
    column_sortable_list = ["name"]
    column_default_sort = [("create_date", True)]

    # detail page
    column_details_list = ["name",
                           "label",
                           "table_name",
                           "compiled",
                           "foreignkey_constraints",
                           "index_constraints",
                           "unique_constraints",
                           "relships",
                           "creator",
                           "create_date",
                           "updater",
                           "update_date",
                           ]

    # General options
    column_labels = {i: get_column_label(i) for i in inspect(Entity).mapper.attrs}

    # Form options
    form_ajax_refs = {
        "table": {
            "fields": ("name",),
            "order_by": "name",
        },
    }
    form_widget_args_edit = {"name": {"readonly": True}
                             }
    form_columns = ["name",
                    "label",
                    "table",
                    ]

    async def insert_field(self, session, *, entity_id: int, field_name: str, label: str, field_type: FieldTypes,
                           **kwargs):
        """生成Field"""
        field_id = Field(name=field_name,
                         entity_id=entity_id,
                         label=label,
                         field_type=field_type,
                         **kwargs
                         )
        session.add(field_id)

    async def insert_default_fields(self, model: Any, request: Request):
        """新建默认字段"""
        async with self.session_maker() as session:
            # 新建id
            await self.insert_field(session,
                                    entity_id=model.id,
                                    entity_name=model.name,
                                    field_name="id",
                                    label="ID",
                                    field_type=FieldTypes.Integer,
                                    autoincrement=True,
                                    primary_key=True,
                                    creator_id=request._current_user.id
                                    )
            # 新建name
            await self.insert_field(session,
                                    entity_id=model.id,
                                    entity_name=model.name,
                                    field_name="name",
                                    label="名称",
                                    field_type=FieldTypes.String,
                                    length=128,
                                    nullable=True,
                                    creator_id=request._current_user.id
                                    )
            # 新建创建日期
            await self.insert_field(session,
                                    entity_id=model.id,
                                    entity_name=model.name,
                                    field_name="create_date",
                                    label="创建日期",
                                    field_type=FieldTypes.DateTime,
                                    default_="now",
                                    creator_id=request._current_user.id
                                    )
            # 新建更新日期
            await self.insert_field(session,
                                    entity_id=model.id,
                                    entity_name=model.name,
                                    field_name="update_date",
                                    label="更新日期",
                                    field_type=FieldTypes.DateTime,
                                    default_="now",
                                    nullable=True,
                                    creator_id=request._current_user.id
                                    )
            await session.commit()

    async def after_model_change(self, data: dict, model: Any, is_created: bool, request: Request):
        """创建类时自动创建id,create_date,update_date"""
        await super().after_model_change(data, model, is_created, request)
        if is_created:
            await self.insert_default_fields(model, request)

    async def get_alembic_version(self):
        """查询当前版本"""
        stmt = text("select version_num from alembic_version")
        cur = await connect_execute(stmt)
        if cur.rowcount:
            return cur.scalar()

    # action 自定义操作
    @action(
        name="reload_view",
        label="重载View",
        confirmation_message="确认重新加载View?",
        add_in_detail=False,
        add_in_list=True,
    )
    async def action_4(self, request: Request):
        """编译"""
        await dynamic_view()
        return RedirectResponse(request.url_for("admin:list", identity=self.identity))

    @action(
        name="compile",
        label="编译",
        confirmation_message="确认执行编译?",
        add_in_detail=False,
        add_in_list=True,
    )
    async def action_3(self, request: Request):
        """编译"""
        result = subprocess.run("alembic revision --autogenerate -m '{}'".format(self.identity), shell=True,
                                capture_output=True)
        version_file = re.findall(r".*Generating (.*?)\.py", result.stdout.decode())
        if version_file:
            return RedirectResponse(request.url_for("admin:list", identity=self.identity))
        else:
            raise HTTPException(status_code=500, detail=result.stderr.decode())

    @action(
        name="migrate",
        label="迁移",
        confirmation_message="确认执行迁移?",
        add_in_detail=False,
        add_in_list=True,
    )
    async def action_2(self, request: Request):
        """迁移"""
        # 查询当前版本
        cur_version = await self.get_alembic_version()
        result = subprocess.run("alembic upgrade head", shell=True, capture_output=True)
        new_version = await self.get_alembic_version()
        if new_version != cur_version:
            # 更新编译状态
            stmt = update(Entity).values(compiled=True)
            await connect_execute(stmt)
            # 重新加载动态ORM
            await dynamic_view()
            return RedirectResponse(request.url_for("admin:list", identity=self.identity))
        else:
            raise HTTPException(status_code=500, detail=result.stderr.decode())

    @action(
        name="clear_version",
        label="版本修复",
        confirmation_message="确认执行版本修复?",
        add_in_detail=False,
        add_in_list=True,
    )
    async def action_1(self, request: Request):
        """清空版本"""
        # 清除当前版本
        stmt = text("delete from alembic_version")
        await connect_execute(stmt)
        # 清除历史迁移文件
        versions_path = get_versions_path()
        if os.path.exists(versions_path):
            shutil.rmtree(versions_path)
            os.mkdir(versions_path)
        return RedirectResponse(request.url_for("admin:list", identity=self.identity))


    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> Any:
        """新建时保存表名称"""
        stmt = select(Table.name).where(Table.id == int(data["table"]))
        result = await self._run_query(stmt)
        data["table_name"] = result[0]
        return await super().on_model_change( data,model,is_created,request)


    async def after_model_delete(self, model: Any, request: Request) -> None:
        """删除类时自动刷新View"""
        await super().after_model_delete(model, request)
        await dynamic_view()
