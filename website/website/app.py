# Copyright (c) 2020 HAICOR Project Team
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from __future__ import annotations

from flask import Flask

KNOWLEDGE_API = "http://knowledge:5000"
KNOWLEDGE_API = "http://localhost:4000"

app: Flask = Flask(__name__)
