# Copyright (c) 2020 HAICOR Project Team
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from __future__ import annotations

from flask import render_template

from website.app import app


@app.route("/")
def reasoning():
    return render_template("reasoning.html")
