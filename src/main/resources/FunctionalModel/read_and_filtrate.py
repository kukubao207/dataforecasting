#!/Users/wanghaogang/Applications/anaconda3/bin
# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pandas as pd
import pickle


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
UPLOADS_DIR = os.path.join(ROOT_DIR, 'uploads')
sales = pd.DataFrame()


def ins_process(sales_path):
    status = open(os.path.join(UPLOADS_DIR, 'status.txt'), 'w')
    status.write('wait')
    print('wait')
    status.close()
    print('ins start')
    global sales
    sales = pd.read_csv(filepath_or_buffer=sales_path, header=0)
    sales = sales[sales['round']!=0.0]
    sales = sales[sales['cnt']!=0]
    sales = sales[sales['sale_nbr']==sales['sale_nbr']]
    sales = sales[sales['buy_nbr']==sales['buy_nbr']]
    sales = sales[sales['round']==sales['round']]
    sales = sales[sales['cnt']==sales['cnt']]
    sales = sales[sales['day_id']==sales['day_id']]
    sales.to_hdf(os.path.join(ROOT_DIR, 'uploads/sales_log.h5'), 'df')
    print('ins end')
    print('filtrate begin')
    juds = set()
    objects = list()
    id_for_pairs = dict()
    idcnt = 0
    validate = list()
    opairs = list()
    ocnts = list()
    cnts = list()
    orounds = list()
    rounds = list()
    size = max(sales['day_id'])
    count_for_pair = list()
    parts = np.zeros((5,), dtype=int)
    limit = size/9
    # 遍历数据表格，为每个交易对设置标号，并产生了对应的时间序列
    for record in sales.values:
        if record[1] not in juds:
            objects.append(record[1])
            juds.add(record[1])
        if(record[2]) not in juds:
            objects.append(record[2])
            juds.add(record[2])
        if (record[1], record[2]) in id_for_pairs:
            idp = id_for_pairs[(record[1], record[2])]
        else:
            id_for_pairs[(record[1], record[2])] = idcnt
            idp = idcnt
            idcnt += 1
            count_for_pair.append(0)
            opairs.append((record[1], record[2]))
            ocnts.append(np.zeros((size,)))
            orounds.append(np.zeros((size,)))
        ocnts[idp][record[0]-1] = record[3]
        orounds[idp][record[0]-1] = record[4]
        count_for_pair[idp] += 1

    for pair in opairs:
        idp = id_for_pairs[pair]
        times = count_for_pair[idp]
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
        validate.append(pair)
        cnts.append(ocnts[idp])
        rounds.append(orounds[idp])


    rounds = np.array(rounds)
    cnts = np.array(cnts)
    validate = np.array(validate)
    np.save(os.path.join(BASE_DIR, 'validate'), validate)
    np.save(os.path.join(BASE_DIR, 'cnts'), cnts)
    np.save(os.path.join(BASE_DIR, 'rounds'), rounds)
    t = type(str())
    objects = np.array([i for i in objects if type(i) == t and i.startswith('O') == True])
    np.save(os.path.join(BASE_DIR, 'objects'), objects)
    idx = {objects[i]:i for i in range(len(objects))}
    output = open(os.path.join(BASE_DIR, 'idx.pkl'), 'wb')
    pickle.dump(idx, output)
    output.close()
    situations = open(os.path.join(ROOT_DIR, 'uploads/situations.txt'), 'w')
    situations.write(str(size)+'\n')
    situations.write(str(len(objects))+'\n')
    situations.write(str(len(validate))+'\n')
    situations.write(str(len(opairs)-len(validate))+'\n')
    for part in parts:
        situations.write(str(part)+'\n')
    situations.close()
    judge = np.zeros((size, len(objects)), dtype=bool)
    np.save(os.path.join(BASE_DIR,'judge.npy'), judge)
    print("filtrate end")
    status = open(os.path.join(UPLOADS_DIR, 'status.txt'), 'w')
    status.write('go')
    print('go')
    status.close()


def main():
    salespath = sys.argv[1]
    ins_process(salespath)

if __name__=='__main__':
    main()
