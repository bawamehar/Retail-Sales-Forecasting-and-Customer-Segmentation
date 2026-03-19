import pmdarima as pm
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import pandas as pd

def train_auto_arima(train_data):

    model = pm.auto_arima(
        train_data,
        start_p=0, start_q=0,
        max_p=10, max_q=10,
        seasonal=False,
        error_action='ignore',
        suppress_warnings=True,
        stepwise=True
    )
    return model

def get_forecast(model, steps, index):

    forecast_values = model.predict(n_periods=steps)
    return pd.Series(forecast_values, index=index)

def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    return mae, rmse