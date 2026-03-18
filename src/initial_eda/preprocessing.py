import pandas as pd

def clean_retail_data(df):
    df['Customer ID'] = df['Customer ID'].astype('Int64')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Sales'] = df['Quantity'] * df['Price']

    return df

def get_eda_dataframe(df):

    df1 = df[
        (df['Quantity'] >0) &
        (df['Price'] >= 1) &
        (df['Invoice'].astype(str).str.isnumeric())    
    ].copy()

    #plot 1
    # product_sales = (
    #     df1.groupby(['StockCode', 'Description'])['Quantity']
    #     .sum()
    #     .reset_index()
    # )
    # top_products = product_sales.sort_values(by='Quantity', ascending=False)

    # #plot 2
    
    # # top_cancelled_products = cancelled_products.groupby(['StockCode', 'Description'])['Quantity'].sum().reset_index()
    
    # # top10_cancelled_prod = top_cancelled_products.sort_values(by='Quantity', ascending = False).head(10)

    # #plot 3
    # top_customer = (df1.groupby(df1['Customer ID'])['Sales'].sum().reset_index()).sort_values(by='Sales', ascending = False).head(10)
    
    # #plot 4
    # total_revenue_by_product = df1.groupby(['StockCode','Description'])['Sales'].sum().reset_index().sort_values(by='Sales', ascending = False)
    # highest_revenue_products = total_revenue_by_product.head(10)

    # #plot 5
    # trend = df1.groupby(['InvoiceDate'])['Sales'].sum().reset_index()
    # trend_monthly = df1.resample('MS', on='InvoiceDate')['Sales'].sum().reset_index()

    return df1

def get_cancelled_invoices(df):
    cancelled_orders = df[df['Invoice'].astype(str).str.startswith('C')]
    cancelled_orders['Quantity'] = cancelled_orders['Quantity'].abs()

    return cancelled_orders





