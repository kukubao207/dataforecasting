#!/Users/wanghaogang/Applications/anaconda3/bin
# -*- coding: utf-8 -*-  
import os
import sys
import multiprocessing as mlp
from multiprocessing import Pool
import numpy as np
import pickle
import pandas as pd

day_id = int(sys.argv[1])
startDay = int(sys.argv[2])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'uploads')
sales_path = os.path.join(UPLOADS_DIR, 'sales_log.h5')
predict_path = os.path.join(UPLOADS_DIR, 'predict_sales.csv')
agents_details = pd.read_hdf(os.path.join(BASE_DIR, 'agents_detail.h5'), 'df')
daily_data = agents_details[agents_details['day_id']==day_id].head(500)
status = open(os.path.join(UPLOADS_DIR, 'status.txt'), 'w')
status.write('wait')
print('wait')
status.close()
if day_id >= startDay:
    sales = pd.read_csv(filepath_or_buffer=predict_path, header=0)
else:
    sales = pd.read_hdf(sales_path, 'df')

daily_sales = sales[sales['day_id']==day_id]
pkl_file = open(os.path.join(BASE_DIR, 'idx.pkl'), 'rb')
idx = pickle.load(pkl_file)
judge = np.load(os.path.join(BASE_DIR, 'judge.npy'))

def update_day(agent_rank):
    global judge
    record = daily_data.values[agent_rank-1]
    if judge[day_id-1][idx[record[2]]]:
        return ','.join([str(i) for i in record])
    asales = daily_sales[daily_sales['sale_nbr']==record[2]]
    record[3] = sum(asales['cnt'].values)
    record[4] = int(sum(asales['round'].values))
    record[5] = len(daily_sales[daily_sales['buy_nbr']==record[2]])
    record[6] = len(asales)
    row = len(idx)*(day_id-1)+agent_rank-1
    for i in range(3,7):
        agents_details.iat[row, i] = record[i]
    judge[day_id-1][idx[record[2]]] = True
    return ','.join([str(i) for i in record])
    



pool = Pool(mlp.cpu_count()*4)
content = pool.map(update_day, range(1, 501))
np.save(os.path.join(BASE_DIR, 'judge.npy'), judge)
daily_res = open(os.path.join(UPLOADS_DIR, 'daily_res.txt'), 'w')
for row in content:
    daily_res.write(row + '\n')
daily_res.close()
agents_details.to_hdf(os.path.join(BASE_DIR, 'agents_detail.h5'), 'df')
status = open(os.path.join(UPLOADS_DIR, 'status.txt'), 'w')
status.write('go')
print('go')
status.close()
