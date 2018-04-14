import os
import MySQLdb
import numpy as np
from multiprocessing import Pool


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

train_size = 91


def filtrate_step(pair):
    db = MySQLdb.connect("localhost", "root", "wws85583813", """cnPlane""")
    cursor = db.cursor()
    sql = "SELECT day_id, cnt, round from sales_log where sale_nbr='%s' and buy_nbr='%s';" % (pair[0], pair[1])
    cursor.execute(sql)
    res = cursor.fetchall()
    times = len(res)
    # print(pair, times)
    if times <= 10:
        return {'times':times}
    cnt = []
    sale = []
    i = 0
    for j in range(train_size):
        if i < len(res) and j == res[i][0]:
            cnt.append(res[i][1])
            sale.append(res[i][2])
            i += 1
        else:
            cnt.append(0)
            sale.append(0)
    # for neron
    # cnt = np.array(cnt, ndmin=2)
    # cnt = cnt.reshape(len(cnt[0]), 1)
    # cnt = cnt.astype('float32')
    cnt = np.array(cnt)
    # sale = np.array(sale, ndmin=2)
    # sale = sale.reshape(len(sale[0]), 1)
    # sale = sale.astype('float32')
    sale = np.array(sale)
    return {'times':times, 'cnt':cnt, 'sale':sale}


def filtrate(sales_path, size):
    print("filtrate start")
    global train_size
    train_size = size
    db = MySQLdb.connect("localhost", "root", "wws85583813", """cnPlane""")
    cursor = db.cursor()
    sql = """SELECT DISTINCT sale_nbr,buy_nbr FROM sales_log;"""
    cursor.execute(sql)
    pairs = cursor.fetchall()
    db.close()
    validate = []
    cnts = []
    sales = []
    parts = np.array([0, 0, 0, 0, 0])
    pool = Pool(50)
    dicts = pool.map(filtrate_step, pairs)
    cnts = []
    sales = []
    i = 0
    for pair in dicts:
        i += 1
        times = pair['times']
        if times <= 10:
            parts[0] += 1
            continue
        elif times <= 20:
            parts[1] += 1
        elif times <= 30:
            parts[2] += 1
        elif times <= 40:
            parts[3] += 1
        else:
            parts[4] += 1
        cnts.append(pair['cnt'])
        sales.append(pair['sale'])
        validate.append(pairs[i-1])


    sales = np.array(sales)
    cnts = np.array(cnts)
    validate = np.array(validate)
    np.save(os.path.join(BASE_DIR, 'validate'), validate)
    np.save(os.path.join(BASE_DIR, 'cnts'), cnts)
    np.save(os.path.join(BASE_DIR, 'sales'), sales)
    sales_path = sales_path[:(sales_path.find('uploads')+8)]
    situations = open(sales_path+'situations.txt', 'a')
    situations.write(str(len(validate))+'\n')
    situations.write(str(len(pairs)-len(validate))+'\n')
    for part in parts:
        situations.write(str(part)+'\n')
    situations.close()
    print("filtrate end")
