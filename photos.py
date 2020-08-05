#!/usr/bin/python3

import random
import sqlite3


def new_photo_id(brand, model, extension):
    return "%s_%s_%d.%s" % (brand, model, random.randrange(10**6, (10**6)*2), extension)


def add_photo(brand, model, size, filepath, userid=None):
    mt = sqlite3.connect("metatable.sqlite3")
    c = mt.cursor()
    insertion = [brand, model, size, filepath, userid if userid else "*"]
    c.execute("insert into bm_files values (?,?,?,?,?)", insertion)
    mt.commit()
    mt.close()


def get_photos(brand, model, sizes=None, users=None):
    query = "select filepath from bm_files where brand='%s' and model='%s'" % (brand, model)
    if sizes:
        query += " " + "and size in (" + ",".join(["'%s'" % e for e in sizes]) + ")"
    if users:
        query += " " + "and userid in (" + ",".join(["'%s'" % e for e in users]) + ")"
    mt = sqlite3.connect("metatable.sqlite3")
    c = mt.cursor()
    results = [r[0] for r in c.execute(query).fetchall()]
    mt.close()
    return results


def get_photo(offset, *args, **kwargs):
    photos = get_photos(*args, **kwargs)
    if not photos:
        return {
            "bm_files_count": 0,
            "next_offset": 0,
            "load_path": None
        }
    else:
        return {
            "bm_files_count": len(photos),
            "next_offset": offset + 1,
            "load_path": photos[offset]
        }
