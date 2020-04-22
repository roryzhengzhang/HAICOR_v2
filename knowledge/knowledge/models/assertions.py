# Copyright (c) 2020 HAICOR Project Team
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from __future__ import annotations

from sqlalchemy import (Boolean, Column, Float, ForeignKey, Integer, Text,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from knowledge.app import database


class Relation(database.Model):
    __tablename__ = "relations"

    id = Column(Integer, primary_key=True)
    relation = Column(Text, unique=True, nullable=False)
    directed = Column(Boolean, nullable=False)

    def uri(self) -> str:
        """Generate ConceptNet URI."""

        return f"/r/{self.relation}"


class Assertion(database.Model):
    __tablename__ = "assertions"
    __table_args__ = (
        UniqueConstraint("relation_id", "source_id", "target_id"),
    )

    id = Column(Integer, primary_key=True)
    relation_id = Column(Integer, ForeignKey("relations.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    weight = Column(Float, nullable=False)

    relation = relationship("Relation")
    source = relationship(
        "Concept",
        foreign_keys="Assertion.source_id",
        back_populates="source_assertions"
    )
    target = relationship(
        "Concept",
        foreign_keys="Assertion.target_id",
        back_populates="target_assertions"
    )

    def uri(self) -> str:
        """Generate ConceptNet URI."""

        return f"/a/[{self.relation.uri()}/,"\
            + f"{self.source.uri()}/,{self.target.uri()}/]"


class ExternalURL(database.Model):
    __tablename__ = "external_urls"
    __table_args__ = (UniqueConstraint("source_id", "target_id"),)

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    target_id = Column(Text, nullable=False)
    weight = Column(Float, nullable=False)

    source = relationship(
        "Concept",
        foreign_keys="ExternalURL.source_id",
        back_populates="external_urls"
    )

    def uri(self) -> str:
        """Generate ConceptNet URI."""

        return f"/a/[/r/ExternalURL/,"\
            + f"{self.source.uri()}/,/{self.target_id}/]"
