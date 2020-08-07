#!/usr/bin/python3

import openpyexcel as pyxl
import os
import json

wb = pyxl.load_workbook(filename="test_data/" + os.listdir("test_data")[0])
all_rows = [row for row in wb.active.rows]
columns = [c.value for c in all_rows[0]]
if len(columns) < 3:
    raise ValueError
systems = {}
for e, m in enumerate(columns[2:]):
    systems[e + 2] = m
records = []
for row in all_rows[1:]:
    record = [row[0].value, 0 if row[1].value == "m" else 1, {}]
    for j, c in enumerate(row):
        if j < 2:
            continue
        if c.value:
            record[-1][systems[j]] = c.cached_value if c.cached_value else c.value
    record[-1] = json.dumps(record[-1])
    records.append(record)
print(records)