# Copyright (c) 2020 HAICOR Project Team
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from __future__ import annotations

from typing import Optional

from flask_restful import Resource
from sqlalchemy import func

from knowledge.app import api, database
from knowledge.models import concepts


def concept_to_dict(concept: concepts.Concept):
    return {"id": concept.id,
            "uri": concept.uri(),
            "lang": concept.language.code,
            "text": concept.text,
            "speech": concept.part_of_speech.code if concept.speech else None,
            "suffix": concept.suffix,
            "externals": tuple(i.target_id for i in concept.external_urls)}


class Search(Resource):
    def get(self, text: str,
            speech: Optional[str] = None, limit: Optional[int] = None):
        query = database.session\
            .query(concepts.Concept)\
            .filter(concepts.Concept.text.contains(text))

        if speech:
            query = query\
                .filter(concepts.Concept.part_of_speech.has(code=speech))

        query = query.order_by(func.length(concepts.Concept.text),
                               concepts.Concept.speech,
                               concepts.Concept.suffix)

        if limit:
            query = query.limit(limit)

        return {"concepts": tuple(concept_to_dict(i) for i in query.all())}


class Concept(Resource):
    def get(self, id: int):
        query = database.session\
            .query(concepts.Concept)\
            .filter(concepts.Concept.id == id)

        return concept_to_dict(query.one())


api.add_resource(Search,
                 "/search/<string:text>",
                 "/search/<string:text>/<int:limit>",
                 "/search/<string:text>/<string:speech>",
                 "/search/<string:text>/<string:speech>/<int:limit>")
api.add_resource(Concept, "/concept/<int:id>")
