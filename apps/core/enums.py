# -*- coding: utf-8 -*-
from enum import Enum


class FieldTypes(Enum):
    """字段类型"""
    String = 'String'
    Text = 'Text'
    Numeric = 'Numeric'
    Integer = 'Integer'
    SmallInteger = 'SmallInteger'
    BigInteger = 'BigInteger'
    Float = 'Float'
    Double = 'Double'
    DateTime = 'DateTime'
    Date = 'Date'
    Time = 'Time'
    Enum = 'Enum'
    Boolean = 'Boolean'
    JSON = 'JSON'


class ForeignKeyStrategy(Enum):
    """外键删除更新策略"""
    CASCADE = 'CASCADE'
    DELETE = 'DELETE'
    RESTRICT = 'RESTRICT'


class Gender(Enum):
    """性别"""
    Male = 'Male'
    Female = 'Female'


class Action(Enum):
    """操作类型"""
    Create = "Create"
    Edit = "Edit"
    Query = "Query"
    Delete = "Delete"
