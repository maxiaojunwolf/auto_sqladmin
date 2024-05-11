# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.core.db import Base
from apps.core.tools import local_datetime
from settings import ServerSettings, NameSettings


class User2Role(Base):
    """用户-角色"""
    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_user2role"

    user_id: Mapped[int] = mapped_column(ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_user.id", ondelete='CASCADE'),
                                         primary_key=True, doc="用户ID",
                                         comment="用户ID")
    role_id: Mapped[int] = mapped_column(ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_role.id", ondelete='CASCADE'),
                                         primary_key=True, doc="角色ID",
                                         comment="角色ID")


class Role(Base):
    """角色"""
    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, doc="id", comment="id")
    name: Mapped[str] = mapped_column(String(128), unique=True, doc="名称（唯一标识）", comment="名称（唯一标识）")
    label: Mapped[str] = mapped_column(String(64), doc="标签", comment="标签")

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

    users: Mapped[List["User"]] = relationship('User', secondary=f"{NameSettings.CORE_TABLE_PREFIX}_user2role",
                                               back_populates="roles",
                                               lazy='noload', doc="用户")

    creator = relationship('User', foreign_keys=[creator_id], lazy='noload', doc='创建者')
    updater = relationship('User', foreign_keys=[updater_id], lazy='noload', doc='更新者')
    view_configs: Mapped[List["ViewConfig"]] = relationship('ViewConfig', back_populates="roles",
                                                            secondary=f"{NameSettings.CORE_TABLE_PREFIX}_role2viewconfig",
                                                            lazy='noload', doc="视图配置")

    def __str__(self):
        return self.name
