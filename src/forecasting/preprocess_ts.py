import pandas as pd

def prepare_time_series_data(df):

    df_ts = df.copy()
    df_ts['InvoiceDate'] = pd.to_datetime(df_ts['InvoiceDate'])
    
    #Set index and resample to daily sum
    daily_sales = df_ts.set_index('InvoiceDate')['Sales'].resample('D').sum()
    print(daily_sales.head())  
    # fill missing dates with 0 (days with no sales)
    daily_sales = daily_sales.fillna(0)
    
    return daily_sales

def split_train_test(series, test_days=45):

    train = series[:-test_days]
    test = series[-test_days:]
    return train, test