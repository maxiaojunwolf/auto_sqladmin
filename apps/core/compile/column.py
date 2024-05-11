# -*- coding: utf-8 -*-
import json
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, func, Boolean, Text, JSON, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column

from apps.core.enums import FieldTypes
from apps.core.models.field import Field


class DynamicColumn:
    """动态列"""
    Column_Type = None

    @classmethod
    async def compile(cls, field: Field):
        """编译"""
        raise NotImplementedError


class DynamicColumnString(DynamicColumn):
    """字符型"""
    Column_Type = String
    Default_Length = 128

    @classmethod
    async def compile(cls, field: Field):
        """编译"""
        kw = {"default": field.default_,
              "nullable": field.nullable,
              "comment": field.label,
              "primary_key": field.primary_key,
              "doc": field.label
              }
        column: Mapped[str] = mapped_column(cls.Column_Type(field.length or cls.Default_Length), **kw)
        return column


class DynamicColumnText(DynamicColumn):
    """长文本"""
    Column_Type = Text

    @classmethod
    async def compile(cls, field: Field):
        """编译"""
        kw = {"default": field.default_,
              "nullable": field.nullable,
              "comment": field.label,
              "doc": field.label
              }
        if field.length:
            column: Mapped[str] = mapped_column(cls.Column_Type(field.length), **kw)
        else:
            column: Mapped[str] = mapped_column(cls.Column_Type, **kw)
        return column


class DynamicColumnInteger(DynamicColumn):
    """整数"""
    Column_Type = Integer

    @classmethod
    async def compile(cls, field: Field):
        """编译"""
        kw = {"nullable": field.nullable,
              "primary_key": field.primary_key,
              "comment": field.label,
              "doc": field.label
              }
        if field.default_:
            try:
                kw["default"] = field.default_ and int(field.default_)
            except:
                kw["default"] = 0
        column: Mapped[int] = mapped_column(cls.Column_Type, **kw)
        return column


class DynamicColumnFloat(DynamicColumn):
    """小数"""
    Column_Type = Float

    @classmethod
    async def compile(cls, field: Field):
        """编译"""
        kw = {"nullable": field.nullable,
              "comment": field.label,
              "doc": field.label
              }
        if field.default_:
            try:
                kw["default"] = field.default_ and float(field.default_)
            except:
                kw["default"] = 0.0
        column: Mapped[int] = mapped_column(cls.Column_Type, **kw)
        return column


class DynamicColumnDateTime(DynamicColumn):
    """日期"""
    Column_Type = DateTime

    @classmethod
    async def compile(cls, field: Field):
        """编译"""
        kw = {"nullable": field.nullable,
              "comment": field.label,
              "doc": field.label
              }
        if field.default_ == "now":
            kw["default"] = datetime.now
            kw["server_default"] = func.now()
        if field.name == "update_date":
            kw["onupdate"] = func.now()
        column: Mapped[datetime] = mapped_column(cls.Column_Type, **kw)
        return column


class DynamicColumnBoolean(DynamicColumn):
    """布尔"""
    Column_Type = Boolean

    @classmethod
    async def compile(cls, field: Field):
        """编译"""
        kw = {"nullable": field.nullable,
              "comment": field.label,
              "doc": field.label
              }
        if field.default_:
            if field.default_ in ("1", "true", "True"):
                kw["default"] = True
            else:
                kw["default"] = False
        column: Mapped[bool] = mapped_column(cls.Column_Type, **kw)
        return column


class DynamicColumnJSON(DynamicColumn):
    """Json"""
    Column_Type = JSON

    @classmethod
    async def compile(cls, field: Field):
        """编译"""
        kw = {"nullable": field.nullable,
              "comment": field.label,
              "doc": field.label
              }
        if field.default_:
            try:
                kw["default"] = json.loads(field.default_)
            except:
                kw["default"] = {}

        column: Mapped[dict] = mapped_column(cls.Column_Type, **kw)
        return column


class DynamicColumnEnum(DynamicColumn):
    """Enum"""
    Column_Type = Enum

    @classmethod
    async def compile(cls, field: Field):
        """编译"""
        kw = {"default": field.default_,
              "nullable": field.nullable,
              "comment": field.label,
              "doc": field.label
              }
        column: Mapped[dict] = mapped_column(cls.Column_Type(*field.choices.split(",")), **kw)
        return column


# 类型和类映射关系
type_to_class = {
    FieldTypes.String: DynamicColumnString,
    FieldTypes.Text: DynamicColumnText,
    FieldTypes.Integer: DynamicColumnInteger,
    FieldTypes.DateTime: DynamicColumnDateTime,
    FieldTypes.Boolean: DynamicColumnBoolean,
    FieldTypes.JSON: DynamicColumnJSON,
    FieldTypes.Enum: DynamicColumnEnum,
}


async def get_dynamic_column(field: Field):
    """动态列"""
    class_ = type_to_class.get(field.field_type)
    if not class_:
        raise Exception(f"{field.field_type}列类型暂不支持")
    else:
        column = await class_.compile(field)
    return column
