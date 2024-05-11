# -*- coding: utf-8 -*-
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from apps.core.compile.column import get_dynamic_column
from apps.core.compile.constraint import DynamicConstraintUnique, DynamicConstraintIndex, DynamicConstraintForeignKey
from apps.core.compile.relship import DynamicRelship_NtoN, DynamicRelship_1toN, DynamicRelship_1to1, dynamic_relships
from apps.core.db import session_factory, DynamicBase, session_execute
from apps.core.models.constraint import Unique_Constraint, Index_Constraint, ForeignKey_Constraint
from apps.core.models.entity import Entity
from apps.core.models.field import Field
from apps.core.models.relship import RelShip


class LoadORM:
    """加载ORM"""

    @classmethod
    async def reset_dynamicbase(cls):
        """重置Base:由于register.mappers为弱引用，需要单独保存下生产的orm，避免被自动回收"""
        DynamicBase.metadata.clear()
        DynamicBase.registry.dispose(cascade=True)
        DynamicBase._orms = dict()

    @classmethod
    async def load_columns(cls, entity: Entity) -> dict:
        """生成列属性"""
        columns = {}
        stmt = select(Field).where(Field.entity_id==entity.id)
        result = await session_execute(stmt)
        for field in result.scalars():
            column = await get_dynamic_column(field)
            columns[field.name] = column
        return columns

    @classmethod
    async def load_constraints(cls, entity: Entity) -> list:
        """生成约束"""
        unique_constraints = await DynamicConstraintUnique.compile(entity)
        index_constraints = await DynamicConstraintIndex.compile(entity)
        foreignkey_constraints = await DynamicConstraintForeignKey.compile(entity)
        return unique_constraints + index_constraints + foreignkey_constraints

    @classmethod
    async def load_relships(cls, entity: Entity) -> dict:
        """加载关系对象"""
        return await dynamic_relships(entity)

    @classmethod
    def load_str_func(cls, orm):
        """设置__str__方法"""
        if getattr(orm, "name", None):
            orm.__str__ = lambda i: i.name
        elif getattr(orm, "id", None):
            orm.__str__ = lambda i: str(i.id)
        else:
            pass

    @classmethod
    async def _load(cls, entity):
        """动态生成orm"""
        # 动态生成列
        columns = await cls.load_columns(entity)
        # 动态生成约束
        constraints = await cls.load_constraints(entity)
        # 动态生成关系
        relships = await cls.load_relships(entity)
        kw = {"__tablename__": entity.table_name,
              "__table_args__": (*constraints,
                                 {"extend_existing": True}),
              "__is_dynamic__": True,
              # 保存动态类基本信息
              "__entity__": {"id": entity.id, "name": entity.name},
              **columns,
              **relships
              }
        orm = type(entity.name.capitalize(), (DynamicBase,), kw)
        cls.load_str_func(orm)
        return orm

    @classmethod
    async def load(cls):
        """动态生成ORM"""
        print("-----加载动态ORM-开始------")
        await cls.reset_dynamicbase()
        async with session_factory() as session:
            # 类必须包含主键列
            stmt = select(Entity).join(Field).where(Field.primary_key==True)
            result = await session.execute(stmt)
            for obj in result.unique().scalars():
                try:
                    DynamicBase._orms[obj.name] = await cls._load(obj)
                except:
                    print(f"-----加载{obj.name}-异常------")
        print("-----加载动态ORM-完成------")
