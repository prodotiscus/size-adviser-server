#!/usr/bin/python3

import os

from flask import Flask, redirect, render_template, Response, send_from_directory

from subservices.firebase import firebase
from subservices.for_users import for_users
from subservices.mobile_requests import mobile
from subservices.sysop_operations import sysop

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "files")
app.config["ALLOWED_EXTENSIONS"] = {".xlsx", ".xls", ".jpg", ".jpeg", ".png"}


app.register_blueprint(firebase, url_prefix="/firebase")
app.register_blueprint(for_users, url_prefix="/for-users")
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
    return redirect("/error/Authorization needed/sysop/p")


@app.route("/robots.txt")
def disallow_robots():
    return Response("User-agent: *\nDisallow: /\n", mimetype="text/plain")


@app.route("/report")
def report_bugs():
    GFORM_SHORTURL = "https://forms.gle/B5qzTSWFkAAg3PqE7"
    return redirect(GFORM_SHORTURL)


@app.route("/tasks")
def trello_board():
    TRELLO_SHORTURL = "https://trello.com/b/ACy6aF4G/%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%B2%D1%8B%D0%B5-%D0%B7%D0%B0%D0%B4%D0%B0%D1%87%D0%B8"
    return redirect(TRELLO_SHORTURL)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
