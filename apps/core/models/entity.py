# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from sqlalchemy import Boolean, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.core.db import Base
from apps.core.tools import local_datetime
from settings import ServerSettings, NameSettings


class Entity(Base):
    """类"""

    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_entity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, doc="ID", comment="ID")

    name: Mapped[str] = mapped_column(String(128), unique=True, doc="类名", comment="类名")
    label: Mapped[str] = mapped_column(String(64), doc="标签", comment="标签")
    table_id: Mapped[int] = mapped_column(ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_table.id"), unique=True,
                                          doc="表id", comment="表id")
    table_name: Mapped[str] = mapped_column(String(128),doc="表名", comment="表名")
    compiled: Mapped[bool] = mapped_column(Boolean, default=False, doc="是否编译", comment="是否编译")

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
    # 创建人
    creator: Mapped["User"] = relationship('User', foreign_keys=[creator_id], lazy='noload', doc='创建者')
    # 更新人
    updater: Mapped["User"] = relationship('User', foreign_keys=[updater_id], lazy='noload', doc='更新者')

    # 表
    table: Mapped["Table"] = relationship('Table', lazy="noload", doc="表")
    # 属性
    fields: Mapped[List["Field"]] = relationship('Field', lazy="noload", viewonly=True, order_by="Field.id", doc="属性")
    # 唯一约束
    unique_constraints: Mapped[List["Unique_Constraint"]] = relationship('Unique_Constraint', lazy="noload",
                                                                         viewonly=True, order_by="Unique_Constraint.id",
                                                                         doc="唯一约束")
    # 索引
    index_constraints: Mapped[List["Index_Constraint"]] = relationship('Index_Constraint', lazy="noload", viewonly=True,
                                                                       order_by="Index_Constraint.id", doc="索引")
    # 外键
    foreignkey_constraints: Mapped[List["ForeignKey_Constraint"]] = relationship('ForeignKey_Constraint', lazy="noload",
                                                                                 viewonly=True,
                                                                                 order_by="ForeignKey_Constraint.id",
                                                                                 doc="外键")
    # 关系
    relships: Mapped[List["RelShip"]] = relationship('RelShip', back_populates="ref_entity",
                                                     foreign_keys="RelShip.ref_entity_id", lazy="noload", viewonly=True,
                                                     order_by="RelShip.id", doc="关系")

    def __str__(self):
        return self.name
