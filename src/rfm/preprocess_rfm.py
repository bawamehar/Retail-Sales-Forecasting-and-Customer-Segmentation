import pandas as pd
import numpy as np

def calculate_rfm_metrics(df1):
    rfm_m = df1.groupby('Customer ID')['Sales'].sum().reset_index()
    rfm_m.rename(columns={'Sales':'Monetary'}, inplace=True)

    rfm_f = df1.groupby('Customer ID')['Invoice'].nunique().reset_index()
    rfm_f.rename(columns={'Invoice':'Frequency'}, inplace=True)


    #snapshot_date = pd.Timestamp('2010-12-10')
    snapshot_date = (df1['InvoiceDate'].max() + pd.Timedelta(days=1)).normalize()

    rfm_r = df1.groupby('Customer ID')['InvoiceDate'].max().reset_index()
    rfm_r['Recency'] = (snapshot_date - rfm_r['InvoiceDate']).dt.days
    rfm_r = rfm_r[['Customer ID', 'Recency']]

    rfm = rfm_r.merge(rfm_f, on='Customer ID').merge(rfm_m, on='Customer ID')
    rfm['Recency_reversed'] = rfm['Recency'] * -1
    
    print(rfm.head())

    return rfm


def assign_rfm_scores(rfm):

    # R,f,M divided in 5 Bins
    rfm['R'] = pd.qcut(rfm['Recency_reversed'], 5, labels=[1,2,3,4,5])

    #rfm['F'] = pd.qcut(rfm['Frequency'], 5, labels=[1,2,3,4,5]).astype(int)
    #above line showed error because frequency is highly skewed and bins could not be divided with same boundaries 

    rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
    rfm['M'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5])

    # Concatenate RFM scores
    rfm['RFM'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)

    return rfm


def segment_customers(rfm):

    conditions = [
        (rfm['R'] >= 4) & (rfm['F'] >= 4),      # Champions
        (rfm['R'] >= 3) & (rfm['F'] >= 3),      # Loyal Customers
        (rfm['R'] >= 4),                        # Recent Customers
        (rfm['R'] <= 2) & (rfm['F'] >= 3)       # At Risk
    ]
    
    choices = [
        'Champions', 
        'Loyal Customers', 
        'Recent Customers', 
        'At Risk'
    ]
    
    rfm['Segment'] = np.select(conditions, choices, default='Others')
    
    return rfm
