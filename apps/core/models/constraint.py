# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, String, Integer, DateTime, func, UniqueConstraint, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from apps.core.db import Base
from apps.core.enums import ForeignKeyStrategy
from apps.core.tools import local_datetime
from settings import ServerSettings, NameSettings


class Unique_Constraint2field(Base):
    """唯一约束2属性"""

    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_unique_constraint2field"

    constraint_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_unique_constraint.id", ondelete="CASCADE"),
        primary_key=True,
        doc="约束id", comment="约束id")
    field_id: Mapped[int] = mapped_column(ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_field.id", ondelete="CASCADE"),
                                          primary_key=True,
                                          doc="属性id",
                                          comment="属性id")


class Unique_Constraint(Base):
    """唯一约束：通过创建unique索引实现"""

    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_unique_constraint"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, doc="ID", comment="ID")
    label: Mapped[str] = mapped_column(String(64),doc="标签", comment="标签")
    entity_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_entity.id", ondelete="CASCADE"), doc="类ID",
        comment="类ID")

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

    entity: Mapped["Entity"] = relationship('Entity', lazy="noload", doc="类")
    fields: Mapped[List["Field"]] = relationship('Field',
                                                 secondary=f"{NameSettings.CORE_TABLE_PREFIX}_unique_constraint2field",
                                                 lazy="noload",
                                                 cascade = 'all, delete',
                                                 doc="属性")

    def __str__(self):
        return self.label


class Index_Constraint2field(Base):
    """索引2属性"""

    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_index_constraint2field"

    constraint_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_index_constraint.id", ondelete="CASCADE"),
        primary_key=True,
        doc="约束id", comment="约束id")
    field_id: Mapped[int] = mapped_column(ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_field.id", ondelete="CASCADE"),
                                          primary_key=True,
                                          doc="属性id",
                                          comment="属性id")


class Index_Constraint(Base):
    """索引约束"""

    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_index_constraint"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, doc="ID", comment="ID")
    label: Mapped[str] = mapped_column(String(64), doc="标签", comment="标签")
    entity_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_entity.id", ondelete="CASCADE"), doc="类ID",
        comment="类ID")


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

    entity: Mapped["Entity"] = relationship('Entity', lazy="noload", doc="类")
    fields: Mapped[List["Field"]] = relationship('Field',
                                                 secondary=f"{NameSettings.CORE_TABLE_PREFIX}_index_constraint2field",
                                                 lazy="noload",
                                                 cascade='all, delete',
                                                 doc="属性")

    def __str__(self):
        return self.label


class ForeignKey_Constraint(Base):
    """外键约束"""
    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_foreignkey_constraint"

    __table_args__ = (
        UniqueConstraint("ref_field_id", "refed_field_id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, doc="ID", comment="ID")
    label: Mapped[str] = mapped_column(String(64), doc="标签", comment="标签")
    entity_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_entity.id", ondelete="CASCADE"), doc="引用类ID",
        comment="引用类ID")
    ref_field_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_field.id", ondelete="CASCADE"), doc="链接类id",
        comment="链接类id")

    refed_field_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_field.id", ondelete="CASCADE"),
        doc="被引用类id",
        comment="被引用类id")

    on_update: Mapped[str] = mapped_column(Enum(ForeignKeyStrategy), default=ForeignKeyStrategy.RESTRICT, doc="更新时",
                                           comment="更新时")
    on_delete: Mapped[str] = mapped_column(Enum(ForeignKeyStrategy), default=ForeignKeyStrategy.RESTRICT, doc="删除时",
                                           comment="删除时")

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

    entity: Mapped["Entity"] = relationship('Entity', lazy="noload", doc="类")
    ref_field: Mapped["Field"] = relationship('Field', foreign_keys=[ref_field_id], lazy='noload', doc="引用属性")
    refed_field: Mapped["Field"] = relationship('Field', foreign_keys=[refed_field_id], lazy='noload', doc="被引用属性")

    def __str__(self):
        return self.label
