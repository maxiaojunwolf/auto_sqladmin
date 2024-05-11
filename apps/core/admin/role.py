# -*- coding: utf-8 -*-
from sqlalchemy import inspect

from apps.core.admin.base import CoreModelView
from apps.core.models.role import Role
from apps.core.tools import get_column_label


class RoleAdmin(CoreModelView, model=Role):
    """角色"""
    # Internals
    category = "组织"
    # Metadata
    name = "角色"
    name_plural = "角色"
    icon = "fa-solid fa-people-roof"

    # List page
    column_list = ["id",
                   "name",
                   "label",
                   "create_date",
                   "update_date",
                   ]

    column_searchable_list = ["name"]
    column_sorrole_list = ["name"]
    column_default_sort = [("id", True)]

    # detail page
    column_details_list = ["id",
                           "name",
                           "label",
                           "view_configs",
                           "creator",
                           "create_date",
                           "updater",
                           "update_date"]

    # General options 自动从ORM获取doc作为属性标签
    column_labels = {i: get_column_label(i) for i in inspect(Role).mapper.attrs}
    # Form options
    form_widget_args_edit = {"name": {"readonly": True}}
