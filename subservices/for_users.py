#!/usr/bin/python3

from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import render_template

import os


for_users = Blueprint("for_users", __name__, static_folder="static", template_folder="templates")


def android_get_latest(prefix="size-adviser-for-android_1.0.a", folder_name="static/android_bin"):
    return max([fn for fn in os.listdir(folder_name) if fn.startswith(prefix)])


@for_users.route("/download-app")
def user_download_app_page():
    return render_template("app-download-page.html", android_apk="static/android_bin/" + android_get_latest())


@for_users.route("/privacy-policy")
def show_privacy_policy():
    return render_template("gdpr_6jan.html")


@for_users.route("/data-deletion")
def data_deletion():
    return render_template("data_deletion.html")
