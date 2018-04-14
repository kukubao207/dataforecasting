import os
import sys
import MySQLdb
from multiprocessing import Pool
import numpy as np
import pickle


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'uploads')
status = open(os.path.join(UPLOADS_DIR, 'status.txt'), 'w')
status.write('wait')
print('wait')
status.close()
agent_name = sys.argv[1]
startDay = int(sys.argv[2])
endDay = int(sys.argv[3])
judge = np.load(os.path.join(BASE_DIR, 'judge.npy'))
pkl_file = open(os.path.join(BASE_DIR, 'idx.pkl'), 'rb')
idx = pickle.load(pkl_file)
aid = idx[agent_name]


def update_nbr(j):
    if judge[j-1][aid]:
        return
    judge[j-1][aid] = True
    db = MySQLdb.connect('localhost','root','wws85583813','cnPlane')
    cursor = db.cursor()
    if j < startDay:
        table_name = 'sales_log'
    else:
        table_name = 'predict_sales_log'
    sql = "SELECT SUM(cnt),SUM(round),COUNT(buy_nbr) \
        FROM %s WHERE day_id=%d AND sale_nbr='%s';" % (table_name, j, agent_name)
    cursor.execute(sql)
    san = cursor.fetchall()
    if san[0][2] == 0:
        san=[(0, 0, 0),]
    sql = "SELECT COUNT(sale_nbr) FROM %s WHERE day_id=%d AND buy_nbr='%s';"\
     % (table_name, j, agent_name)
    cursor.execute(sql)
    one = cursor.fetchall()
    sql = "UPDATE agents_details SET sum_cnt=%d,\
        sum_round=%d,indeg=%d,outdeg=%d \
        WHERE day_id=%d AND nbr='%s';" \
        % (san[0][0], san[0][1], one[0][0], san[0][2], j, agent_name)
    try:
        cursor.execute(sql)
        # print(sql)
        db.commit()
    except:
        print("fail updation")
        db.rollback()
    db.close()


pool = Pool(70)
pool.map(update_nbr, range(1, endDay+1))
np.save(os.path.join(BASE_DIR, 'judge.npy'), judge)
status = open(os.path.join(UPLOADS_DIR, 'status.txt'), 'w')
status.write('go')
print('go')
status.close()
