# -*- coding: utf-8 -*-
from sqlalchemy import inspect

from apps.core.admin.base import CoreModelView
from apps.core.models.table import Table
from apps.core.tools import get_column_label


class TableAdmin(CoreModelView, model=Table):
    """类"""
    # Internals
    category = "管理"
    # Metadata
    name = "表"
    name_plural = "表"
    icon = "fa-solid fa-table"

    # List page
    column_list = ["id",
                   "name",
                   "label",
                   "create_date",
                   "update_date"]

    column_searchable_list = ["name"]
    column_sortable_list = ["name"]
    column_default_sort = [("name", True)]

    # detail page
    column_details_list = ["id",
                           "name",
                           "label",
                           "creator",
                           "create_date",
                           "updater",
                           "update_date"]

    # General options 自动从ORM获取doc作为属性标签
    column_labels = {i: get_column_label(i) for i in inspect(Table).mapper.attrs}
    # Form options
    form_widget_args_edit = {"name": {"readonly": True}
                             }
