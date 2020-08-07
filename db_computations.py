#!/usr/bin/python3

import openpyexcel as pyxl
import os
import json
import sqlite3


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
                    record[-1][systems[j]] = c.cached_value if c.cached_value else c.value
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

    def range_on_brand(self, brand, gender_int, standard, size):
        query = "SELECT system FROM from_sheets WHERE brand='%s' AND gender=%d " \
                "AND json_extract(system, '$.%s')='%s'" % (brand, gender_int, standard, size)

        return json.loads(self.c.execute(query).fetchone()[0])

    def stop(self):
        self.db.commit()
        self.db.close()

