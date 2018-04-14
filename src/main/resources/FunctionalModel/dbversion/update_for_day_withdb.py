import os
import sys
from multiprocessing import Pool
import numpy as np
import pickle
import MySQLdb


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'uploads')
status = open(os.path.join(UPLOADS_DIR, 'status.txt'), 'w')
status.write('wait')
print('wait')
status.close()
day_id = int(sys.argv[1])
startDay = int(sys.argv[2])
if day_id < startDay:
    table_name = 'sales_log'
else:
    table_name = 'predict_sales_log'
objects = np.load(os.path.join(BASE_DIR, 'objects.npy'))
pkl_file = open(os.path.join(BASE_DIR, 'idx.pkl'), 'rb')
idx = pickle.load(pkl_file)
judge = np.load(os.path.join(BASE_DIR, 'judge.npy'))

def update_day(agent_name):
    if judge[day_id-1][idx[agent_name]]:
        return
    db = MySQLdb.connect('localhost', 'root', 'wws85583813', 'cnPlane')
    cursor = db.cursor()
    sql = "SELECT SUM(cnt),SUM(round),COUNT(buy_nbr) \
        FROM %s WHERE day_id=%d AND sale_nbr='%s';" % (table_name, day_id, agent_name)
    cursor.execute(sql)
    san = cursor.fetchall()
    if san[0][2] == 0:
        san=[(0, 0, 0),]
    sql = "SELECT COUNT(sale_nbr) FROM %s WHERE day_id=%d AND buy_nbr='%s';"\
     % (table_name, day_id, agent_name)
    cursor.execute(sql)
    one = cursor.fetchall()
    sql = "UPDATE agents_details SET sum_cnt=%d,\
        sum_round=%d,indeg=%d,outdeg=%d \
        WHERE day_id=%d AND nbr='%s';" \
        % (san[0][0], san[0][1], one[0][0], san[0][2], day_id, agent_name)
    try:
        cursor.execute(sql)
        # print(sql)
        db.commit()
    except:
        print("fail updation")
        db.rollback()
    db.close()


db = MySQLdb.connect('localhost', 'root', 'wws85583813', 'cnPlane')
cursor = db.cursor()
cursor.execute("SELECT nbr FROM agents_details WHERE day_id=%d ORDER BY rank LIMIT 500;" % day_id)
objects = cursor.fetchall()
objects = np.array(objects)[:, 0]
pool = Pool(70)
pool.map(update_day, objects)
judge[day_id-1][:] = True
np.save(os.path.join(BASE_DIR, 'judge.npy'), judge)
status = open(os.path.join(UPLOADS_DIR, 'status.txt'), 'w')
status.write('go')
print('go')
status.close()
