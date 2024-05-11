# -*- coding: utf-8 -*-
from typing import Union

from sqladmin._menu import CategoryMenu, ViewMenu
from sqlalchemy import select, inspect

from apps.core.admin.base import DynamicModelView
from apps.core.db import DynamicBase, session_execute
from apps.core.models.relship import RelShip
from apps.core.models.view_config import ViewConfig
from apps.core.tools import get_column_label


async def reset_menu(menu: Union[CategoryMenu, ViewMenu]):
    """重置菜单"""
    if isinstance(menu, CategoryMenu):
        del_menu = []
        for c in menu.children:
            if await reset_menu(c):
                del_menu.append(c)
        for d in del_menu:
            menu.children.remove(d)
    else:
        if getattr(menu.view.model, "__is_dynamic__", None):
            return True


async def reset_view():
    """重置view"""
    from main import admin
    # 删除动态路由
    del_views = []
    for view in admin.views:
        if getattr(view.model, "__is_dynamic__", None):
            del_views.append(view)
    # 由于admin.views不能重新赋值，因此需要逐个删除
    for i in del_views:
        admin.views.remove(i)


async def dynamic_view():
    """动态加载admin view"""
    from main import admin
    from apps.core.compile.load import LoadORM
    # 重载动态ORM
    await LoadORM.load()
    # 重置view
    await reset_view()
    # 重置menu,保存外层没有类别的菜单
    del_menus = []
    for m in admin._menu.items:
        if await reset_menu(m):
            del_menus.append(m)
    for i in del_menus:
        admin._menu.items.remove(i)
    # 重新加载View
    for k, v in DynamicBase._orms.items():
        dv = DynamicView(v, admin)
        await dv.generate_view()


class DynamicView:
    """动态生成view"""

    def __init__(self, model, admin):
        self.model = model
        self.admin = admin
        self.config = None
        self.view = None
        self.kw = None
        self.entity_id = model.__entity__["id"]
        self.entity_name = model.__entity__["name"]

    async def get_list_column(self, attr):
        value = getattr(self.config, attr, None)
        if value is not None:
            return value.split(",")
        else:
            return []

    async def get_page_size_options(self):
        if self.config.page_size_options:
            return [int(p) for p in self.config.page_size_options.split(",")]
        else:
            return [10, 20, 50, 100]

    async def set_list_column(self):
        if self.config.column_list:
            if self.config.column_list == "__all__":
                self.kw["column_list"] = "__all__"
            else:
                self.kw["column_list"] = await self.get_list_column("column_list")
        elif self.config.column_exclude_list:
            self.kw["column_exclude_list"] = await self.get_list_column("column_exclude_list")

    async def set_details_column(self):
        if self.config.column_details_list:
            if self.config.column_details_list == "__all__":
                self.kw["column_details_list"] = "__all__"
            else:
                self.kw["column_details_list"] = await self.get_list_column("column_details_list")
        elif self.config.column_details_exclude_list:
            self.kw["column_details_exclude_list"] = await self.get_list_column("column_details_exclude_list")

    async def set_column_labels(self):
        column_labels = {i: get_column_label(i) for i in inspect(self.model).mapper.attrs}
        self.kw["column_labels"] = column_labels

    async def set_form_column(self):

        if self.config.form_columns:
            self.kw["form_columns"] = await self.get_list_column("form_columns")
        elif self.config.form_excluded_columns:
            self.kw["form_excluded_columns"] = await self.get_list_column("form_excluded_columns")

    async def set_export_column(self):

        if self.config.column_export_list:
            self.kw["column_export_list"] = await self.get_list_column("column_export_list")
        elif self.config.column_export_exclude_list:
            self.kw["column_export_exclude_list"] = await self.get_list_column("column_export_exclude_list")

    async def set_ajax_refs(self):
        """根据关联对象的配置，自动设置搜索"""
        form_ajax_refs = {}
        # 查询关系
        stmt = select(RelShip).where(RelShip.ref_entity_id==self.entity_id)
        result = await session_execute(stmt)
        for relship in result.scalars():
            # 查询视图设置
            stmt = select(ViewConfig).where(ViewConfig.entity_id==relship.refed_entity_id)
            result = await session_execute(stmt)
            view_config = result.scalar()
            if view_config:
                tmp = {}
                if view_config.column_searchable_list:
                    tmp["fields"] = tuple(view_config.column_searchable_list.split(","))
                if view_config.column_default_sort:
                    tmp["order_by"] = view_config.column_default_sort
                if tmp:
                    form_ajax_refs[relship.name] =tmp
        self.kw["form_ajax_refs"] = form_ajax_refs

    async def _view(self):
        """根据设置生成view"""
        self.kw = dict(
            model=self.model,
            # permission
            can_create=self.config.can_create,
            can_edit=self.config.can_edit,
            can_delete=self.config.can_delete,
            can_view_details=self.config.can_view_details,
            can_export=self.config.can_export,
            save_as=self.config.save_as,
            save_as_continue=self.config.save_as_continue,
            # Metadata
            name=self.config.name or self.entity_name,
            name_plural=self.config.name_plural or self.entity_name,
            icon=self.config.icon,
            category=self.config.category,
            # list
            page_size=self.config.page_size,
            page_size_options=await self.get_page_size_options(),
            column_searchable_list=await self.get_list_column("column_searchable_list"),
            column_sortable_list=await self.get_list_column("column_sortable_list"),
            column_default_sort=self.config.column_default_sort,
            list_template=self.config.list_template,
            create_template=self.config.create_template,
            details_template=self.config.details_template,
            edit_template=self.config.edit_template,
            export_max_rows=self.config.export_max_rows,
            export_types=await self.get_list_column("export_types"),
            form_include_pk=self.config.form_include_pk,
        )
        await self.set_list_column()
        await self.set_details_column()
        await self.set_column_labels()
        await self.set_export_column()
        await self.set_form_column()
        await self.set_ajax_refs()
        extend_class = DynamicModelView._extend_dynamic_views.get(self.entity_name)
        if extend_class:
            # 添加扩展功能
            excludes = ("__module__",
                        "__dict__",
                        "__weakref__",
                        "__doc__",
                        "__annotations__",
                        )
            extend_kw = {k: v for k, v in vars(extend_class).items() if k not in excludes}
            extend_kw["__maps_to__"] = extend_class.__maps_to__
            self.kw.update(extend_kw)
        TmpView = type("Dynamic{}View".format(self.entity_name.capitalize()), (DynamicModelView,), self.kw)
        return TmpView

    async def generate_view(self):
        """生成view"""
        stmt = select(ViewConfig).where(ViewConfig.entity_id == self.entity_id)
        result = await session_execute(stmt)
        self.config = result.scalar()
        if self.config and self.config.is_visible:
            self.view = await self._view()
            self.admin.add_view(self.view)
