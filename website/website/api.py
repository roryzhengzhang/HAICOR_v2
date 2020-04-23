# Copyright (c) 2020 HAICOR Project Team
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from __future__ import annotations

import datetime
import json
from typing import Optional

from flask import request
from requests import get

from website.app import KNOWLEDGE_API, app

SEARCH_LIMIT = 1000
REASON_LIMIT = 5


@app.route("/api/search/<string:text>", defaults={"speech": None})
@app.route("/api/search/<string:text>/<string:speech>")
def search(text: str, speech: Optional[str] = None):
    query = f"{KNOWLEDGE_API}/search/{text}"\
        + (f"/{speech}" if speech else "")\
        + f"/{SEARCH_LIMIT}"

    return get(query).text


@app.route("/api/concept/<int:id>")
def concept(id: int):
    query = f"{KNOWLEDGE_API}/concept/{id}"

    return get(query).text


@app.route("/api/reason/<int:source>/<int:middle>/<int:target>")
def reason(source: int, middle: int, target: int):
    query_1 = f"{KNOWLEDGE_API}/reason/{source}/{middle}"
    query_2 = f"{KNOWLEDGE_API}/reason/{middle}/{target}"

    left_path = get(query_1).json()
    right_path = get(query_2).json()

    if len(left_path["path"]) > REASON_LIMIT:
        left_path["path"] = []

    if len(right_path["path"]) > REASON_LIMIT:
        right_path["path"] = []

    return {"left": left_path, "right": right_path}


@app.route("/api/assertion/<int:source>/<int:target>")
def assertion(source: int, target: int):
    query = f"{KNOWLEDGE_API}/assertion/{source}/{target}"

    response = get(query)

    if response.json() is None:
        return get(f"{KNOWLEDGE_API}/assertion/{target}/{source}").text

    return response.text


@app.route("/api/submit", methods=["POST"])
def submit():
    data = json.loads(request.data)

    current = datetime.datetime.now()
    filename = f"{data['username']}-{data['question']}-{current}"

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

    return "success"
