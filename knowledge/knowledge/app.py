# Copyright (c) 2020 HAICOR Project Team
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from __future__ import annotations

import os

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

DATA_DIRECTORY = os.path.abspath(os.getenv("DATA_DIRECTORY"))
CONFIG_DIRECTORY = os.path.abspath(os.getenv("CONFIG_DIRECTORY"))

app: Flask = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = \
    f"sqlite:///{os.path.join(DATA_DIRECTORY, 'database.sqlite')}"

api: Api = Api(app, prefix="api")
database: SQLAlchemy = SQLAlchemy(app)
