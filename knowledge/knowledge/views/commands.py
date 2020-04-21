# Copyright (c) 2020 HAICOR Project Team
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from __future__ import annotations

import csv
import gzip
import json
import os
import re

import click
import igraph

from knowledge.app import CONFIG_DIRECTORY, DATA_DIRECTORY, app, database
from knowledge.models.assertions import Assertion, ExternalURL, Relation
from knowledge.models.concepts import Concept, Language, PartOfSpeech


@app.cli.command("init")
@click.argument("conceptnet", type=str)
def initialize(conceptnet: str):
    """Initialize database and necessary Python objects (as pickle)."""

    LIMIT = 10000
    REGEX = re.compile(r"^/c/(\w+)/([^/]+)(/\w)?(/.+)?/?$")

    CONCEPTNET = os.path.abspath(conceptnet)

    # foreign key lookup tables
    LANG = {}
    SPEECH = {}
    CONCEPT = {}
    RELATION = {}

    SPEECH[None] = None

    # reset current database
    database.drop_all()
    database.create_all()

    # process configuration files
    with open(os.path.join(CONFIG_DIRECTORY, "language.csv"), "r") as file:
        cache = []

        for idx, (code, name) in enumerate(csv.reader(file)):
            LANG[code] = idx + 1
            cache.append({"id": idx + 1, "code": code, "name": name})

        database.session.execute(Language.__table__.insert(), cache)

    with open(os.path.join(CONFIG_DIRECTORY, "part-of-speech.csv"), "r") as file:
        cache = []

        for idx, (code, name) in enumerate(csv.reader(file)):
            SPEECH[code] = idx + 1
            cache.append({"id": idx + 1, "code": code, "name": name})

        database.session.execute(PartOfSpeech.__table__.insert(), cache)

    with open(os.path.join(CONFIG_DIRECTORY, "relation.csv"), "r") as file:
        cache = []

        for idx, (relation, directed) in enumerate(csv.reader(file)):
            RELATION[relation] = idx + 1
            cache.append({"id": idx + 1, "relation": relation,
                          "directed": directed == "directed"})

        database.session.execute(Relation.__table__.insert(), cache)

    # process conceptnet file
    COUNTER = {"concept": 0, "assertion": 0, "external_url": 0}

    def get_concept(uri: str) -> int:
        if uri not in CONCEPT.keys():
            COUNTER["concept"] += 1
            CONCEPT[uri] = COUNTER["concept"]

            lang, text, speech, suffix = re.match(REGEX, uri).groups()

            speech = speech[1:] if speech else None
            suffix = suffix[1:] if suffix else None

            database.session.execute(Concept.__table__.insert(),
                                     {"id": CONCEPT[uri],
                                      "lang": LANG[lang],
                                      "text": text,
                                      "speech": SPEECH[speech],
                                      "suffix": suffix})

        return CONCEPT[uri]

    with gzip.open(CONCEPTNET, "rt") as conceptnet:
        cache = []
        reader = csv.reader(conceptnet, delimiter='\t')

        for idx, (_, relation, source, target, data) in enumerate(reader):
            print(f"Processed {idx + 1:,} lines ("
                  f"concept: {COUNTER['concept']:,}, "
                  f"assertion: {COUNTER['assertion']:,})", end='\r')

            relation = relation[3:]
            data = json.loads(data)

            if relation == "ExternalURL":
                continue  # process in second pass

            COUNTER["assertion"] += 1

            cache.append({"id": COUNTER["assertion"],
                          "relation_id": RELATION[relation],
                          "source_id": get_concept(source),
                          "target_id": get_concept(target),
                          "weight": data["weight"]})

            if len(cache) == LIMIT:
                database.session.execute(Assertion.__table__.insert(), cache)
                cache.clear()

        database.session.execute(Assertion.__table__.insert(), cache)

    with gzip.open(CONCEPTNET, "rt") as conceptnet:
        cache = []
        reader = csv.reader(conceptnet, delimiter='\t')

        for idx, (_, relation, source, target, data) in enumerate(reader):
            print(f"Processed {idx + 1:,} lines ("
                  f"concept: {COUNTER['concept']:,}, "
                  f"assertion: {COUNTER['assertion']:,}, "
                  f"external url: {COUNTER['external_url']:,})", end='\r')

            relation = relation[3:]
            data = json.loads(data)

            if relation != "ExternalURL" or source not in CONCEPT.keys():
                continue  # already processed in first pass

            COUNTER["external_url"] += 1

            cache.append({"id": COUNTER["external_url"],
                          "relation_id": RELATION[relation],
                          "source_id": get_concept(source),
                          "target_id": target,
                          "weight": data["weight"]})

            if len(cache) == LIMIT:
                database.session.execute(ExternalURL.__table__.insert(), cache)
                cache.clear()

        database.session.execute(ExternalURL.__table__.insert(), cache)

    print()
    database.session.commit()

    # generate minified knowledge graph
    print("Generating minified knowledge graph ...", end='\r')

    assertions = database.session \
        .query(Assertion.source_id, Assertion.target_id) \
        .union(
            database.session
            .query(Assertion.target_id, Assertion.source_id)
            .filter(Assertion.relation.has(directed=False))
        ) \
        .distinct()

    graph = igraph.Graph(edges=assertions.all(), directed=True)
    graph.write_pickle(os.path.join(DATA_DIRECTORY, "directed-graph.pkl"))

    print(f"Generated minified knowledge graph with {len(graph.es)} edges")
