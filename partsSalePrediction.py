import pandas as pd
from pandas import to_datetime
from pandas import DataFrame
from prophet import Prophet
from datetime import datetime

def previousPartSale():
    path = 'parts_mock_v1.csv'
    df = pd.read_csv(path, header=0)
    df.columns = ['part','y', 'ds','vehicle']
    data = []
    for index, row in df.iterrows():
        data.append({
            "date": row['ds'],
            "sale": row['y']
        })
    return data


def futurePartSale():
    path = 'parts_mock_v1.csv'
    df = pd.read_csv(path, header=0)
    df.columns = ['part','y', 'ds','vehicle']
    #df.columns = ['ds', 'y']
    df['ds'] = to_datetime(df['ds'])

    model = Prophet()
    model.fit(df)

    future = list()

    '''for i in range(6, 13):
        date = '2022-%02d' % i
        future.append([date])

    future = DataFrame(future)
    '''
    future = model.make_future_dataframe(periods=6,freq='M',include_history=False)
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


# def futurePartSale():
#     path = 'parts.csv'
#     df = pd.read_csv(path, header=0)
#     df.columns = ['ds', 'y']
#     df['ds'] = to_datetime(df['ds'])
#
#     # set the uncertainty interval to 95% (the Prophet default is 80%)
#     my_model = Prophet(interval_width=0.95)
#
#     my_model.fit(df)
#
#     future_dates = my_model.make_future_dataframe(periods=6, freq='MS')
#     forecast = my_model.predict(future_dates)
#     # forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
#     data = []
#     for index, row in forecast.iterrows():
#         is_exist = False
#         for i, value in df.iterrows():
#             if value['ds'].strftime("%Y-%m-%d") == row['ds'].strftime("%Y-%m-%d"):
#                 is_exist = True
#                 break
#         if not is_exist:
#             data.append({
#                 "date": row['ds'].strftime("%Y-%m-%d"),
#                 "sale": round(row['yhat'], 2)
#             })
#     return data