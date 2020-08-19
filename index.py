#!/usr/bin/python3

import os

from flask import Flask, redirect, render_template, Response, send_from_directory

from subservices.firebase import firebase
from subservices.mobile_requests import mobile
from subservices.sysop_operations import sysop

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "files")
app.config["ALLOWED_EXTENSIONS"] = {".xlsx", ".xls", ".jpg", ".jpeg", ".png"}


app.register_blueprint(firebase, url_prefix="/firebase")
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


@app.route("/robots.txt")
def disallow_robots():
    return Response("User-agent: *\nDisallow: /\n", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
