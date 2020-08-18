#!/usr/bin/python3

import os
import random
from datetime import datetime
from shutil import copyfile

from flask import Flask
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory

from subservices.mobile_requests import mobile
from subservices.sysop_operations import sysop

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "files")
app.config["ALLOWED_EXTENSIONS"] = {".xlsx", ".xls", ".jpg", ".jpeg", ".png"}


app.register_blueprint(mobile, url_prefix="/mobile")
app.register_blueprint(sysop, url_prefix="/sysop")


@app.route("/error/<text>/<path:returnto>")
def throw_error(text, returnto):
    return render_template("error.html", text=text, returnto=returnto)


@app.route('/st/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


@app.route("/")
def welcome():
    return redirect("/error/Authorization needed/p")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
