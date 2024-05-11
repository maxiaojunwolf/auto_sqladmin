# -*- coding: utf-8 -*-
from typing import List

from sqlalchemy import String, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.core.db import Base
from apps.core.enums import Gender
from settings import NameSettings


class User(Base):
    """用户"""
    __tablename__ = f"{NameSettings.CORE_TABLE_PREFIX}_user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, doc="id", comment="id")
    name: Mapped[str] = mapped_column(String(64), index=True, doc="名称", comment="名称")
    login: Mapped[str] = mapped_column(String(64), index=True, unique=True, doc="登录名", comment="登录名")
    password: Mapped[str] = mapped_column(String(255), doc="密码", comment="密码")
    icon: Mapped[str] = mapped_column(String(255), nullable=True, doc="头像", comment="头像")
    gender: Mapped[str] = mapped_column(Enum(Gender), default=Gender.Male, doc="性别", comment="性别")
    department: Mapped[str] = mapped_column(String(255), nullable=True, doc="部门", comment="部门")
    title: Mapped[str] = mapped_column(String(255), nullable=True, doc="岗位", comment="岗位")
    mail: Mapped[str] = mapped_column(String(64), nullable=True, unique=True, doc="邮箱", comment="邮箱")
    mobile: Mapped[str] = mapped_column(String(32), nullable=True, unique=True, doc="手机", comment="手机")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, doc="激活", comment="激活")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, doc="超级用户", comment="超级用户")

    roles: Mapped[List["Role"]] = relationship('Role', secondary=f"{NameSettings.CORE_TABLE_PREFIX}_user2role",
                                               back_populates="users", lazy='noload', doc="角色")

    def __str__(self):
        return self.name
