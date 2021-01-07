#!/usr/bin/python3

import openpyexcel as pyxl
import os
import json
import sqlite3


def brand_of_file(filename, dirname="sheets/brands"):
    wb = pyxl.load_workbook(filename=os.path.join(dirname, filename))
    all_rows = [row for row in wb.active.rows]
    if len(all_rows) < 2:
        raise ValueError
    return all_rows[1][0].value


def sheet_records(dirname="sheets/brands", mgender=0):
    files = os.listdir(dirname)
    for flname in files:
        if "CATALOGUE" in flname or "~" in flname:
            continue
        wb = pyxl.load_workbook(filename=dirname + "/" + flname)
        all_rows = [row for row in wb.active.rows]
        columns = [c.value for c in all_rows[0]]
        if len(columns) < 3:
            raise ValueError
        systems = {}
        for e, m in enumerate(columns[2:]):
            systems[e + 2] = m
        for row in all_rows[1:]:
            record = [row[0].value, mgender if row[1].value == "m" else int(not mgender), {}]
            for j, c in enumerate(row):
                if j < 2:
                    continue
                if c.value:
                    record[-1][systems[j]] = c.cached_value if c.cached_value else str(c.value)
            record[-1] = json.dumps(record[-1])
            yield record


def db_load_sheets(dirname="sheets/brands", mgender=0):
    db = sqlite3.connect("databases/computations.sqlite3")
    c = db.cursor()
    c.execute("DELETE FROM from_sheets")
    for record in sheet_records(dirname, mgender):
        c.execute("INSERT INTO from_sheets VALUES (?, ?, ?)", record)
    db.commit()
    db.close()


class ComputationsDbSession:
    def __init__(self):
        self.db = sqlite3.connect("databases/computations.sqlite3")
        self.c = self.db.cursor()

    def get_brand_data(self, brand, gender_int):
        query = f"SELECT systems FROM from_sheets where brand='{brand}' AND gender={gender_int}"
        db_brand_data = self.c.execute(query).fetchall()
        data_dict = {}
        for row in db_brand_data:
            for (standard, value) in json.loads(row[0]).items():
                if standard not in data_dict:
                    data_dict[standard] = []
                data_dict[standard].append(value)
        for (standard, list_values) in data_dict.items():
            data_dict[standard] = sorted(data_dict[standard], key=lambda s: eval(s.replace(" 1/", "+1/")))
        return data_dict

    def systems_of_size(self, brand, gender_int, standard, size):
        query = "SELECT systems FROM from_sheets WHERE brand='%s' AND gender=%d " \
                "AND json_extract(systems, '$.%s')='%s'" % (brand, gender_int, standard, size)

        return json.loads(self.c.execute(query).fetchone()[0])

    def range_of_system(self, brand, gender_int, system):
        query = "SELECT json_extract(systems, '$.%s') FROM from_sheets WHERE brand='%s' " \
                "AND gender=%d" % (system, brand, gender_int)

        res = dict(data=["<"] + [s[0] for s in self.c.execute(query).fetchall()] + [">"])
        res["system"] = system
        if len(res) >= 2:
            res["minimal"] = res["data"][0]
            res["maximal"] = res["data"][-1]
        else:
            res["minimal"] = None
            res["maximal"] = None

        return res

    def stop(self):
        self.db.commit()
        self.db.close()

