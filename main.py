import streamlit as st
from src.dataload import load_data
from src.initial_eda.preprocessing import clean_retail_data, get_eda_dataframe, get_cancelled_invoices
from src.initial_eda.analysis_utils import get_top_entities, get_monthly_trend
from src.plots_utils import plot_bar_chart, plot_time_series, plot_revenue_scatter, plot_rfm_distribution, plot_rfm_heatmap, plot_segment_share
from src.rfm.preprocess_rfm import assign_rfm_scores, calculate_rfm_metrics, segment_customers

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

    tab1, tab2, tab3, tab4 = st.tabs(["Sales Analysis", "Cancellations", "Customers & Quantity", "RFM Analysis"])

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


if __name__ == "__main__":
    main()
