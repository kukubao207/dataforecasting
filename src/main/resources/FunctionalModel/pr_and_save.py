#!/Users/wanghaogang/Applications/anaconda3/bin
# -*- coding: utf-8 -*-
import os
import multiprocessing as mlp
from multiprocessing import Pool
import pickle
import networkx as nx
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sales = pd.DataFrame()
predict_sales = pd.DataFrame()
startDay = open(os.path.join(os.path.dirname(BASE_DIR), 'uploads/startDay.txt'), 'r')
train_size = int(startDay.readline())-1
length = int(startDay.readline())
startDay.close()
pkl_file = open(os.path.join(BASE_DIR, 'idx.pkl'), 'rb')
idx = pickle.load(pkl_file)


def work_for_pr(day_id):
    if day_id <= train_size:
        usales = sales[sales['day_id']==day_id]
    else:
        usales = predict_sales[predict_sales['day_id']==day_id]
    daily_data = usales[['sale_nbr','buy_nbr','round']]
    daily_data = [(d[0],d[1],d[2]) for d in daily_data.values]
    ng = nx.DiGraph()
    ng.add_weighted_edges_from(daily_data)
    npr = nx.pagerank(ng)
    npr = [ (k,v*len(idx)*10) for (k,v) in npr.items() if k.startswith('O') == True]
    rankData = sorted(npr, key = lambda x: x[1], reverse=True)
    judem = np.zeros((len(idx),), dtype=bool)
    rank = []
    # print("pr 1 end")
    for j in range(len(rankData)):
        nbr = rankData[j][0]
        rank.append((day_id, j+1, nbr, 0, 0, 0, 0, rankData[j][1]))
        # rank.append((day_id, j+1, nbr, sum(nsales['cnt']), sum(nsales['round']), \
        #     len(usales[usales['buy_nbr']==nbr]), len(nsales), rankData[j][1]))
        judem[idx[nbr]] = True
    j = len(rankData)
    # print("rank 1 end 2 start")
    for (k,v) in idx.items():
        if judem[v] == False:
            rank.append((day_id, j+1, k, 0, 0, 0, 0, 0.0))
            j += 1
    return rank


def out_to_csv(ranks):
    print("---ranks---")
    print(ranks)
    print("---ranks---")
    headers = ['day_id','rank','nbr','sum_cnt','sum_round','indeg','outdeg','pagerank_value']
    f = open(os.path.join(BASE_DIR, 'pr.csv'),'w')
    f.write(','.join(headers)+'\n')
    for rank in ranks:
        for record in rank:
            f.write(','.join([str(s) for s in record])+'\n')
    f.flush()
    agents_details = pd.read_csv(f.name, header=0)
    #print("---agents_details---")
    #print(agents_details)
    #print("---agents_details---")
    agents_details.to_hdf(os.path.join(BASE_DIR, 'agents_detail.h5'), 'df')
    f.close()

def pr():
    global sales
    global predict_sales
    sales_path = os.path.join(ROOT_DIR, 'uploads/sales_log.h5')
    sales = pd.read_hdf(sales_path, 'df')
    predict_path = os.path.join(os.path.dirname(sales_path), 'predict_sales.csv')
    predict_sales = pd.read_csv(filepath_or_buffer=predict_path, header=0)
    pool = Pool(mlp.cpu_count()*4)
    ranks = pool.map(work_for_pr, range(1, length+1))
    out_to_csv(ranks)

def main():
    pr()

if __name__=='__main__':
    main()
