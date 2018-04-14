#!/Users/wanghaogang/Applications/anaconda3/bin
# -*- coding: utf-8 -*-  
import os
import sys
import multiprocessing as mlp
from multiprocessing import Pool
import numpy as np
import pickle
import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'uploads')
status = open(os.path.join(UPLOADS_DIR, 'status.txt'), 'w')
status.write('wait')
print('wait')
status.close()
sales_path = os.path.join(UPLOADS_DIR, 'sales_log.h5')
predict_path = os.path.join(UPLOADS_DIR, 'predict_sales.csv')
agents_details = pd.read_hdf(os.path.join(BASE_DIR, 'agents_detail.h5'), 'df')
agent_name = sys.argv[1]
nbr_data = agents_details[agents_details['nbr']==agent_name]
startDay = int(sys.argv[2])
endDay = int(sys.argv[3])
judge = np.load(os.path.join(BASE_DIR, 'judge.npy'))
pkl_file = open(os.path.join(BASE_DIR, 'idx.pkl'), 'rb')
idx = pickle.load(pkl_file)
aid = idx[agent_name]
predict_sales = pd.read_csv(filepath_or_buffer=predict_path, header=0)
osales = pd.read_hdf(sales_path, 'df')


def update_nbr(j):
    global judge
    record = nbr_data.values[j-1]
    if judge[j-1][aid]:
        record[4] = int(record[4])
        return ','.join([str(i) for i in record])
    judge[j-1][aid] = True
    if j < startDay:
        sales = osales
    else:
        sales = predict_sales
    daily_sales = sales[sales['day_id']==j]
    asales = daily_sales[daily_sales['sale_nbr']==agent_name]
    record[3] = sum(asales['cnt'].values)
    record[4] = int(sum(asales['round'].values))
    record[5] = len(daily_sales[daily_sales['buy_nbr']==agent_name])
    record[6] = len(asales)
    row = len(idx)*(j-1)+record[1]-1
    for i in range(3,7):
        agents_details.iat[row, i] = record[i]
    judge[j-1][aid] = True
    return ','.join([str(i) for i in record])

pool = Pool(mlp.cpu_count()*4)
content = pool.map(update_nbr, range(1, endDay+1))
np.save(os.path.join(BASE_DIR, 'judge.npy'), judge)
agents_details.to_hdf(os.path.join(BASE_DIR, 'agents_detail.h5'), 'df')
nbr_res = open(os.path.join(UPLOADS_DIR, 'nbr_res.txt'), 'w')
for row in content:
    nbr_res.write(row + '\n')
nbr_res.close()
status = open(os.path.join(UPLOADS_DIR, 'status.txt'), 'w')
status.write('go')
status.close()
print('go')
