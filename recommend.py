#!/usr/bin/python3

from itertools import groupby, permutations
import sqlite3

personal = sqlite3.connect("../DATABASES/personal.sqlite3")
curs = personal.cursor()
computations = sqlite3.connect("../DATABASES/computations.sqlite3")
c_curs = computations.cursor()
fd = curs.execute("SELECT user_id, brand, size, fit_value FROM fitting").fetchall()

def bs_equiv():
    BS_Equiv = []
    for key, grouper in groupby(fd, key=lambda t: t[0]):
        f = {}
        dp = []
        for _tuple in grouper:
            _, B, S, F = _tuple
            if B in dp:
                continue
            if F not in f:
                f[F] = []
            f[F].append( (B, S) )
        for Fk, tuples in f.items():
            if len(tuples) >= 2:
                BS_Equiv.extend([rel for rel in permutations(tuples, 2)])
    return BS_Equiv

BS_Equiv = bs_equiv()

def user_base(user_id):
    for key, grouper in groupby(fd, key=lambda t: t[0]):
        if key == user_id:
            return [_tuple for _tuple in grouper]

def get_E(B_a):
    return list(filter(lambda rel: rel[0][0] == B_a, BS_Equiv))

def alg1(user_id, B_a):
    E = get_E(B_a)
    R_M1 = user_base(user_id)
    Srt = []
    for Rel in E:
        Bw_Ts = list(filter(lambda _tuple: _tuple[1] == Rel[1][0], R_M1))
        if not Bw_Ts:
            continue
        Bw_Tuple = min(Bw_Ts, key=lambda k: abs(3-k[3]))
        _, Bw, k, x = Bw_Tuple
        Srt.append( (abs(3-x), Rel[0]) )
    if not Srt:
        return None
    return min(Srt, key=lambda k: k[0])[1]

def any_to_US(brand, size_str):
    size, system = size_str.split(" ", 1)
    q = f"select json_extract(systems, '$.US') from from_sheets where brand='{brand}' and json_extract(systems, '$.{system}') = '{size}'"
    x = c_curs.execute(q).fetchone()
    if x is None:
        return None
    return c_curs.execute(q).fetchone()[0] + " " + "US"

def size_str_to_int(brand, size_str):
    return float(any_to_US(brand, size_str).split()[0])

def find_nearest_to(gender_int, conv_float):
    s = min([x[0] for x in c_curs.execute('select json_extract(systems, "$.US") from from_sheets where brand="Nike" and gender='+str(gender_int)).fetchall()], key=lambda s: abs(conv_float-float(s)))
    return s + " " + "US"

def alg2(user_id, gender_int, B_a):
    E = get_E(B_a)
    R_M1 = user_base(user_id)
    Srt = []
    for Rel in E:
        Ts = list(filter(lambda _tuple: _tuple[1] == Rel[1][0], R_M1))
        if not Ts:
            continue
        Bw_Tuple = min(Ts, key=lambda k: abs(3-k[3]))
        _, Bw, j, v = Bw_Tuple
        if 2 <= v <= 4:
            x = size_str_to_int(Rel[0][0], Rel[0][1])
            y = size_str_to_int(Rel[1][0], Rel[1][1])
        S_f = (x*y)/size_str_to_int(Bw, j)
        Srt.append( (abs(3-v), S_f) )
    if not Srt:
        return None
    return find_nearest_to(gender_int, min(Srt, key=lambda k: k[0])[1])



def terminate():
    global personal
    personal.close()