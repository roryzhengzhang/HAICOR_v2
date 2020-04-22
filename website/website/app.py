# Copyright (c) 2020 HAICOR Project Team
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from __future__ import annotations

from flask import Flask

# KNOWLEDGE_API = "http://knowledge:5000/api"
KNOWLEDGE_API = "http://192.168.1.100:5000/api"

app: Flask = Flask(__name__)
