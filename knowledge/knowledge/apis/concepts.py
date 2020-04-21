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


class Search(Resource):
    RESULTS = 1000

    def get(self, text: str, speech: Optional[str] = None):
        query = None

        if not speech:
            query = database.session \
                .query(concepts.Concept) \
                .filter(concepts.Concept.text.contains(text)) \
                .order_by(func.length(concepts.Concept.text),
                          concepts.Concept.speech,
                          concepts.Concept.suffix) \
                .limit(self.RESULTS)
        else:
            query = database.session \
                .query(concepts.Concept) \
                .filter(concepts.Concept.text.contains(text),
                        concepts.Concept.part_of_speech.has(code=speech)) \
                .order_by(func.length(concepts.Concept.text),
                          concepts.Concept.suffix) \
                .limit(self.RESULTS)

        return {"concepts": tuple(i.id for i in query.all())}


class Concept(Resource):
    def get(self, id: int):
        query = database.session \
            .query(concepts.Concept) \
            .filter(concepts.Concept.id == id)

        return self.concept_to_dict(query.one())

    @staticmethod
    def concept_to_dict(x: concepts.Concept):
        return {"id": x.id,
                "uri": x.uri(),
                "lang": x.language.code,
                "text": x.text,
                "speech": x.part_of_speech.code if x.speech else None,
                "suffix": x.suffix,
                "externals": tuple(i.target_id for i in x.external_urls)}


api.add_resource(Search,
                 "/search/<string:text>",
                 "/search/<string:text>/<string:speech>")
api.add_resource(Concept, "/concept/<int:id>")
