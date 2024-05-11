# -*- coding: utf-8 -*-
from sqlalchemy import inspect

from apps.core.admin.base import CoreModelView
from apps.core.models.relship import RelShip
from apps.core.tools import get_column_label


class RelShipAdmin(CoreModelView, model=RelShip):
    """关系"""
    # Internals
    category = "管理"
    # Metadata
    name = "关系"
    name_plural = "关系"
    icon = "fa-solid fa-bridge"

    # List page
    column_list = ["id",
                   "name",
                   "label",
                   "ref_entity",
                   "link_entity",
                   "refed_entity",
                   "create_date",
                   "update_date"]
    # column_exclude_list = [RelShip.create_date,RelShip.update_date]
    column_searchable_list = ["name"]
    column_sortable_list = ["name"]
    column_default_sort = [("name", True)]

    # detail page
    column_details_list = ["id",
                           "name",
                           "label",
                           "ref_entity",
                           "link_entity",
                           "refed_entity",
                           "uselist",
                           "foreign_keys",
                           "back_populates",
                           "backref",
                           "order_by",
                           "lazy",
                           "passive_deletes",
                           "creator",
                           "create_date",
                           "updater",
                           "update_date"]

    # General options
    column_labels = {i: get_column_label(i) for i in inspect(RelShip).mapper.attrs}

    # Form options
    form_widget_args_edit = {"name": {"readonly": True}}
    form_ajax_refs = {

        "ref_entity": {
            "fields": ("name",),
            "order_by": "name",
        },
        "link_entity": {
            "fields": ("name",),
            "order_by": "name",
        },
        "refed_entity": {
            "fields": ("name",),
            "order_by": "name",
        },
    }
