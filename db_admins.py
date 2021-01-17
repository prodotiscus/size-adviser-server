#!/usr/bin/python3

import random
import sqlite3


class AdminDatabase:
    def __init__(self):
        self.db = sqlite3.connect("../DATABASES/admins.sqlite3")
        self.c = self.db.cursor()

    def check_token(self, username, token):
        res = self.c.execute("SELECT username, token FROM admins WHERE username='%s'" % username).fetchall()
        if not res:
            return False
        return res[0][1] == token

    def get_token(self, username, password):
        res = self.c.execute("SELECT username, password FROM admins WHERE username='%s'" % username).fetchall()
        if not res or res[0][1] != password:
            return "notoken"
        else:
            token = "t" + str(random.randrange(100000, 999999))
            self.c.execute("UPDATE admins SET token='%s' WHERE username='%s'" % (token, username))
            return token

    def exit(self):
        self.db.commit()
        self.db.close()
