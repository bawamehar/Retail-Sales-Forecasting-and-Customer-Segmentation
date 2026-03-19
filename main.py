import streamlit as st
import pandas as pd
from src.dataload import load_data
from src.initial_eda.preprocessing import clean_retail_data, get_eda_dataframe, get_cancelled_invoices
from src.initial_eda.analysis_utils import get_top_entities, get_monthly_trend
from src.plots_utils import plot_bar_chart, plot_time_series, plot_revenue_scatter, plot_rfm_distribution, plot_rfm_heatmap, plot_segment_share, plot_mba_scatter, plot_forecast_results
from src.rfm.preprocess_rfm import assign_rfm_scores, calculate_rfm_metrics, segment_customers
from src.association_rule_mining.preprocess_mba import prepare_basket
from src.association_rule_mining.model_apriori import generate_association_rules
from src.association_rule_mining.model_fpgrowth import run_fpgrowth_analysis
from src.forecasting.preprocess_ts import prepare_time_series_data, split_train_test
from src.forecasting.model_arima import train_auto_arima, get_forecast, calculate_metrics
from src.forecasting.model_linear import prepare_regression_features, train_linear_model, get_regression_metrics

def main():
    
    st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")
    st.title("Retail Analysis & Forecasting")

    #st.cache_data so it doesn't reload Excel file every time slider is changed
    @st.cache_data
    def run_pipeline():
        raw_df = load_data()
        clean_df = clean_retail_data(raw_df)
        return clean_df

    df = run_pipeline()
    df1 = get_eda_dataframe(df)

    #Sidebar
    st.sidebar.header("Dashboard Settings")
    top_n = st.sidebar.slider("Select Number of Top Items", min_value=5, max_value=30, value=10)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Sales Analysis", "Cancellations", "Customers & Quantity", "RFM Analysis", "Market Basket Analysis", "Time Series Forecasting"])

    with tab1:
        st.subheader(f"Revenue Generating Products")
        
        # Calling  analysis_utils
        top_revenue_df = get_top_entities(df1, ['Description', 'StockCode'], 'Sales', n=top_n)
        
        # Calling utils_plots
        fig_rev = plot_bar_chart(top_revenue_df, 'Description', 'Sales', f"Top {top_n} Products by Revenue")
        st.plotly_chart(fig_rev, use_container_width=True)
        st.divider()
        
        bottom_revenue_df = get_top_entities(df1, ['Description', 'StockCode'], 'Sales', n=top_n, largest=False)
        fig_rev_les = plot_bar_chart(bottom_revenue_df, 'Description', 'Sales', f"Bottom {top_n} Products by Revenue")
        st.plotly_chart(fig_rev_les, use_container_width=True)
        st.divider()

        st.subheader("Monthly Sales Trend")
        trend_df = get_monthly_trend(df1)
        fig_trend = plot_time_series(trend_df, 'InvoiceDate', 'Sales', "Revenue Trend Over Time")
        st.plotly_chart(fig_trend, use_container_width=True)

    with tab2:
        st.subheader("Loss Analysis: Cancelled Orders")
        df_cancelled = get_cancelled_invoices(df)
        
        top_cancel_df = get_top_entities(df_cancelled, ['Description', 'StockCode'], 'Quantity', n=top_n)
        
        fig_can = plot_bar_chart(top_cancel_df, 'Description', 'Quantity', "Most Cancelled Products", color_hex="#EF553B")
        st.plotly_chart(fig_can, use_container_width=True)
    
    with tab3:
        st.subheader(f"Top {top_n} most loyal Customers")
        top_customers = get_top_entities(df1, ['Customer ID'], 'Sales', n=top_n)
        fig_cus = plot_bar_chart(top_customers, 'Customer ID', 'Sales', "Top Buyers")
        st.plotly_chart(fig_cus, use_container_width=True)

        st.divider()

        st.subheader(f"Top {top_n} most sold products")
        top_products = get_top_entities(df1, ['StockCode', 'Description'], 'Quantity', n=top_n)
        fig_quan = plot_bar_chart(top_products, 'Description', 'Quantity', "Most Sold Products", color_hex="#00CC96")
        st.plotly_chart(fig_quan, use_container_width=True)

    with tab4:
        st.header("RFM Customer Segmentation")

        rfm_raw = calculate_rfm_metrics(df1)
        rfm_scored = assign_rfm_scores(rfm_raw)
        rfm_segments = segment_customers(rfm_scored)

        #plot 1
        rfm_counts = rfm_segments['RFM'].value_counts().reset_index()
        rfm_counts.columns = ['RFM', 'Count']
        top_rfm_scores = rfm_counts.sort_values(by='Count', ascending=False).head(top_n)

        #top_rfm_scores = rfm_segments['RFM'].value_counts().sort_values(ascending=False).head(top_n)
        fig_rfm_scores = plot_segment_share(top_rfm_scores, 'RFM', 'Count', f"Top {top_n} RFM Scores by Customer Count")
        st.plotly_chart(fig_rfm_scores, use_container_width=True)
        st.divider()

        #plot 2
        st.subheader("RFM Score Distribution")

        rfm_counts = rfm_segments['RFM'].value_counts().reset_index()
        rfm_counts.columns = ['RFM', 'Count']
        rfm_counts = rfm_counts.sort_values('RFM')
        fig1 = plot_rfm_distribution(rfm_counts, 'RFM', 'Count', "Customer Count by RFM Score")
        st.plotly_chart(fig1, use_container_width=True)
        st.divider()

        #plot 3, 4
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Customers per Segment (%)")

            seg_counts = rfm_segments['Segment'].value_counts().reset_index()
            seg_counts.columns = ['Segment', 'count']
            
            seg_counts['Percentage'] = (seg_counts['count'] / seg_counts['count'].sum()) * 100
            
            fig2 = plot_segment_share(seg_counts, 'Segment', 'Percentage', "Customer Share %")
            st.plotly_chart(fig2, use_container_width=True)

        with col2:
            st.subheader("Revenue per Segment (%)")
            
            seg_rev = rfm_segments.groupby('Segment')['Monetary'].sum().reset_index()
            seg_rev['Percentage'] = (seg_rev['Monetary'] / seg_rev['Monetary'].sum()) * 100
            
            seg_rev_desc = seg_rev.sort_values(by='Percentage', ascending=False)

            fig3 = plot_segment_share(seg_rev_desc, 'Segment', 'Percentage', "Revenue Share %", color_hex="#00CC96")
            st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        #plot 5
        st.subheader("Revenue Contribution vs Customer Share by Segments")
        scatter_df = rfm_segments.groupby('Segment').agg({
            'Customer ID': 'count',
            'Monetary': 'sum'
        }).reset_index()
        scatter_df['Cust_Share'] = (scatter_df['Customer ID'] / scatter_df['Customer ID'].sum()) * 100
        scatter_df['Rev_Share'] = (scatter_df['Monetary'] / scatter_df['Monetary'].sum()) * 100
        
        fig4 = plot_revenue_scatter(scatter_df, 'Cust_Share', 'Rev_Share', 'Monetary', 'Segment', "Revenue % vs Customer %")
        st.plotly_chart(fig4, use_container_width=True)
        st.divider()

        #plot 6
        st.subheader("Average Monetary Value by R and F")
        heatmap_data = rfm_segments.groupby(['R', 'F'])['Monetary'].mean().reset_index()
        fig5 = plot_rfm_heatmap(heatmap_data, 'F', 'R', 'Monetary', "Monetary Heatmap")
        st.plotly_chart(fig5, use_container_width=True)
        
    with tab5:
        st.header("Product Affinity Analysis (MBA)")
        st.markdown("---")

        col_s1, col_s2, col_s3 = st.columns([1, 1, 1])
        with col_s1:
            support_val = st.slider("Min Support", 0.01, 0.10, 0.02, step=0.01, help="The frequency with which the items appear together.")
        with col_s2:
            confidence_val = st.slider("Min Confidence", 0.1, 0.9, 0.5, step=0.1, help="The likelihood that an item B is purchased when item A is purchased.")
        with col_s3:
            algo_choice = st.radio("Select Algorithm", ["FP-Growth (Fast)", "Apriori"], horizontal=True)

        @st.cache_data
        def get_basket_data(_df):
            return prepare_basket(_df)

        basket = get_basket_data(df)


        with st.spinner(f"Running {algo_choice} algorithm..."):
            if "FP-Growth" in algo_choice:
        
                mba_rules = run_fpgrowth_analysis(
                    basket, 
                    min_support=support_val, 
                    min_confidence=confidence_val
                )
            else:

                mba_rules = generate_association_rules(
                    basket, 
                    min_support=support_val, 
                    min_confidence=confidence_val
                )

        if not mba_rules.empty:
            display_rules = mba_rules.copy()
            display_rules['antecedents'] = display_rules['antecedents'].apply(lambda x: ', '.join(list(x)))
            display_rules['consequents'] = display_rules['consequents'].apply(lambda x: ', '.join(list(x)))


            st.subheader(f"Top {top_n} Associations by Lift ({algo_choice})")
            st.dataframe(display_rules.head(top_n), use_container_width=True)

            st.markdown("---")
            
            # plot
            st.subheader("Rule Distribution: Support vs Confidence")
            fig_mba = plot_mba_scatter(mba_rules, title=f"Association Rules Impact ({algo_choice})")
            st.plotly_chart(fig_mba, use_container_width=True)
            
            st.info("**Tip:** Lift > 1 indicates a strong positive association. Hover over points to see specific product rules!")

        else:
            st.warning("No rules found with these thresholds. Try lowering the Support or Confidence values.")
    
    with tab6:
        st.header("Sales Forecasting Dashboard")
        
        # Preprocessing
        daily_sales = prepare_time_series_data(df1)
        train_s, test_s = split_train_test(daily_sales, test_days=45)
        
        model_type = st.radio("Select Forecasting Model", ["ARIMA (Auto-tuned)", "Linear Regression"], horizontal=True)

        if model_type == "ARIMA (Auto-tuned)":
            with st.spinner("Tuning ARIMA parameters..."):
                model = train_auto_arima(train_s)
                forecast = get_forecast(model, 45, test_s.index)
                mae, rmse = calculate_metrics(test_s, forecast)
                st.write(f"**Best Model Order:** {model.order}")

        else:
            # Linear Regression logic
            full_df = prepare_regression_features(daily_sales)
            train_reg = full_df.iloc[:-45]
            test_reg = full_df.iloc[-45:]
            
            X_train, y_train = train_reg[['Day', 'Weekday']], train_reg['TotalSales']
            X_test, y_test = test_reg[['Day', 'Weekday']], test_reg['TotalSales']
            
            lr_model = train_linear_model(X_train, y_train)
            forecast = pd.Series(lr_model.predict(X_test), index=test_s.index)
            mae, rmse = get_regression_metrics(y_test, forecast)

        # plot and metrics display
        m1, m2 = st.columns(2)
        m1.metric("Mean Absolute Error (MAE)", f"{mae:,.2f}")
        m2.metric("Root Mean Square Error (RMSE)", f"{rmse:,.2f}")
        
        fig_forecast = plot_forecast_results(train_s, test_s, forecast, title=f"{model_type} Performance")
        st.plotly_chart(fig_forecast, use_container_width=True)
    

if __name__ == "__main__":
    main()
