#!/usr/bin/python3

import openpyexcel as pyxl
import sqlite3


def update_metatable(xlname):
    wb = pyxl.load_workbook(filename=xlname)
    ws = wb.active
    a_cells = [cell for cell in ws["A"][1:]]
    b_cells = [cell for cell in ws["B"][1:]]
    c_cells = [cell for cell in ws["C"][1:]]
    mt = sqlite3.connect("metatable.sqlite3")
    c = mt.cursor()
    c.execute("delete from sizes")
    for n, value in enumerate(a_cells):
        c.execute("insert into sizes values (?, ?, ?)", (a_cells[n].value, b_cells[n].value, c_cells[n].value))
    mt.commit()
    mt.close()


def build_table(filename):
    mt = sqlite3.connect("metatable.sqlite3")
    c = mt.cursor()
    data = c.execute("select brand,model,size from sizes").fetchall()
    wb = pyxl.Workbook()
    ws = wb.active
    ws["A1"] = "Бренд"
    ws["B1"] = "Модель"
    ws["C1"] = "Размер"
    for i in range(len(data)):
        x = i + 2
        ws["A%d" % x] = data[i][0]
        ws["B%d" % x] = data[i][1]
        ws["C%d" % x] = data[i][2]
    wb.save(filename=filename)
