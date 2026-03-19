import pandas as pd
from mlxtend.preprocessing import TransactionEncoder

def prepare_basket(df):

    df_mba = df[['Invoice', 'Description']].dropna(subset=['Description'])
    df_mba.columns = ['Transaction', 'Item']
    df_mba['Item'] = df_mba['Item'].astype(str)

    transactions = df_mba.groupby('Transaction')['Item'].apply(list).tolist()

    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions, sparse=True)
    
    basket = pd.DataFrame.sparse.from_spmatrix(te_ary, columns=te.columns_)
    
    return basket