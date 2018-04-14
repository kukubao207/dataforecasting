import os
import pickle
import numpy as np
import MySQLdb


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db = MySQLdb.connect("localhost", "root", "wws85583813", "cnPlane")
cursor = db.cursor()


def ins(sales_path):
    print("ins start")
    cursor.execute("DROP TABLE IF EXISTS sales_log")
    sql = """CREATE TABLE `cnPlane`.`sales_log` ( \
        `day_id` INT NOT NULL, \
        `sale_nbr` VARCHAR(8) NOT NULL, \
        `buy_nbr` VARCHAR(8) NOT NULL, \
        `cnt` INT NOT NULL, \
        `round` INT(11) NOT NULL);"""

    cursor.execute(sql)
    sql = "LOAD DATA INFILE '%s' \
        INTO TABLE sales_log  \
        FIELDS TERMINATED BY ','  \
        lines terminated by '\n'  \
        ignore 1 lines;" % sales_path

    # '/Users/wanghaogang/sales.csv'
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

    sql = """delete from sales_log where sale_nbr='' or buy_nbr='' or cnt=0 or round=0"""
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

def create_index():
    try:
        sql = """CREATE INDEX index_sale_buy ON sales_log(sale_nbr, buy_nbr);"""
        cursor.execute(sql)
        sql = """CREATE INDEX index_sale ON sales_log(sale_nbr);"""
        cursor.execute(sql)
        sql = """CREATE INDEX index_buy ON sales_log(buy_nbr);"""
        cursor.execute(sql)
        sql = """CREATE INDEX index_day ON sales_log(day_id);"""
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()


def prepare(sales_path):
    sql = """select distinct sale_nbr from sales_log union select distinct buy_nbr from sales_log;"""
    cursor.execute(sql)
    objects = cursor.fetchall()
    objects = [ob[0] for ob in objects if ob[0].startswith('O') == True ]
    objects = np.array(objects)
    idx = {objects[i]:i for i in range(len(objects))}
    np.save(os.path.join(BASE_DIR, 'objects'), objects)
    output = open(os.path.join(BASE_DIR, 'idx.pkl'), 'wb')
    pickle.dump(idx, output)
    output.close()
    sales_path = sales_path[:sales_path.find('uploads')+8]
    sql = """SELECT MAX(day_id) FROM sales_log"""
    cursor.execute(sql)
    size = cursor.fetchall()
    situations = open(sales_path+'situations.txt','w')
    situations.write(str(size[0][0])+'\n')
    situations.write(str(len(objects))+'\n')
    situations.close()
    judge = np.zeros((size[0][0], len(objects)), dtype=bool)
    np.save(os.path.join(BASE_DIR,'judge.npy'), judge)
    db.close()
    print("ins end")
    return size[0][0]


def ins_process(sales_path):
    ins(sales_path)
    create_index()
    size = prepare(sales_path)
    return size
    