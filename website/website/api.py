# Copyright (c) 2020 HAICOR Project Team
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from __future__ import annotations

from typing import Optional

from requests import get

from website.app import KNOWLEDGE_API, app

SEARCH_LIMIT = 1000


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
