def get_top_entities(df1, group_cols, measure_col, n=10, largest=True):
    return (df1.groupby(group_cols)[measure_col]
            .sum()
            .reset_index()
            .sort_values(by=measure_col, ascending=not largest)
            .head(n))

def get_monthly_trend(df1):
    return df1.resample('MS', on='InvoiceDate')['Sales'].sum().reset_index()

