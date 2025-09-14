import streamlit as st
import pandas as pd
import warnings
from app.scraper import get_stock_data
from app.database import connect_to_db, save_data_to_db

warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(page_title="Stock Data Scraper (Streamlit)", page_icon="📈", layout="centered")
st.title("📈 Stock Data Scraper (Streamlit)")

st.markdown("""
Enter a stock symbol and timeline (years, max 10) to save historical data directly to your MySQL database.
""")

with st.form("scrape_form"):
    ticker = st.text_input("Stock Symbol", "AAPL")
    years = st.number_input("Timeline (years, max 10)", min_value=1, max_value=10, value=1)
    submitted = st.form_submit_button("Get & Save Data")

if submitted:
    st.info(f"Fetching data for {ticker} for the last {years} year(s)...")
    try:
        end = pd.Timestamp.today()
        start = end - pd.DateOffset(years=years)
        df = get_stock_data(ticker, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
        if df is None or df.empty:
            st.error("No data found for ticker.")
        else:
            st.success("Data fetched successfully!")
            st.dataframe(df.head(10))
            # Save to MySQL
            conn, db_error = connect_to_db()
            if conn is None:
                st.error(f"Database connection failed: {db_error}")
            else:
                try:
                    save_data_to_db(conn, ticker, df)
                    conn.close()
                    st.success("Data saved to MySQL database!")
                except Exception as e:
                    st.error(f"Error saving data: {e}")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
