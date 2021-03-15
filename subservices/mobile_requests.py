#!/usr/bin/python3

from db_computations import ComputationsDbSession
from db_personal import FittingSession

from flask import abort
from flask import Blueprint
from flask import flash
from flask import jsonify
from flask import make_response
from flask import request

from PIL import ExifTags
from PIL import ImageOps
from PIL import Image

from typing import Dict, List, Union

import datetime
import os
import re
import sqlite3
import urllib.request

from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
mobile = Blueprint("mobile", __name__, static_folder="static")


@mobile.route("/get_brand_data")
def _app_get_brand_data():
    """Used in SizeAdviserApi"""
    brand = request.args.get("brand")
    gender_int = int(request.args.get("gender_int", -1))
    if brand is None or gender_int == -1:
        return abort(400)
    standards = ComputationsDbSession().get_brand_data(brand, gender_int)
    return jsonify({
        "standards": [{"standard": k if k != "CM" else "Cm", "sizes": v} for (k, v) in standards.items()],
        "defaultStandard": get_default_standard(list(standards.keys()))
    })


def get_default_standard(list_standards):
    if "RU" in list_standards:
        return "RU"
    return list_standards[0]


@mobile.route("/get_brands")
def _app_get_brands():
    """Used in SizeAdviserApi"""
    gender_int = int(request.args.get("gender_int", -1))
    if gender_int == -1:
        return abort(400)
    return jsonify({
        "listBrands": ComputationsDbSession().get_all_brands(gender_int)
    })


@mobile.route("/random_brand")
def _app_random_brand():
    """Used in SizeAdviserApi"""
    """The value will be the first brand of lex-sorted table, not actually random"""
    gender_int = int(request.args.get("gender_int", -1))
    if gender_int == -1:
        return abort(400)
    return jsonify({
        "brand": ComputationsDbSession().get_all_brands(gender_int, "LIMIT 1")[0]
    })


def recommend_size(brand, gender_int, user_id, system=None):
    return ["US", "7"] # FIX IT!


@mobile.route("/recommended_size")
def _app_recommended_size():
    """Used in SizeAdviserApi"""
    brand = request.args.get("brand", None)
    gender_int = int(request.args.get("gender_int", -1))
    user_id = request.args.get("user_id", None)

    if not brand or gender_int == -1 or not user_id:
        return abort(400)

    s = ComputationsDbSession()

    try:
        # FIX IT !!!
        _recommended = recommend_size(brand, gender_int, user_id)
        return jsonify({
            "recommendations": [{"standard": k if k != "CM" else "Cm", "value": v}
             for (k,v) in s.systems_of_size(brand, gender_int, *_recommended).items()]
        })
    except TypeError:
        return abort(400)


@mobile.route("/data_for_gender")
def _app_data_for_gender():
    """Used in SizeAdviserApi"""
    gender_int = int(request.args.get("gender_int", -1))
    user_id = request.args.get("user_id", None)

    if gender_int == -1 or not user_id:
        return abort(400)

    s = ComputationsDbSession()
    f = FittingSession(user_id=user_id)

    brands = s.get_all_brands(gender_int)
    best_fits = f.get_user_best_fits()

    def _gson_conv(size_dict: Dict[str, str]) -> List[Dict[str, str]]:
        return [{"standard": k, "size": v} for (k, v) in size_dict.items()]

    recommended = {}
    for brand in brands:
        recommended[brand] = {
            "systemsOfSize": _gson_conv(s.systems_of_size(
                brand, gender_int, *recommend_size(brand, gender_int, user_id)
            )),
            "triedOn": False
        }

    for brand in best_fits:
        size_joint, fv = best_fits[brand]
        size, standard = size_joint.rsplit(' ', 1)
        systems_of_size: List[Dict[str, str]] = []

        try:
            systems_of_size = _gson_conv(s.systems_of_size(brand, gender_int, standard, size))
        except TypeError:
            systems_of_size = _gson_conv(f.wo_table_fitting(brand))

        recommended[brand] = {
            "systemsOfSize": systems_of_size,
            "triedOn": True
        }
    return jsonify({
        "data": [dict({"brand": brand}, **recommended[brand]) for brand in recommended]
    })


@mobile.route("/try_with_size")
def _app_try_with_size():
    """Used in SizeAdviserApi"""
    user_id = request.args.get("user_id", None)
    fitting_id = request.args.get("fitting_id", None)
    brand = request.args.get("brand", None)
    size = request.args.get("size", None)
    system = request.args.get("system", None)
    fit_value = request.args.get("fit_value", None)
    date = request.args.get("date", None)
    geo = request.args.get("geo", "")
    if not user_id or not fitting_id or not brand or not size or not system or not fit_value or not date:
        return abort(400)

    s = FittingSession(user_id, fitting_id)
    s.try_with_size(brand, " ".join([size, system]), fit_value, date, geo)
    return jsonify({
        "result": "success"
    })


