from pandas import Series
from matplotlib import pyplot
from keras.layers import Dense, LSTM
from keras.models import Sequential, load_model
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import os
from mpmath import sqrt
import time
import pandas as pd
from multiprocessing import Pool

np.random.seed(seed=int(time.time()))

def generate_dataset(dataset, look_back=1):
    while True:
        for i in range(len(dataset) - look_back):
            a = dataset[i:(i + look_back), :]
            b = dataset[i + look_back, :]
            a = np.array(a, ndmin=3).reshape(1, 1, look_back)
            yield(a, b)

def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return np.array(dataX), np.array(dataY)


def evaluate_ar_model(dataset):
    look_back = 8
    dataset = np.array(dataset, ndmin=2).reshape(91, 1).astype('float64')
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    train_size = 71
    train, test = dataset[0:train_size, :], dataset[train_size:len(dataset), :]
    trainX, trainY = create_dataset(train, look_back)
    # testX, testY = create_dataset(test, look_back)
    trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    # testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
    model = Sequential()
    model.add(LSTM(4, input_shape=(1, look_back), name='lstm'))
    model.add(Dense(1, name='output'))
    model.compile(loss='mae', optimizer='adam')
    model.save('my_model.h5')
    # model.fit_generator(generator=generate_dataset(train, look_back), epochs=50, verbose=1, steps_per_epoch=len(train) - look_back)
    model.fit(trainX, trainY, epochs=400, batch_size=2, verbose=1)
    # make predictions
    history = [i for i in dataset[(train_size-look_back):train_size, 0]]
    predictions = list()
    for i in range(20):
        prediction = model.predict(np.array([history]).reshape(1, 1, look_back))
        predictions.append(scaler.inverse_transform(prediction)[0][0])
        # predictions.append(prediction[0][0])
        history.append(prediction[0, 0])
        history = history[(len(history))-look_back:len(history)]
    print('Test Score: %.2f RMSE %.2f MAE' % (sqrt(mean_squared_error(test, predictions)), mean_absolute_error(test, predictions)))
    # trainPredict = model.predict(trainX)
    # testPredict = model.predict(testX)
    # # invert predictions
    # trainPredict = scaler.inverse_transform(trainPredict)
    # trainY = scaler.inverse_transform([trainY])
    # testPredict = scaler.inverse_transform(testPredict)
    # testY = scaler.inverse_transform([testY])
    # # calculate root mean squared error
    # trainScore = sqrt(mean_squared_error(trainY[0], trainPredict[:, 0]))
    # print(trainY[0])
    # print('Train Score: %.2f RMSE' % (trainScore))
    # testScore = sqrt(mean_squared_error(testY[0], testPredict[:, 0]))
    # print(testY[0])
    # print(testPredict[:, 0])
    # print('Test Score: %.2f RMSE' % (testScore))
    return predictions





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


train_size = 71
validate = np.load('validate.npy')
cnts = np.load('cnts.npy')
sales = np.load('sales.npy')
length = len(validate)
new_cnt = evaluate_ar_model(sales[1224])
print(new_cnt)
print(sales[1224])
# pool = Pool(40)
# new_cnts = pool.map(evaluate_ar_model, cnts)
# new_sales = pool.map(evaluate_ar_model, sales)

# new_sales = np.array(new_sales)
# new_cnts = np.array(new_cnts)

# output_to_csv()
