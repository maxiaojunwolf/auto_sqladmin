# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import String, ForeignKey, Integer, Boolean, DateTime, func, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.core.db import Base
from apps.core.enums import FieldTypes
from apps.core.tools import local_datetime
from settings import ServerSettings, NameSettings


class Field(Base):
    """属性"""
    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_field"
    __table_args__ = (
        UniqueConstraint('entity_id', 'name'),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, doc="ID", comment="ID")
    name: Mapped[str] = mapped_column(String(128),index=True, doc="属性名", comment="属性名")
    label: Mapped[str] = mapped_column(String(64), doc="标签", comment="标签")

    entity_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_entity.id", ondelete="CASCADE"), doc="类ID", comment="类ID")
    entity_name: Mapped[str] = mapped_column(String(128),index=True, doc="类", comment="类")
    field_type: Mapped[str] = mapped_column(Enum(FieldTypes), default=FieldTypes.String, doc="类型", comment="类型")
    default_: Mapped[str] = mapped_column(String(64), nullable=True, doc="默认值", comment="默认值")
    length: Mapped[int] = mapped_column(Integer, nullable=True, doc="长度", comment="长度")
    autoincrement: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", doc="自增", comment="自增")
    primary_key: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", doc="主键", comment="主键")
    nullable: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", doc="允许为空",
                                           comment="允许为空")
    choices: Mapped[int] = mapped_column(String(128), nullable=True, doc="可选值（使用,分割）", comment="可选值（使用,分割）")

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

    entity: Mapped["Entity"] = relationship('Entity', lazy='noload', doc="类")

    def __str__(self) -> str:
        return f"{self.entity_name}.{self.name}"
