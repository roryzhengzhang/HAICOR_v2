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
    def get(self, source: int, middle: int, target: int):
        conceptnet = ConceptNet.get()

        path = conceptnet.get_shortest_paths(source, middle)[0]\
            + conceptnet.get_shortest_paths(middle, target)[0][1:]

        if len(path) == 0 or path[0] != source or path[-1] != target:
            return {"reachable": False, "path": path}
        else:
            return {"reachable": True, "path": path}


class Assertion(Resource):
    def get(self, source: int, target: int):
        query = database.session\
            .query(assertions.Assertion)\
            .filter_by(source_id=source, target_id=target)

        assertion = query.one()

        return {"source_id": assertion.source_id,
                "source_uri": assertion.source.uri(),
                "target_id": assertion.target_id,
                "target_uri": assertion.target.uri(),
                "relations": [{"id": i.id,
                               "relation": i.relation.relation,
                               "directed": i.relation.directed}
                              for i in query.all()]}


api.add_resource(Reason, "/reason/<int:source>/<int:middle>/<int:target>")
api.add_resource(Assertion, "/assertion/<int:source>/<int:target>")
