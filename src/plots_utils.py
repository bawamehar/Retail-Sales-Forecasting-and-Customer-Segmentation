import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def plot_bar_chart(df, x_col, y_col, title, color_hex="#636EFA"):

    plot_df = df.copy()
    
    plot_df[x_col] = plot_df[x_col].astype(str)
    
    fig = px.bar(
        plot_df, 
        x=x_col, 
        y=y_col, 
        title=title,
        template="plotly_white",
        text_auto='.2s'
    )
    
    fig.update_traces(marker_color=color_hex)

    fig.update_layout(
        xaxis_title=x_col, 
        yaxis_title=y_col,
        xaxis={'type':'category'}
    )
    return fig


def plot_time_series(df, x_col, y_col, title):
    fig = px.line(
        df, 
        x=x_col, 
        y=y_col, 
        title=title,
        template="plotly_white"
    )
    
    fig.update_xaxes(rangeslider_visible=True)
    return fig


def plot_rfm_distribution(df, x_col, y_col, title):

    fig = px.bar(df, x=x_col, y=y_col, text=y_col, title=title, template="plotly_white", hover_data={'RFM': True, 'Count': True},)
    fig.update_layout(xaxis=dict(showticklabels=False), yaxis_title="Number of Customers", title_x=0.5)
    return fig


def plot_revenue_scatter(df, x_col, y_col, size_col, text_col, title):

    fig = px.scatter(
        df, x=x_col, y=y_col, size=size_col, text=text_col,
        title=title, template="plotly_white",
        labels={x_col: "Customer Share (%)", y_col: "Revenue Share (%)"}
    )
    fig.update_traces(textposition='top center')
    return fig


def plot_rfm_heatmap(df, x_col, y_col, z_col, title):

    pivot = df.pivot(index=y_col, columns=x_col, values=z_col)
    fig = px.imshow(
        pivot, text_auto='d', title=title,
        labels=dict(x="Frequency Score", y="Recency Score", color="Avg Monetary"),
        color_continuous_scale='RdYlGn'
    )
    return fig


def plot_segment_share(df, x_col, y_col, title, color_hex="#636EFA"):

    plot_df = df.copy()
    plot_df[x_col] = plot_df[x_col].astype(str)
    
    fig = px.bar(
        plot_df, 
        x=x_col, 
        y=y_col, 
        title=title,
        template="plotly_white",
        text_auto='.1f%' 
    )
    
    fig.update_traces(
        marker_color=color_hex,
        textposition='outside',
        #textfont=dict(family="Arial", size=12, color="black"),
        texttemplate='%{y:.1f}%'
    )
    
    fig.update_layout(
        xaxis_title="Segment", 
        yaxis_title="Percentage %",
        xaxis={'type':'category'}
    )
    return fig


def plot_mba_scatter(rules_df, title="Support vs Confidence (Size/Color = Lift)"):

    plot_df = rules_df.copy()
    plot_df['rule'] = (
        plot_df['antecedents'].apply(lambda x: ', '.join(list(x))) + 
        " -> " + 
        plot_df['consequents'].apply(lambda x: ', '.join(list(x)))
    )

    fig = px.scatter(
        plot_df, 
        x="support", 
        y="confidence", 
        size="lift", 
        color="lift",
        hover_name="rule", 
        title=title,
        template="plotly_white",
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(xaxis_title="Support", yaxis_title="Confidence")
    return fig


def plot_forecast_results(train, test, forecast, title="Sales Forecast vs Actual"):

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=train.index, y=train, name='Train', line=dict(color='blue')))
    
    fig.add_trace(go.Scatter(x=test.index, y=test, name='Actual (Test)', line=dict(color='green')))
    
    fig.add_trace(go.Scatter(x=forecast.index, y=forecast, name='Forecast', line=dict(color='red', dash='dash')))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Sales",
        template="plotly_white",
        hovermode="x unified"
    )
    return fig


def plot_top_rfm_distribution(df, x_col, y_col, title):

    plot_df = df.copy()
    plot_df[x_col] = plot_df[x_col].astype(str)
    
    fig = px.bar(
        plot_df, 
        x=x_col, 
        y=y_col, 
        #color=y_col,               
        text_auto='d',             
        title=title,
        template="plotly_white",
        #color_continuous_scale='viridis'
    )
    
    fig.update_traces(textposition='outside')
    
    fig.update_layout(
        xaxis_title="RFM Score",
        yaxis_title="Number of Customers",
        coloraxis_showscale=False,  
        xaxis={'type': 'category'} 
    )
    return fig


def plot_pareto_curve(revenue_series):

    revenue_sorted = revenue_series.sort_values(ascending=False)
    cumulative_revenue = (revenue_sorted.cumsum() / revenue_sorted.sum()) * 100

    percent_customers = (np.arange(1, len(revenue_sorted) + 1) / len(revenue_sorted)) * 100

    idx_80 = np.searchsorted(cumulative_revenue, 80)
    customer_percent_at_80 = percent_customers[idx_80]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=percent_customers, 
        y=cumulative_revenue,
        mode='lines',
        name='Cumulative Revenue',
        line=dict(color='blue', width=3),
        hovertemplate='Top %{x:.2f}% Customers<br>Contribution: %{y:.2f}%'
    ))

    fig.add_hline(y=80, line_dash="dash", line_color="red", 
                  annotation_text="80% Revenue Target", annotation_position="bottom right")


    fig.add_vline(x=customer_percent_at_80, line_dash="dash", line_color="green",
                  annotation_text=f"Top {customer_percent_at_80:.1f}% Customers", 
                  annotation_position="top left")

    fig.update_layout(
        title="Pareto Analysis: Revenue Contribution by Customers",
        xaxis_title="Percentage of Customers (%)",
        yaxis_title="Cumulative Revenue (%)",
        template="plotly_white",
        hovermode="x"
    )
    return fig