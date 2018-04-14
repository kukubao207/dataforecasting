# -*- coding:utf-8 -*-
import os
from multiprocessing import Pool
import pickle
import networkx as nx
import numpy as np
import MySQLdb


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
startDay = open(os.path.join(os.path.dirname(BASE_DIR), 'uploads/startDay.txt'), 'r')
train_size = int(startDay.readline())-1
length = int(startDay.readline())
startDay.close()
pkl_file = open(os.path.join(BASE_DIR, 'idx.pkl'), 'rb')
idx = pickle.load(pkl_file)


def work_for_pr(day_id):
    db = MySQLdb.connect("localhost", "root", "wws85583813", "cnPlane")
    cursor = db.cursor()
    if day_id <= train_size:
        sql = "SELECT sale_nbr, buy_nbr, round FROM sales_log WHERE day_id=%d;" % day_id
    else:
        sql = "SELECT sale_nbr, buy_nbr, round FROM predict_sales_log WHERE day_id=%d;" % day_id
    cursor.execute(sql)
    daily_data = cursor.fetchall()
    ng = nx.DiGraph()
    ng.add_weighted_edges_from(daily_data)
    npr = nx.pagerank(ng)
    npr = [ (k,v*len(idx)*10) for (k,v) in npr.items() if k.startswith('O') == True]
    rank = []
    rankData = sorted(npr, key = lambda x: x[1], reverse=True)
    judem = np.zeros((len(idx),), dtype=bool)
    for j in range(len(rankData)):
        rank.append((day_id, j+1, rankData[j][0], rankData[j][1]))
        judem[idx[rankData[j][0]]] = True
    j = len(rankData)
    for (k,v) in idx.items():
        if judem[v] == False:
            rank.append((day_id, j+1, k, 0.0))
            j += 1
    # if i <= train_size:
    #     tableName = 'sales_log'
    # else:
    #     tableName = 'predict_sales_log'
    # for j in range(len(rankData)):
    #     sql = "SELECT SUM(cnt),SUM(round),COUNT(buy_nbr) FROM %s WHERE day_id=%d AND sale_nbr='%s';" % (tableName, i, rankData[j][0])
    #     cursor.execute(sql)
    #     san = cursor.fetchall()
    #     if(san[0][2]==0):
    #         san=[(0,0,0),]
    #     sql = "SELECT COUNT(sale_nbr) FROM %s WHERE day_id=%d AND buy_nbr='%s';" % (tableName, i ,rankData[j][0])
    #     cursor.execute(sql)
    #     one = cursor.fetchall()
    #     rank.append((i, j+1, rankData[j][0], san[0][0], san[0][1], one[0][0], san[0][2], rankData[j][1]))
    # db.close()
    return rank


def out_to_csv_and_database(ranks):
    headers = ['day_id','rank','nbr','sum_cnt','sum_round','indeg','outdeg','pagerank_value']
    f = open(os.path.join(BASE_DIR, 'pr.csv'),'w')
    f.write(','.join(headers)+'\n')
    db = MySQLdb.connect('localhost','root','wws85583813','cnPlane')
    cursor = db.cursor()
    sql = "DROP TABLE IF EXISTS agents_details"
    try:
        cursor.execute(sql)
        sql = "CREATE TABLE `cnPlane`.`agents_details` (\
            `day_id` INT NOT NULL,\
            `rank` INT NOT NULL,\
            `nbr` VARCHAR(8) NOT NULL,\
            `sum_cnt` INT NULL,\
            `sum_round` INT(11) NULL,\
            `indeg` INT NULL,\
            `outdeg` INT NULL,\
            `pagerank_value` DECIMAL(20, 12) NOT NULL);"
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    for rank in ranks:
        for record in rank:
            f.write(','.join([str(record[0]), str(record[1]), record[2], '0', '0', '0', '0', \
            str(record[3])])+'\n')
    f.flush()
    sql = "LOAD DATA INFILE '%s' \
        INTO TABLE agents_details  \
        FIELDS TERMINATED BY ','  \
        lines terminated by '\n'  \
        ignore 1 lines;" % f.name
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    try:
        sql = """CREATE INDEX index_nbr ON agents_details(nbr);"""
        cursor.execute(sql)
        sql = """CREATE INDEX index_day ON agents_details(day_id);"""
        cursor.execute(sql)
        sql = """CREATE INDEX index_day_nbr ON agents_details(day_id,nbr);"""
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    db.close()
    f.close()


def pr():
    pool = Pool(70)
    ranks = pool.map(work_for_pr, range(1, length+1))
    out_to_csv_and_database(ranks)
    
def main():
    pr()

if __name__=='__main__':
    main()
