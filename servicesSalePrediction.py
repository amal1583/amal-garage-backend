import pandas as pd
from pandas import to_datetime
from pandas import DataFrame
from prophet import Prophet
from datetime import datetime


def previousServicesSale():
    path = 'services.csv'
    df = pd.read_csv(path, header=0)
    df.columns = ['ds', 'y']
    data = []
    for index, row in df.iterrows():
        data.append({
            "date": row['ds'],
            "sale": row['y']
        })
    return data


def futureServicesSale():
    path = 'services.csv'
    df = pd.read_csv(path, header=0)
    df.columns = ['ds', 'y']
    df['ds'] = to_datetime(df['ds'])

    model = Prophet()
    model.fit(df)

    future = list()

    for i in range(6, 13):
        date = '2022-%02d' % i
        future.append([date])

    future = DataFrame(future)
    future.columns = ['ds']
    future['ds'] = to_datetime(future['ds'])

    # use the model to make a forecast
    forecast = model.predict(future)

    data = []
    for index, row in forecast.iterrows():
        data.append({
            "date": row['ds'].strftime("%Y-%m-%d"),
            "sale": round(row['yhat'], 2)
        })
    return data