import pandas as pd
from pandas import Series
import numpy as np
from matplotlib import pyplot
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
from multiprocessing import Pool
from math import sqrt
import warnings

warnings.filterwarnings("ignore")


# evaluate an ARIMA model for a given order (p,d,q)
def evaluate_arima_model(X, arima_order, train_size, pair, tr_id, days):
    # prepare training dataset
    train, test = X[0:train_size], X[train_size:]
    history = [x for x in train]
    # make predictions
    differenced = difference(train, days)
    model = ARIMA(differenced, order=arima_order)
    model_fit = model.fit(disp=False)

    # one-step out of sample forecast
    forecast = model_fit.forecast(steps=len(test))[0]
    day = 1
    predictions = list()
    for yhat in forecast:
        inverted = inverse_difference(history, yhat, days)
        print('Day %d: %f;expected: %f' % (day, inverted, test[day - 1]))
        predictions.append(inverted)
        history.append(inverted)
        day += 1

    rmse = sqrt(mean_squared_error(test, predictions))
    mae = mean_absolute_error(test, predictions)
    print('%d %s %s: Test RMSE: %.3f MAE: %.3f' % (tr_id, pair[0], pair[1], rmse, mae))
    # calculate out of sample error
    return mae, predictions


def evaluate_models(dataset):
    dataset = dataset.astype('float32')
    best_score, best_cfg, best_predictions= float("inf"), None, None
    for days in dayset:
        for p in p_values:
            for d in d_values:
                for q in q_values:
                    order = (p, d, q)
                    border = (days, p, d, q)
                    try:
                        mae, predictions = evaluate_arima_model(dataset, order, 71, ('C1', 'O6186'), 1224, days)
                        if mae < best_score:
                            best_score, best_cfg, best_predictions = mae, border, predictions
                        print('ARIMA%s RMSE=%.3f' % (border, mae))
                    except:
                        continue
    print('Best ARIMA%s MAE=%.3f' % (best_cfg, best_score))
    return best_predictions


# create a differenced series
def difference(dataset, interval=1):
    diff = list()
    for i in range(interval, len(dataset)):
        value = dataset[i] - dataset[i - interval]
        diff.append(value)
    return np.array(diff)


# invert differenced value
def inverse_difference(history, yhat, interval=1):
    return yhat + history[-interval]

def output_to_csv():
    headers = ['day_id', 'sale_nbr', 'buy_nbr', 'cnt', 'round']
    f = open('/Users/wanghaogang/Desktop/predict_sales.csv', 'w')
    f.write(','.join(headers) + '\n')
    for i in range(20):
        new_cnt = new_cnts[:, i]
        new_sale = new_sales[:, i]
        for j in range(length):
            if new_cnt[j] <= 0 or new_sale[j] <= 0:
                continue
            record = (str(i+72), validate[j][0], validate[j][1],str(int(new_cnt[j]+0.5)), str(int(new_sale[j]+0.5)))
            f.write(','.join(record) + '\n')


size = 71
validate = np.load('validate.npy')
cnts = np.load('cnts.npy')
sales = np.load('sales.npy')
length = len(validate)

dayset = [1, 3, 6, 19]
p_values = [7, 9]
d_values = [0, 1]
q_values = [1, 4]
pool = Pool(3)
new_cnts = pool.map(evaluate_models, cnts)
new_sales = pool.map(evaluate_models, sales)
new_sales = np.array(new_sales)
new_cnts = np.array(new_cnts)
output_to_csv()

# rmse, predictions = evaluate_arima_model(X, (7, 0, 1), size, validate[tr_id], tr_id, 3)
# testPredictPlot = np.empty_like(np.array(test, ndmin=2).reshape(len(test), 1))
# testPredictPlot[:, :] = np.nan
# testPredictPlot[0:len(test), :] = np.array(predictions, ndmin=2).reshape(len(predictions), 1)
# pyplot.plot(test)
# pyplot.plot(testPredictPlot)
# pyplot.show()
