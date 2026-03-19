import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

def prepare_regression_features(series):

    df_reg = series.reset_index()
    df_reg.columns = ['InvoiceDate', 'TotalSales']

    df_reg['Day'] = (df_reg['InvoiceDate'] - df_reg['InvoiceDate'].min()).dt.days + 1

    df_reg['Weekday'] = df_reg['InvoiceDate'].dt.weekday + 1
    
    return df_reg

def train_linear_model(X_train, y_train):

    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

def get_regression_metrics(y_true, y_pred):

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return mae, rmse