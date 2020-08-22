#!/usr/bin/python3

from db_computations import ComputationsDbSession
from db_personal import FittingSession

from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request

import re
import sqlite3
import urllib.request

mobile = Blueprint("mobile", __name__)


@mobile.route("/systems_of_size")
def _app_systems_of_size():
    return jsonify(
        ComputationsDbSession().systems_of_size(
            request.args["brand"], int(request.args["gender_int"]), request.args["standard"], request.args["size"]
        )
    )


@mobile.route("/range_of_system")
def _app_range_of_system():
    return jsonify(
        ComputationsDbSession().range_of_system(
            request.args["brand"], int(request.args["gender_int"]), request.args["system"]
        )
    )


@mobile.route("/recommended_size")
def _app_recommended_size():
    brand = request.args["brand"]
    gender_int = int(request.args["gender_int"])
    user_id = request.args["user_id"]
    s = ComputationsDbSession()
    # FIX IT !!!
    _recommended = ["UK", "4.5"]
    return jsonify(
        s.systems_of_size(brand, gender_int, *_recommended)
    )


@mobile.route("/try_with_size")
def _app_try_with_size():
    user_id = request.args["user_id"]
    fitting_id = request.args["fitting_id"]
    brand = request.args["brand"]
    size = request.args["size"]
    fit_value = request.args["fit_value"]
    s = FittingSession(user_id, fitting_id)
    s.try_with_size(brand, size, fit_value)
    return jsonify({
        "result": "success"
    })


@mobile.route("/my_collection")
def _app_my_collection():
    user_id = request.args["user_id"]
    s = FittingSession(user_id)
    ignore = int(request.args["ignore"])
    limit = None
    if request.args["limit"]:
        limit = int(request.args["limit"])
    media = "media" in request.args
    coll = s.get_user_collection(ignore, limit, media)
    # ...


@mobile.route("/upload_photo")
def _app_upload_photo():
    user_id = request.args.get("user_id", None)
    fitting_id = request.args.get("fitting_id", None)
    brand = request.args.get("brand", None)
    photo_url = request.args.get("url", None)
    s = FittingSession(user_id, fitting_id)

    if not user_id or not fitting_id or not brand or not photo_url:
        return abort(400)
    if not re.search(r"^https://res\.cloudinary\.com/size-adviser/.*", photo_url):
        return abort(400)

    extension = re.search(r".+\.(.+)", photo_url).group(1)
    photo_id = s.make_photo_id()
    urllib.request.urlretrieve(photo_url, "media/%s.%s" % (photo_id, extension))
    s.db_media_adding(photo_id + "." + extension)

    return jsonify({
        "result": "success"
    })


@mobile.route("/get_images/<brand>/<int:index>")
def _app_get_images(brand, index):
    db = sqlite3.connect("databases/personal.sqlite3")
    c = db.cursor()
    pids = c.execute("SELECT photo_id FROM brand_photos WHERE fitting_id IN "
                     "(SELECT fitting_id FROM fitting WHERE brand='{brand}')".format(brand=brand)).fetchall()
    db.close()
    try:
        image = pids[index][0]
    except IndexError:
        return abort(400)

    pid, extension = image.split(".")
    extension = extension.lower()
    if "jp" in extension:
        content_type = "image/jpeg"
    elif "png" in extension:
        content_type = "image/png"
    elif "bmp" in extension:
        content_type = "image/bmp"
    elif "svg" in extension:
        content_type = "image/svg+xml"
    else:
        return abort(400)

    with open("media/" + image, mode="rb") as img:
        image_binary = img.read()
    response = make_response(image_binary)
    response.headers.set("Content-Type", content_type)
    response.headers.set(
        "Content-Disposition", "attachment", filename="media/" + image)
    return response


'''
@app.route("/_app_download_photo")
def _app_download_photo():
    ...


@app.route("/_app_upload_photo")
def _app_upload_photo():
    ...


@app.route("/_app_ajax_brand_search")
def _app_ajax_brand_search():
    prefix = request.args["prefix"]
    ...
'''