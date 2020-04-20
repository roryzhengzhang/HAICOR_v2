# Copyright (c) 2020 HAICOR Project Team
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from __future__ import annotations

import os

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

DATABASE_FILENAME = os.path.join(os.getenv("DATA_DIR"), "database.sqlite")

app: Flask = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DATABASE_FILENAME
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

api: Api = Api(app, prefix="api")
database: SQLAlchemy = SQLAlchemy(app)


@app.route("/")
def index():
    return "Hello"
