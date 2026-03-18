import pandas as pd
from mlxtend.preprocessing import TransactionEncoder

def prepare_basket(df):
    """
    Transforms the cleaned sales data into a sparse Transaction Matrix.
    """
    # 1. Prepare the data (Using your logic)
    df_mba = df[['Invoice', 'Description']].dropna(subset=['Description'])
    df_mba.columns = ['Transaction', 'Item']
    df_mba['Item'] = df_mba['Item'].astype(str)

    # 2. Group into lists of items per transaction
    transactions = df_mba.groupby('Transaction')['Item'].apply(list).tolist()

    # 3. One-Hot Encoding (Using Sparse Matrix for memory efficiency)
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions, sparse=True)
    
    # 4. Create the basket DataFrame
    basket = pd.DataFrame.sparse.from_spmatrix(te_ary, columns=te.columns_)
    
    return basket