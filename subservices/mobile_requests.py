#!/usr/bin/python3

from db_computations import ComputationsDbSession
from db_personal import FittingSession

from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request

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
    brand = request.args["brand"]
    size = request.args["size"]
    fit_value = request.args["fit_value"]
    s = FittingSession(user_id)
    s.try_with_size(brand, size, fit_value)
    return jsonify({
        "result": "success",
        "fittingID": s.fitting_id
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
    brand = request.args.get("brand", None)
    photo_url = request.args.get("url", None)
    if not user_id or not brand or not photo_url:
        return abort(400)
    return photo_url


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