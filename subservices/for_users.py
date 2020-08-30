#!/usr/bin/python3

from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import render_template

import os


for_users = Blueprint("for_users", __name__, template_folder="templates")


def android_get_latest(prefix="size-adviser-for-android_1.0.a", folder_name="android_bin"):
    return max([fn for fn in os.listdir(folder_name) if fn.startswith(prefix)])


@for_users.route("/download-app")
def user_download_app_page():
    return render_template("app-download-page.html", android_apk=android_get_latest())
