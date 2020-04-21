# Copyright (c) 2020 HAICOR Project Team
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from knowledge.app import database


class Language(database.Model):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    code = Column(Text, unique=True, nullable=False)
    name = Column(Text, unique=True, nullable=False)


class PartOfSpeech(database.Model):
    __tablename__ = "part_of_speeches"

    id = Column(Integer, primary_key=True)
    code = Column(Text, unique=True, nullable=False)
    name = Column(Text, unique=True, nullable=False)


class Concept(database.Model):
    __tablename__ = "concepts"
    __table_args__ = (UniqueConstraint("lang", "text", "speech", "suffix"),)

    id = Column(Integer, primary_key=True)
    lang = Column(Integer, ForeignKey("languages.id"), nullable=False)
    text = Column(Text, nullable=False)
    speech = Column(Integer, ForeignKey("part_of_speeches.id"))
    suffix = Column(Text)

    language = relationship("Language")
    part_of_speech = relationship("PartOfSpeech")

    source_assertions = relationship("Assertion", back_populates="source",
                                     foreign_keys="Assertion.source_id")
    target_assertions = relationship("Assertion", back_populates="target",
                                     foreign_keys="Assertion.target_id")

    external_urls = relationship("ExternalURL", back_populates="source")

    def uri(self) -> str:
        """Generate ConceptNet URI."""

        return f"/c/{self.language.code}/{self.text}" \
            + (f"/{self.part_of_speech.code}" if self.speech else "") \
            + (f"/{self.suffix}" if self.suffix else "")
