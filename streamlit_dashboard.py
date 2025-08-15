import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# Set page configuration
st.set_page_config(
    page_title="Sales Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
.stSelectbox > div > div {
    background-color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# Load and cache data
@st.cache_data
def load_data():
    """Load and preprocess the sales data"""
    try:
        df = pd.read_csv("sales_data_sample (1).csv", encoding='latin1')
        
        # Data preprocessing
        df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])
        df['Year'] = df['ORDERDATE'].dt.year
        df['Month'] = df['ORDERDATE'].dt.month
        df['MonthName'] = df['ORDERDATE'].dt.month_name()
        df['Quarter'] = df['ORDERDATE'].dt.quarter
        df['Weekday'] = df['ORDERDATE'].dt.day_name()
        
        # Remove columns with high missing values if they exist
        columns_to_drop = ['ADDRESSLINE2', 'STATE', 'TERRITORY']
        existing_columns = [col for col in columns_to_drop if col in df.columns]
        if existing_columns:
            df.drop(columns=existing_columns, inplace=True)
        
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'sales_data_sample (1).csv' is in the correct directory.")
        return None

# Main dashboard function
def main():
    # Title and header
    st.markdown('<h1 class="main-header">📊 Sales Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar filters
    st.sidebar.title("🔍 Filters")
    st.sidebar.markdown("---")
    
    # Year filter
    years = sorted(df['Year'].unique())
    selected_years = st.sidebar.multiselect(
        "📅 Select Years", 
        years, 
        default=years,
        help="Choose one or more years to analyze"
    )
    
    # Product line filter
    product_lines = sorted(df['PRODUCTLINE'].unique())
    selected_products = st.sidebar.multiselect(
        "🏷️ Select Product Lines", 
        product_lines, 
        default=product_lines,
        help="Choose product lines to include in analysis"
    )
    
    # Deal size filter
    deal_sizes = sorted(df['DEALSIZE'].unique())
    selected_deal_sizes = st.sidebar.multiselect(
        "💰 Select Deal Sizes", 
        deal_sizes, 
        default=deal_sizes,
        help="Filter by deal size categories"
    )
    
    # Country filter
    countries = sorted(df['COUNTRY'].unique())
    selected_countries = st.sidebar.multiselect(
        "🌍 Select Countries", 
        countries, 
        default=countries[:10] if len(countries) > 10 else countries,
        help="Choose countries to analyze"
    )
    
    # Apply filters
    filtered_df = df[
        (df['Year'].isin(selected_years)) & 
        (df['PRODUCTLINE'].isin(selected_products)) &
        (df['DEALSIZE'].isin(selected_deal_sizes)) &
        (df['COUNTRY'].isin(selected_countries))
    ]
    
    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your selections.")
        return
    
    # Key Metrics Section
    st.markdown("## 📈 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_sales = filtered_df['SALES'].sum()
        st.metric("💰 Total Sales", f"${total_sales:,.0f}")
    
    with col2:
        total_orders = filtered_df['ORDERNUMBER'].nunique()
        st.metric("📦 Total Orders", f"{total_orders:,}")
    
    with col3:
        avg_order_value = filtered_df['SALES'].mean()
        st.metric("💵 Avg Order Value", f"${avg_order_value:,.0f}")
    
    with col4:
        total_customers = filtered_df['CUSTOMERNAME'].nunique()
        st.metric("👥 Total Customers", f"{total_customers:,}")
    
    with col5:
        total_products = filtered_df['PRODUCTCODE'].nunique()
        st.metric("🛍️ Total Products", f"{total_products:,}")
    
    st.markdown("---")
    
    # Charts Section
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Sales Analysis", "🏷️ Product Performance", "👥 Customer Insights", "📅 Time Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sales by Product Line")
            product_sales = filtered_df.groupby('PRODUCTLINE')['SALES'].sum().sort_values(ascending=False)
            
            fig = px.bar(
                x=product_sales.values, 
                y=product_sales.index,
                orientation='h',
                title="Sales Revenue by Product Line",
                labels={'x': 'Sales ($)', 'y': 'Product Line'},
                color=product_sales.values,
                color_continuous_scale='viridis'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Sales by Deal Size")
            deal_sales = filtered_df.groupby('DEALSIZE')['SALES'].sum()
            
            fig = px.pie(
                values=deal_sales.values, 
                names=deal_sales.index,
                title="Sales Distribution by Deal Size",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Geographic Analysis
        st.subheader("🌍 Geographic Sales Distribution")
        country_sales = filtered_df.groupby('COUNTRY')['SALES'].sum().sort_values(ascending=False).head(15)
        
        fig = px.bar(
            x=country_sales.index, 
            y=country_sales.values,
            title="Top 15 Countries by Sales Revenue",
            labels={'x': 'Country', 'y': 'Sales ($)'},
            color=country_sales.values,
            color_continuous_scale='plasma'
        )
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top 10 Products by Revenue")
            top_products = filtered_df.groupby('PRODUCTCODE')['SALES'].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=top_products.values, 
                y=top_products.index,
                orientation='h',
                title="Top 10 Products by Sales",
                labels={'x': 'Sales ($)', 'y': 'Product Code'},
                color=top_products.values,
                color_continuous_scale='blues'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Quantity vs Price Analysis")
            fig = px.scatter(
                filtered_df, 
                x='QUANTITYORDERED', 
                y='PRICEEACH',
                size='SALES',
                color='PRODUCTLINE',
                title="Quantity vs Price (Size = Sales)",
                labels={'QUANTITYORDERED': 'Quantity Ordered', 'PRICEEACH': 'Price Each ($)'}
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # Product Line Performance Table
        st.subheader("📋 Product Line Performance Summary")
        product_summary = filtered_df.groupby('PRODUCTLINE').agg({
            'SALES': ['sum', 'mean', 'count'],
            'QUANTITYORDERED': 'sum',
            'ORDERNUMBER': 'nunique'
        }).round(2)
        
        product_summary.columns = ['Total Sales', 'Avg Sale', 'Total Transactions', 'Total Quantity', 'Unique Orders']
        product_summary = product_summary.sort_values('Total Sales', ascending=False)
        st.dataframe(product_summary, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top 15 Customers by Revenue")
            top_customers = filtered_df.groupby('CUSTOMERNAME')['SALES'].sum().sort_values(ascending=False).head(15)
            
            fig = px.bar(
                x=top_customers.values, 
                y=top_customers.index,
                orientation='h',
                title="Top 15 Customers by Revenue",
                labels={'x': 'Sales ($)', 'y': 'Customer Name'},
                color=top_customers.values,
                color_continuous_scale='greens'
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Customer Order Frequency")
            customer_orders = filtered_df.groupby('CUSTOMERNAME')['ORDERNUMBER'].nunique().sort_values(ascending=False).head(15)
            
            fig = px.bar(
                x=customer_orders.values, 
                y=customer_orders.index,
                orientation='h',
                title="Top 15 Customers by Order Count",
                labels={'x': 'Number of Orders', 'y': 'Customer Name'},
                color=customer_orders.values,
                color_continuous_scale='oranges'
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
        
        # Customer Analysis Table
        st.subheader("👥 Customer Performance Analysis")
        customer_analysis = filtered_df.groupby('CUSTOMERNAME').agg({
            'SALES': ['sum', 'mean'],
            'ORDERNUMBER': 'nunique',
            'QUANTITYORDERED': 'sum'
        }).round(2)
        
        customer_analysis.columns = ['Total Sales', 'Avg Order Value', 'Total Orders', 'Total Quantity']
        customer_analysis['Revenue per Order'] = (customer_analysis['Total Sales'] / customer_analysis['Total Orders']).round(2)
        customer_analysis = customer_analysis.sort_values('Total Sales', ascending=False).head(20)
        st.dataframe(customer_analysis, use_container_width=True)
    
    with tab4:
        # Monthly Sales Trend
        st.subheader("📈 Monthly Sales Trend")
        monthly_sales = filtered_df.groupby(['Year', 'Month'])['SALES'].sum().reset_index()
        monthly_sales['Date'] = pd.to_datetime(monthly_sales[['Year', 'Month']].assign(day=1))
        
        fig = px.line(
            monthly_sales, 
            x='Date', 
            y='SALES',
            title="Monthly Sales Trend Over Time",
            labels={'SALES': 'Sales ($)', 'Date': 'Month-Year'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sales by Quarter")
            quarterly_sales = filtered_df.groupby(['Year', 'Quarter'])['SALES'].sum().reset_index()
            quarterly_sales['Period'] = quarterly_sales['Year'].astype(str) + '-Q' + quarterly_sales['Quarter'].astype(str)
            
            fig = px.bar(
                quarterly_sales, 
                x='Period', 
                y='SALES',
                title="Quarterly Sales Performance",
                labels={'SALES': 'Sales ($)', 'Period': 'Quarter'},
                color='SALES',
                color_continuous_scale='viridis'
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Sales by Day of Week")
            weekday_sales = filtered_df.groupby('Weekday')['SALES'].sum().reindex([
                'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
            ])
            
            fig = px.bar(
                x=weekday_sales.index, 
                y=weekday_sales.values,
                title="Sales by Day of Week",
                labels={'x': 'Day of Week', 'y': 'Sales ($)'},
                color=weekday_sales.values,
                color_continuous_scale='plasma'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Data Export Section
    st.markdown("---")
    st.markdown("## 📁 Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export filtered data to Excel
        @st.cache_data
        def convert_df_to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Filtered Data', index=False)
                
                # Add summary sheet
                summary_data = {
                    'Metric': ['Total Sales', 'Total Orders', 'Avg Order Value', 'Total Customers', 'Total Products'],
                    'Value': [
                        df['SALES'].sum(),
                        df['ORDERNUMBER'].nunique(),
                        df['SALES'].mean(),
                        df['CUSTOMERNAME'].nunique(),
                        df['PRODUCTCODE'].nunique()
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            output.seek(0)
            return output
        
        excel_data = convert_df_to_excel(filtered_df)
        st.download_button(
            label="📊 Download Filtered Data (Excel)",
            data=excel_data,
            file_name=f"sales_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        # Export filtered data to CSV
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📄 Download Filtered Data (CSV)",
            data=csv_data,
            file_name=f"sales_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col3:
        # Show data info
        if st.button("ℹ️ Show Data Info"):
            st.write(f"**Filtered Dataset Shape:** {filtered_df.shape[0]} rows × {filtered_df.shape[1]} columns")
            st.write(f"**Date Range:** {filtered_df['ORDERDATE'].min().date()} to {filtered_df['ORDERDATE'].max().date()}")
            st.write(f"**Total Sales in Selection:** ${filtered_df['SALES'].sum():,.2f}")
    
    # Data Preview Section
    st.markdown("---")
    st.markdown("## 🔍 Data Preview")
    
    if st.checkbox("Show filtered data preview"):
        st.dataframe(
            filtered_df.head(100), 
            use_container_width=True,
            height=400
        )
        st.write(f"Showing first 100 rows of {len(filtered_df)} total filtered records")

# Sidebar info
def sidebar_info():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Dashboard Info")
    st.sidebar.info(
        """
        This dashboard provides comprehensive analysis of sales data including:
        
        • **Key Performance Indicators**
        • **Sales Analysis by Product & Geography**
        • **Customer Insights & Behavior**
        • **Time-based Trends**
        • **Interactive Filtering**
        • **Data Export Capabilities**
        
        Use the filters above to customize your analysis.
        """
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Built with Streamlit 🚀**")

if __name__ == "__main__":
    sidebar_info()
    main()
