# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import String, ForeignKey, Integer, DateTime, func, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.core.db import Base
from apps.core.tools import local_datetime
from settings import ServerSettings, NameSettings


class RelShip(Base):
    """关系：创建外键时会自动创建对应的索引，删除外键时可能会出错"""
    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_rel_ship"
    __table_args__ = (
        UniqueConstraint('ref_entity_id', 'refed_entity_id', 'link_entity_id'),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, doc="ID", comment="ID")
    name: Mapped[str] = mapped_column(String(128), unique=True, doc="名称（唯一标识）", comment="名称（唯一标识）")
    label: Mapped[str] = mapped_column(String(64), doc="标签", comment="标签")

    ref_entity_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_entity.id", ondelete="CASCADE"), doc="引用类ID",
        comment="引用类ID")
    link_entity_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_entity.id", ondelete="CASCADE"),
        doc="连接类ID",
        comment="连接类ID")
    refed_entity_id: Mapped[int] = mapped_column(
        ForeignKey(f"{NameSettings.CORE_TABLE_PREFIX}_entity.id", ondelete="CASCADE"), doc="被引用类ID",
        comment="被引用类ID")

    uselist: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True, doc="多对象", comment="多对象")
    foreign_keys: Mapped[str] = mapped_column(String(256), nullable=True, doc="外键", comment="外键")
    back_populates: Mapped[str] = mapped_column(String(128), nullable=True, doc="映射关系(back_populates)",
                                                comment="映射关系(back_populates)")
    backref: Mapped[str] = mapped_column(String(128), nullable=True, doc="映射关系(backref)",
                                         comment="映射关系(backref)")
    order_by: Mapped[str] = mapped_column(String(128), nullable=True, doc="排序", comment="排序")
    lazy: Mapped[str] = mapped_column(String(128), default="noload", nullable=True, doc="加载", comment="加载")
    passive_deletes: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True, doc="延迟删除",
                                                  comment="延迟删除")

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

    ref_entity: Mapped["Entity"] = relationship('Entity', foreign_keys=[ref_entity_id], lazy="noload", doc="引用类")
    link_entity: Mapped["Entity"] = relationship('Entity', foreign_keys=[link_entity_id], lazy="noload", doc="连接类")
    refed_entity: Mapped["Entity"] = relationship('Entity', foreign_keys=[refed_entity_id], lazy="noload",
                                                  doc="被引用类")

    def __str__(self):
        return self.name
