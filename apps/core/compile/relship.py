# -*- coding: utf-8 -*-
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import relationship, Mapped, joinedload

from apps.core.db import session_execute
from apps.core.models.entity import Entity
from apps.core.models.relship import RelShip


class DynamicRelship:
    """动态关系"""

    @classmethod
    def get_lazy(cls, relship: RelShip):
        """生成lazy参数"""
        if relship.lazy == "False":
            value = False
        elif relship.lazy == "None":
            value = None
        else:
            value = relship.lazy
        return value

    @classmethod
    def get_secondary(cls, relship: RelShip):
        """生成secondary参数"""
        if relship.link_entity_id != relship.refed_entity_id:
            value = relship.link_entity.table_name
        else:
            value = None
        return value

    @classmethod
    def get_foreign_keys(cls, relship: RelShip):
        """生成foreign_keys参数"""
        if relship.foreign_keys:
            # todo 暂不支持多外键
            ref_entity = relship.ref_entity.name.capitalize()
            value = f"{ref_entity}.{relship.foreign_keys}"
        else:
            value = None
        return value

    @classmethod
    def get_order_by(cls, relship: RelShip):
        """生成order_by参数"""
        if relship.order_by:
            refed_entity = relship.refed_entity.name.capitalize()
            value = f"{refed_entity}.{relship.order_by}"
        else:
            value = None
        return value

    @classmethod
    def compile(cls, relship: RelShip):
        """编译"""
        raise NotImplementedError


class DynamicRelship_1to1(DynamicRelship):
    """一对一关系"""

    @classmethod
    async def compile(cls,relship: RelShip) -> relationship:
        """编译"""
        refed_entity = relship.refed_entity.name.capitalize()
        rel_ship: Mapped[refed_entity] = relationship(refed_entity,
                                                      uselist=False,
                                                      back_populates=relship.back_populates,
                                                      backref=relship.backref,
                                                      order_by=cls.get_order_by(relship),
                                                      foreign_keys=cls.get_foreign_keys(relship),
                                                      lazy=cls.get_lazy(relship),
                                                      doc=relship.label)
        return rel_ship


class DynamicRelship_1toN(DynamicRelship):
    """一对多关系"""

    @classmethod
    async def compile(cls, relship: RelShip) -> relationship:
        """编译"""
        refed_entity = relship.refed_entity.name.capitalize()
        rel_ship: Mapped[List[refed_entity]] = relationship(refed_entity,
                                                            uselist=True,
                                                            back_populates=relship.back_populates,
                                                            backref=relship.backref,
                                                            order_by=cls.get_order_by(relship),
                                                            foreign_keys=cls.get_foreign_keys(relship),
                                                            lazy=cls.get_lazy(relship),
                                                            doc=relship.label)
        return rel_ship


class DynamicRelship_NtoN(DynamicRelship):
    """多对多关系"""

    @classmethod
    async def compile(cls, relship: RelShip) -> relationship:
        """关系"""
        refed_entity = relship.refed_entity.name.capitalize()
        rel_ship: Mapped[List[refed_entity]] = relationship(refed_entity,
                                                            uselist=True,
                                                            secondary=cls.get_secondary(relship),
                                                            back_populates=relship.back_populates,
                                                            backref=relship.backref,
                                                            order_by=cls.get_order_by(relship),
                                                            foreign_keys=cls.get_foreign_keys(relship),
                                                            lazy=cls.get_lazy(relship),
                                                            doc=relship.label)
        return rel_ship


async def dynamic_relships(entity: Entity) -> dict:
    """加载关系对象"""
    relationships = {}
    stmt = select(RelShip).where(RelShip.ref_entity_id==entity.id).options(joinedload(RelShip.ref_entity),
                                                                           joinedload(RelShip.link_entity),
                                                                           joinedload(RelShip.refed_entity),
                                                                           )
    result = await session_execute(stmt)
    for r in result.unique().scalars():
        if r.link_entity_id != r.refed_entity_id:
            rel_ship = await DynamicRelship_NtoN.compile(r)
        else:
            if r.uselist:
                rel_ship = await DynamicRelship_1toN.compile(r)
            else:
                rel_ship = await DynamicRelship_1to1.compile(r)
        relationships[r.name] = rel_ship
    return relationships