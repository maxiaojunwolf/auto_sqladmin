# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, func, Boolean, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.core.db import Base
from apps.core.tools import local_datetime
from settings import ServerSettings, NameSettings


class Role2ViewConfig(Base):
    """角色-菜单"""
    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_role2viewconfig"

    role_id: Mapped[int] = mapped_column(ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_role.id", ondelete='CASCADE'),
                                         primary_key=True, doc="角色ID",
                                         comment="角色ID")
    view_config_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_view_config.id", ondelete='CASCADE'), primary_key=True,
        doc="视图设置ID",
        comment="视图设置ID")


class ViewConfig(Base):
    """设置"""
    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_view_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, doc="ID", comment="ID")
    entity_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_entity.id", ondelete="CASCADE"), doc="引用类ID",
        comment="引用类ID")
    entity_name: Mapped[str] = mapped_column(String(128), doc="类", comment="类")
    # permission
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, doc="是否可见", comment="是否可见")
    can_create: Mapped[bool] = mapped_column(Boolean, default=True, doc="允许新建", comment="允许新建")
    can_edit: Mapped[bool] = mapped_column(Boolean, default=True, doc="允许编辑", comment="允许编辑")
    can_delete: Mapped[bool] = mapped_column(Boolean, default=True, doc="允许删除", comment="允许删除")
    can_view_details: Mapped[bool] = mapped_column(Boolean, default=True, doc="允许查看", comment="允许查看")
    can_export: Mapped[bool] = mapped_column(Boolean, default=True, doc="允许导出", comment="允许导出")
    save_as: Mapped[bool] = mapped_column(Boolean, default=False, doc="保存为", comment="保存为")
    save_as_continue: Mapped[bool] = mapped_column(Boolean, default=True, doc="保存并查看", comment="保存并查看")

    # Metadata
    name: Mapped[str] = mapped_column(String(32), nullable=True, doc="名称", comment="名称")
    name_plural: Mapped[str] = mapped_column(String(32), nullable=True, doc="名称(复数)", comment="名称(复数)")
    icon: Mapped[str] = mapped_column(String(128), nullable=True, doc="图标", comment="图标")
    category: Mapped[str] = mapped_column(String(128), nullable=True, doc="菜单组", comment="菜单组")

    # list
    # column_formatters = {}
    column_list: Mapped[str] = mapped_column(String(256), default="__all__", doc="列表显示属性（使用,分割）",
                                             comment="列表显示属性（使用,分割）")
    column_exclude_list: Mapped[str] = mapped_column(String(256), nullable=True, doc="列表隐藏属性（使用,分割）",
                                                     comment="列表隐藏属性（使用,分割）")
    page_size: Mapped[int] = mapped_column(Integer, default=10, doc="每页数量", comment="每页数量")
    page_size_options: Mapped[str] = mapped_column(String(128), default="10,25,50,100", doc="可选的每页数量（使用,分割）",
                                                   comment="可选的每页数量（使用,分割）")
    column_searchable_list: Mapped[str] = mapped_column(String(256), nullable=True, doc="可搜索属性（使用,分割）",
                                                        comment="可搜索属性（使用,分割）")
    column_sortable_list: Mapped[str] = mapped_column(String(256), nullable=True, doc="可以排序属性（使用,分割）",
                                                      comment="可以排序属性（使用,分割）")
    column_default_sort: Mapped[str] = mapped_column(String(256), nullable=True, doc="默认排序属性",
                                                     comment="默认排序属性")

    # detail page
    column_details_list: Mapped[str] = mapped_column(String(256), default="__all__", doc="详情显示属性（使用,分割）",
                                                     comment="详情显示属性（使用,分割）")
    column_details_exclude_list: Mapped[str] = mapped_column(String(256), nullable=True, doc="详情隐藏属性（使用,分割）",
                                                             comment="详情隐藏属性（使用,分割）")
    # column_formatters_detail = {}

    # General options
    # column_labels: Mapped[dict] = mapped_column(JSON, nullable=True, doc="属性标签", comment="属性标签")
    # column_type_formatters = {}

    # Templates
    list_template: Mapped[str] = mapped_column(String(256), default="list.html", doc="列表模板", comment="列表模板")
    create_template: Mapped[str] = mapped_column(String(256), default="create.html", doc="新建模板", comment="新建模板")
    details_template: Mapped[str] = mapped_column(String(256), default="details.html", doc="详情模板",
                                                  comment="详情模板")
    edit_template: Mapped[str] = mapped_column(String(256), default="edit.html", doc="编辑模板", comment="编辑模板")

    # Export options
    column_export_list: Mapped[str] = mapped_column(String(256), nullable=True, doc="导出显示属性（使用,分割）",
                                                    comment="导出显示属性（使用,分割）")
    column_export_exclude_list: Mapped[str] = mapped_column(String(256), nullable=True, doc="导出隐藏属性（使用,分割）",
                                                            comment="导出隐藏属性（使用,分割）")
    export_max_rows: Mapped[int] = mapped_column(Integer, default=0, doc="最大导出行数（0表示导出所有）",
                                                 comment="最大导出行数（0表示导出所有）")
    export_types: Mapped[str] = mapped_column(String(256), default="csv", doc="导出类型", comment="导出类型")

    # Form options
    form_columns: Mapped[str] = mapped_column(String(256), nullable=True, doc="表单显示属性（使用,分割）",
                                              comment="表单显示属性（使用,分割）")
    form_excluded_columns = mapped_column(String(256), default="id,create_date,update_date,creator,updater",
                                          doc="表单隐藏属性（使用,分割）", comment="表单隐藏属性（使用,分割）")
    form_include_pk: Mapped[bool] = mapped_column(Boolean, default=False, doc="是否包含主键", comment="是否包含主键")
    # form_ajax_refs: Mapped[dict] = mapped_column(JSON, nullable=True, doc="关联对象搜索", comment="关联对象搜索")

    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_user.id"),
                                            doc="创建者id", comment='创建者id')
    updater_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_user.id"),
                                            nullable=True, doc="更新者id", comment='更新者id')
    create_date: Mapped[datetime] = mapped_column(DateTime, default=local_datetime,
                                                  server_default=func.now(timezone=ServerSettings.TIMEZONE),
                                                  doc="创建日期",
                                                  comment="创建日期")
    update_date: Mapped[datetime] = mapped_column(DateTime, default=local_datetime,
                                                  server_default=func.now(timezone=ServerSettings.TIMEZONE),
                                                  onupdate=func.now(timezone=ServerSettings.TIMEZONE),
                                                  doc="更新日期",
                                                  comment="更新日期")

    creator: Mapped["User"] = relationship('User', foreign_keys=[creator_id], lazy='noload', doc='创建者')
    updater: Mapped["User"] = relationship('User', foreign_keys=[updater_id], lazy='noload', doc='更新者')

    entity: Mapped["Entity"] = relationship('Entity', lazy='noload', doc="类")
    roles: Mapped[list["Role"]] = relationship('Role', back_populates="view_configs",
                                               secondary=f"{NameSettings.CORE_TABLE_PREFIX}_role2viewconfig",
                                               lazy="noload", doc="角色")

    def __str__(self):
        return f"{self.entity_name}"
