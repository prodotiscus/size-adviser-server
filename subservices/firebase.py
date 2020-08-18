#!/usr/bin/python3

from flask import Blueprint
from flask import render_template

firebase = Blueprint("firebase", __name__, template_folder="templates")


@firebase.route("/facebook_auth")
def facebook_auth():
    return render_template("firebase_auth.html")
