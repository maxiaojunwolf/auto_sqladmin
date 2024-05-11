# -*- coding: utf-8 -*-
from sqlalchemy import UniqueConstraint, Index, ForeignKeyConstraint, select
from sqlalchemy.orm import joinedload

from apps.core.db import session_execute
from apps.core.models.constraint import Unique_Constraint, Index_Constraint, ForeignKey_Constraint
from apps.core.models.entity import Entity
from apps.core.models.field import Field


class DynamicConstraint:
    """动态约束"""

    @classmethod
    async def query(cls,entity_id:int):
        """查询"""
        raise NotImplementedError

    @classmethod
    async def compile(cls, entity):
        """编译"""
        raise NotImplementedError


class DynamicConstraintUnique(DynamicConstraint):
    """唯一约束"""

    @classmethod
    async def query(cls,entity_id:int):
        """查询"""
        stmt = select(Unique_Constraint).where(Unique_Constraint.entity_id==entity_id).options(joinedload(Unique_Constraint.fields))
        result = await session_execute(stmt)
        return result.unique().scalars()

    @classmethod
    async def compile(cls, entity: Entity) -> list[UniqueConstraint]:
        """唯一约束"""
        constraints = []
        unique_constraints = await cls.query(entity.id)
        for c in unique_constraints:
            if c.fields:
                constraints.append(UniqueConstraint(*[f.name for f in c.fields]))
        return constraints


class DynamicConstraintIndex(DynamicConstraint):
    """索引"""
    @classmethod
    async def query(cls,entity_id:int):
        """查询"""
        stmt = select(Index_Constraint).where(Index_Constraint.entity_id==entity_id).options(joinedload(Index_Constraint.fields))
        result = await session_execute(stmt)
        return result.unique().scalars()

    @classmethod
    async def compile(cls, entity):
        """索引约束"""
        constraints = []
        index_constraints = await cls.query(entity.id)
        for c in index_constraints:
            if c.fields:
                constraints.append(Index(None, *[f.name for f in c.fields]))
        return constraints


class DynamicConstraintForeignKey(DynamicConstraint):
    """外键"""

    @classmethod
    async def query(cls,entity_id:int):
        """查询"""
        stmt = select(ForeignKey_Constraint).where(ForeignKey_Constraint.entity_id==entity_id
                                                   ).options(joinedload(ForeignKey_Constraint.ref_field),
                                                             joinedload(ForeignKey_Constraint.refed_field).joinedload(Field.entity)
                                                             )
        result = await session_execute(stmt)
        return result.unique().scalars()

    @classmethod
    async def compile(cls, entity: Entity) -> list[ForeignKeyConstraint]:
        """外键约束"""
        constraints = []
        foreignkey_constraints = await cls.query(entity.id)
        for c in foreignkey_constraints:
            refed_table_name = c.refed_field.entity.table_name
            constraints.append(ForeignKeyConstraint(
                [c.ref_field.name],
                [f"{refed_table_name}.{c.refed_field.name}"],
                onupdate=c.on_update and c.on_update.value,
                ondelete=c.on_delete and c.on_delete.value
            ))
        return constraints
