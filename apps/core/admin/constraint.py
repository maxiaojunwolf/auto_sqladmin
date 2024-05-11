# -*- coding: utf-8 -*-
from sqlalchemy import select, inspect

from apps.core.admin.base import CoreModelView
from apps.core.models.constraint import Unique_Constraint, Index_Constraint, ForeignKey_Constraint
from apps.core.models.field import Field
from apps.core.tools import get_column_label


class Unique_ConstraintAdmin(CoreModelView, model=Unique_Constraint):
    """唯一约束"""
    # Internals
    category = "管理"
    # Metadata
    name = "约束"
    name_plural = "约束"
    icon = "fa-solid fa-road-barrier"

    # List page
    column_list = ["id",
                   "label",
                   "entity",
                   "create_date",
                   "update_date"]

    column_searchable_list = ["label"]
    column_sortable_list = ["entity", "label"]
    column_default_sort = [("id", True)]

    # detail page
    column_details_list = ["id",
                           "label",
                           "entity",
                           "fields",
                           "creator",
                           "create_date",
                           "updater",
                           "update_date"]

    # General options
    column_labels = {i: get_column_label(i) for i in inspect(Unique_Constraint).mapper.attrs}
    # Form options
    form_ajax_refs = {

        "entity": {
            "fields": ("name",),
            "order_by": "name",
        },
        "fields": {
            "fields": ("entity_name", "name",),
            "order_by": "name",
        }
    }


class Index_ConstraintAdmin(CoreModelView, model=Index_Constraint):
    """索引"""
    # Internals
    category = "管理"
    # Metadata
    name = "索引"
    name_plural = "索引"
    icon = "fa-solid fa-book"

    # List page
    column_list = ["id",
                   "label",
                   "entity",
                   "create_date",
                   "update_date"]

    column_searchable_list = ["label"]
    column_sortable_list = ["label"]
    column_default_sort = [("id", True)]

    # detail page
    column_details_list = ["id",
                           "label",
                           "entity",
                           "fields",
                           "creator",
                           "create_date",
                           "updater",
                           "update_date"]

    # General options
    column_labels = {i: get_column_label(i) for i in inspect(Index_Constraint).mapper.attrs}
    # Form options
    form_ajax_refs = {

        "entity": {
            "fields": ("name",),
            "order_by": "name",
        },
        "fields": {
            "fields": ("entity_name", "name",),
            "order_by": "name",
        }
    }


class ForeignKey_ConstraintAdmin(CoreModelView, model=ForeignKey_Constraint):
    """外键"""
    # Internals
    category = "管理"
    # Metadata
    name = "外键"
    name_plural = "外键"
    icon = "fa-solid fa-key"

    # List page
    column_list = ["id",
                   "label",
                   "entity",
                   "ref_field",
                   "refed_field",
                   "on_update",
                   "on_delete",
                   "create_date",
                   "update_date"]

    column_searchable_list = ["entity"]
    column_sortable_list = ["entity"]
    column_default_sort = [("id", True)]

    # detail page
    column_details_list = ["id",
                           "label",
                           "entity",
                           "ref_field",
                           "refed_field",
                           "on_update",
                           "on_delete",
                           "creator",
                           "create_date",
                           "updater",
                           "update_date"]

    # General options
    column_labels = {i: get_column_label(i) for i in inspect(ForeignKey_Constraint).mapper.attrs}

    # Form options
    form_excluded_columns = ["entity", *CoreModelView.form_excluded_columns]
    form_ajax_refs = {
        "ref_field": {
            "fields": ("entity_name", "name",),
            "order_by": "name",
        },
        "refed_field": {
            "fields": ("entity_name", "name",),
            "order_by": "name",
        }
    }

    async def on_model_change(self, data, model, is_created, request):
        """自动更新entity_id"""
        stmt = select(Field.entity_id).where(Field.id == int(data["ref_field"]))
        result = await self._run_query(stmt)
        data["entity_id"] = result[0]
        await super().on_model_change(data, model, is_created, request)
