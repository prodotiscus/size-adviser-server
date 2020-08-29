#!/usr/bin/python3

from random import randint
import sqlite3


class FittingSession:
    def __init__(self, user_id=None, fitting_id=None):
        self.user_id = user_id
        self.fitting_id = fitting_id
        if not user_id and not fitting_id:
            raise ValueError
        if user_id and not fitting_id:
            self.fitting_id = str(randint(10**(8-1), (10**8)-1))
        self.db = sqlite3.connect("databases/personal.sqlite3")
        self.c = self.db.cursor()

    @staticmethod
    def make_photo_id():
        return str(randint(10**(8-1), (10**8)-1))

    def fs_media_adding(self, binary, extension, folder="media"):
        _id = self.make_photo_id()
        self.db_media_adding("%s.%s" % (_id, extension))
        fl = open(folder + "/%s.%s" % (_id, extension), "wb")
        fl.write(binary)
        fl.close()

    def try_with_size(self, brand, size, fit_value):
        self.c.execute("INSERT INTO fitting VALUES (?,?,?,?,?)", (
            self.user_id, self.fitting_id, brand, size, fit_value
        ))
        self.db.commit()

    def get_user_collection(self, ignore=0, limit=None, media=False):
        if not self.user_id:
            raise ValueError
        quantity = (("LIMIT " + str(limit) + " ") if limit else "") + "OFFSET " + str(ignore)
        ftg = self.c.execute("SELECT fitting_id, brand, size, fit_value FROM fitting WHERE "
                             "user_id='%s' %s" % (self.user_id, quantity)).fetchall()
        response = {}
        for row in ftg:
            response[row[0]] = {
                "brand": row[1],
                "size": row[2],
                "fit_value": row[3],
                "media_binaries": None
            }
        if media:
            ids = [row[0] for row in ftg]
            query_ids = ",".join(["'%s'" % el for el in ids])
            links = self.c.execute("SELECT fitting_id, photo_id FROM brand_photos WHERE "
                                   "fitting_id in (%s)" % query_ids).fetchall()
            for row in links:
                fitting_id, photo_id = row
                if not response[fitting_id]["media_binaries"]:
                    response[fitting_id]["media_binaries"] = []
                response[fitting_id]["media_binaries"].append(open("media/" + photo_id, "rb").read())

        return response

    def attribute_tried(self, brand_list, attr_func):
        sql_list = ",".join(["'%s'" % b for b in brand_list])
        tried = [row[0] for row in self.c.execute("SELECT DISTINCT brand FROM fitting WHERE brand IN (%s) AND "
                       "user_id='%s'" % (sql_list, self.user_id))]
        return [attr_func(brand, brand in tried) for brand in brand_list]

    def db_media_adding(self, photo_id, extension=""):
        self.c.execute("INSERT INTO brand_photos VALUES (?,?)", (self.fitting_id, photo_id + extension))
        self.db.commit()

    def stop(self):
        self.db.close()


def save_user_props(user_id, gender):
    db = sqlite3.connect("databases/personal.sqlite3")
    c = db.cursor()
    c.execute("INSERT INTO user_props VALUES (?,?)", (user_id, gender))
    db.commit()
    db.close()
