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
        "standards": standards,
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
        return jsonify(
            s.systems_of_size(brand, gender_int, *_recommended)
        )
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
    
    
    def _gson_conv(size_dict):
        return [{"standard": k, "size": v} for (k,v) in size_dict.items()]
    
    
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
        recommended[brand] = {
            "systemsOfSize": _gson_conv(s.systems_of_size(brand, gender_int, standard, size)),
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
    if not user_id or not fitting_id or not brand or not size or not system or not fit_value:
        return abort(400)

    s = FittingSession(user_id, fitting_id)
    s.try_with_size(brand, " ".join([size, system]), fit_value)
    return jsonify({
        "result": "success"
    })


def fit_value_to_str(fit_value):
    fit_value = int(fit_value)
    if fit_value == 1:
        return "1 SIZE DOWN"
    elif fit_value == 2:
        return "TOO SMALL"
    elif fit_value == 3:
        return "IDEAL"
    elif fit_value == 4:
        return "TOO BIG"
    elif fit_value == 5:
        return "1 SIZE UP"


@mobile.route("/get_collection_items")
def _app_get_collection_items():
    """Used in SizeAdviserApi"""
    user_id = request.args.get("user_id")
    
    if user_id is None:
        abort(400)
    
    s = FittingSession(user_id)
    coll = s.get_user_collection()
    
    return jsonify({
        "items": [
            dict(
                brand = brand,
                standard = coll[brand][0].rsplit(' ',1)[1],
                size = coll[brand][0].rsplit(' ',1)[0],
                fit_value = coll[brand][1]) for brand in coll
        ]
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
    if not re.search(r"^https?://res\.cloudinary\.com/size-adviser/.*", photo_url):
        return abort(400)

    extension = re.search(r".+\.(.+)", photo_url).group(1)
    photo_id = s.make_photo_id()
    urllib.request.urlretrieve(photo_url, "media/%s.%s" % (photo_id, extension))
    s.db_media_adding(photo_id + "." + extension)

    return jsonify({
        "result": "success"
    })


def respond_placeholder_binary():
    with open("static/70x70.png", mode="rb") as img:
        image_binary = img.read()
    response = make_response(image_binary)
    response.headers.set("Content-Type", "image/png")
    response.headers.set(
        "Content-Disposition", "attachment", filename="70x70.png")
    return response


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
        return respond_placeholder_binary()

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
        return respond_placeholder_binary()

    with open("media/" + image, mode="rb") as img:
        image_binary = img.read()
    response = make_response(image_binary)
    response.headers.set("Content-Type", content_type)
    response.headers.set(
        "Content-Disposition", "attachment", filename="media/" + image)
    return response


@mobile.route("/number_of_tries/<user_id>")
def _app_number_of_tries(user_id):
    s = FittingSession(user_id)
    n = s.number_of_tries()
    s.stop()
    return jsonify({"number": n})


@mobile.route("/brands_from/<user_id>/<int:gender_int>/<my_system>/", defaults={"prefix": ""})
@mobile.route("/brands_from/<user_id>/<int:gender_int>/<my_system>/<prefix>")
def _app_ajax_brand_search(user_id, gender_int, my_system, prefix):
    urls = [
        "https://size-adviser.com/static/not-tried-on.png",
        "https://size-adviser.com/static/tried-on.png"
    ]
    prefix = prefix.lower()
    all_brands = ["Adidas", "Asics", "Nike"]  # FIX IT!
    found = [b for b in all_brands if b.lower().startswith(prefix)]
    if not found:
        return jsonify({"hints": []})

    s = FittingSession(user_id)

    def choose_pic(brand_name, have_tried):
        return {
            "brand": brand_name,
            "have_tried": have_tried,
            "picURL": urls[have_tried]
        }

    res_brands = s.attribute_tried(found, choose_pic)

    s2 = ComputationsDbSession()

    for e, item in enumerate(res_brands):
        system, size = recommend_size(item["brand"], gender_int, user_id, my_system)
        if system != my_system and item["have_tried"]:
            try:
                size = s2.systems_of_size(item["brand"], gender_int, system, size)[my_system]
            except TypeError:
                del res_brands[e]
                continue
        del res_brands[e]["have_tried"]
        item["size"] = size

    return jsonify({
        "hints": res_brands
    })
