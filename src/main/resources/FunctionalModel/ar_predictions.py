#!/Users/wanghaogang/Applications/anaconda3/bin
# -*- coding: utf-8 -*-
import os
from statsmodels.tsa.ar_model import AR
import numpy as np
from mpmath import sqrt
import pandas as pd
import multiprocessing as mlp
from multiprocessing import Pool


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
startDay = open(os.path.join(os.path.dirname(BASE_DIR), 'uploads/startDay.txt'), 'r')
size = int(startDay.readline())
predict_length = int(startDay.readline())-size+1
size -= 1
startDay.close()
validate = np.load(os.path.join(BASE_DIR, 'validate.npy'))
cnts = np.load(os.path.join(BASE_DIR, 'cnts.npy'))
rounds = np.load(os.path.join(BASE_DIR, 'rounds.npy'))
length = len(validate)


# create a difference transform of the dataset
def difference(dataset):
    diff = list()
    for i in range(1, len(dataset)):
        value = dataset[i] - dataset[i - 1]
        diff.append(value)
    return np.array(diff)


# Make a prediction give regression coefficients and lag obs
def predict(coef, history):
    yhat = coef[0]
    for i in range(1, len(coef)):
        yhat += coef[i] * history[-i]
    return yhat


def evaluate_ar_model(X):
    # prepare training dataset
    X = X.astype('float64')
    train, test= X[0:size], X[size:]
    # train autoregression
    model = AR(X)
    model_fit = model.fit(maxlag=7, disp=False)
    window = model_fit.k_ar
    coef = model_fit.params
    # walk forward over time steps in test
    history = [i for i in train]
    predictions = list()
    for t in range(predict_length):
        yhat = predict(coef, history)
        predictions.append(yhat)
        if t < test.size:
            obs = test[t]
        else:
            obs = yhat
        history.append(obs)
    return predictions


def output_to_csv(new_cnts, new_sales):
    headers = ['day_id', 'sale_nbr', 'buy_nbr', 'cnt', 'round']
    f = open(os.path.join(os.path.dirname(BASE_DIR), 'uploads/predict_sales.csv'), 'w')
    f.write(','.join(headers) + '\n')
    for i in range(predict_length):
        new_cnt = new_cnts[:, i]
        new_sale = new_sales[:, i]
        for j in range(length):
            if new_cnt[j]+0.5 < 1.0 or new_sale[j]+0.5 < 1.0:
                continue
            record = (str(i+size+1), validate[j][0], validate[j][1],str(int(new_cnt[j]+0.5)), str(int(new_sale[j]+0.5)))
            f.write(','.join(record) + '\n')
    f.flush()
    f.close()


def ar_predict():
    pool = Pool(mlp.cpu_count()*4)
    new_cnts = pool.map(evaluate_ar_model, cnts)
    new_sales = pool.map(evaluate_ar_model, rounds)

    new_sales = np.array(new_sales)
    new_cnts = np.array(new_cnts)

    output_to_csv(new_cnts, new_sales)


def main():
    ar_predict()


if __name__ == '__main__':
    main()
