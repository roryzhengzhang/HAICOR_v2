# Copyright (c) 2020 HAICOR Project Team
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from __future__ import annotations

import os

import igraph
from flask_restful import Resource

from knowledge.app import DATA_DIRECTORY, api, database
from knowledge.models import assertions


class ConceptNet:
    conceptnet = None

    @classmethod
    def get(cls) -> igraph.Graph:
        if cls.conceptnet is None:
            cls.conceptnet = igraph.Graph.Read_Pickle(
                os.path.join(DATA_DIRECTORY, "directed-graph.pkl")
            )

        return cls.conceptnet


class Reason(Resource):
    def get(self, source: int, target: int):
        concept = ConceptNet.get()

        path = concept.get_shortest_paths(source, target)[0]

        return {"connected": len(path) != 0, "path": path}


class Assertion(Resource):
    def get(self, source: int, target: int):
        query = database.session\
            .query(assertions.Assertion)\
            .filter_by(source_id=source, target_id=target)

        assertion = query.all()

        if len(assertion) == 0:
            return

        return {"source_id": assertion[0].source_id,
                "target_id": assertion[0].target_id,
                "relations": [{"id": i.id,
                               "relation": i.relation.relation,
                               "directed": i.relation.directed}
                              for i in query.all()]}


api.add_resource(Reason, "/reason/<int:source>/<int:target>")
api.add_resource(Assertion, "/assertion/<int:source>/<int:target>")