@mobile.route("/get_collection_items")
def _app_get_collection_items():
    """Used in SizeAdviserApi"""
    user_id = request.args.get("user_id")

    if user_id is None:
        abort(400)

    s = FittingSession(user_id)
    coll: Dict[str, List[Union[str, None]]] = s.get_user_collection()
    result = []

    def support_older_records(date):
        if len(date.split(".")) == 3:
            return f"00.00.00.{date}"
        return date

    for brand_object in coll:
        for brand in brand_object:
            result.append({
                "brand": brand,
                "standard": brand_object[brand][0].rsplit(' ', 1)[1],
                "size": brand_object[brand][0].rsplit(' ', 1)[0],
                "fit_value": brand_object[brand][1],
                "fittingID": brand_object[brand][2],
                "date": support_older_records(brand_object[brand][3]),
                "has_photos": brand_object[brand][4] is not None
            })
    result = sorted(result, key=lambda x: datetime.datetime.strptime(x["date"], "%H.%M.%S.%d.%m.%Y"), reverse=True)
    result = map(lambda d: d["date"].split(".", 3)[1], result)

    return jsonify({
        "items": result
    })


@mobile.route("/remove_collection_item")
def _app_rm_collection_item():
    """Used in SizeAdviserApi"""
    user_id = request.args.get("user_id")
    fitting_id = request.args.get("fitting_id")
    s = FittingSession(user_id, fitting_id)
    if s.remove_fitting_data():
        s.stop()
        return jsonify(dict(removed=True))


@mobile.route("/remove_photo")
def _app_rm_photo():
    """Used in SizeAdviserApi"""
    user_id = request.args.get("user_id")
    fitting_id = request.args.get("fitting_id")
    photo_id = request.args.get("photo_id")
    s = FittingSession(user_id, fitting_id)
    if s.remove_photo(photo_id):
        s.stop()
        return jsonify(dict(removed=True))


@mobile.route("/remove_photo_by_index")
def _app_rm_photo_by_index():
    """Used in SizeAdviserApi"""
    user_id = request.args.get("user_id")
    fitting_id = request.args.get("fitting_id")
    photo_index = request.args.get("photo_index")
    s = FittingSession(user_id, fitting_id)
    if s.remove_photo_by_index(photo_index):
        s.stop()
        return jsonify(dict(removed=True))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@mobile.route("/<user_id>/<fitting_id>/<local_id>/upload_photo", methods=["GET", "POST"])
def _app_upload_photo(user_id, fitting_id, local_id):
    """Used in SizeAdviserApi"""
    s = FittingSession(user_id, fitting_id)
    fn = f"photo_{fitting_id}_{local_id}.png"
    if request.method == "POST":
        if "file" not in request.files:
            return abort(400)
        file = request.files["file"]
        if file.filename == "":
            return abort(400)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(os.path.split(mobile.root_path)[0], "../MEDIA", fn))
            thumb_path = fn.rstrip(".png") + "_thumb.png"
            image_loaded = Image.open(os.path.join(os.path.split(mobile.root_path)[0], "../MEDIA", fn))
            image = ImageOps.exif_transpose(image_loaded)
            image.thumbnail((240, 240), Image.ANTIALIAS)
            image.save(os.path.join(os.path.split(mobile.root_path)[0], "../MEDIA", thumb_path), 'PNG', quality=88)
            s.db_media_adding(local_id)
            return jsonify({
                "uploaded": True,
                "result": "success"
            })


def respond_placeholder_binary():
    with open("static/og_image_source.jpg", mode="rb") as img:
        image_binary = img.read()
    response = make_response(image_binary)
    response.headers.set("Content-Type", "image/jpeg")
    response.headers.set(
        "Content-Disposition", "attachment", filename="placeholder_.png")
    return response


@mobile.route("/get_images")
def _app_get_images():
    """Used in SizeAdviserApi"""
    brand = request.args.get("brand")
    index = int(request.args.get("index", 0))
    user_id = request.args.get("user_id")
    fitting_id = request.args.get("fitting_id")
    thumbnail = request.args.get("thumbnail", "no")

    db = sqlite3.connect("../DATABASES/personal.sqlite3")
    c = db.cursor()
    pids = c.execute(f"SELECT fitting_id, photo_id FROM brand_photos WHERE fitting_id='{fitting_id}'").fetchall()
    db.close()

    try:
        image_path = "photo_%s_%s.png" % (pids[index][0], pids[index][1])
    except IndexError:
        return abort(400)

    if thumbnail != "no":
        image_path = image_path.rstrip(".png") + "_thumb.png"

    with open("../MEDIA/" + image_path, mode="rb") as img:
        image_binary = img.read()
    response = make_response(image_binary)
    response.headers.set("Content-Type", "image/png")
    response.headers.set(
        "Content-Disposition", "attachment", filename="photo_%s_%d.png" % (brand, index))
    return response
