
import streamlit as st
import pandas as pd
import yfinance as yf
import mysql.connector
import datetime
import warnings
<<<<<<< HEAD
from app.scraper import get_stock_data
from app.database import connect_to_db, save_data_to_db
import streamlit as st
import mysql.connector
=======
import re
>>>>>>> ac22aad (Update: multi-asset input, bugfixes, and secrets config)

try:
    db = mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        port=int(st.secrets["DB_PORT"])
    )
    cursor = db.cursor()
    cursor.execute("SELECT 1")
    st.success("Database connection and simple query succeeded!")
except Exception as e:
    st.error(f"Database connection failed: {e}")
warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(page_title="Multi-Asset Data Scraper", page_icon="�", layout="centered")
st.title("� Multi-Asset Data Scraper (Stocks, Indexes, FX, Commodities)")

st.markdown("""
Select asset type, choose assets (or fetch all), and date range (max 15 years). Data will be saved to MySQL and available for download.
""")

# --- Asset lists (expand as needed) ---

# Asset type options
ASSET_TYPES = ["Stock", "Index", "Currency", "Commodity"]

with st.form("asset_form"):
    asset_type = st.selectbox("Asset Type", ASSET_TYPES)
    tickers_input = st.text_area(
        f"Enter {asset_type} symbols (comma-separated)",
        placeholder="e.g. AAPL, MSFT, GOOGL for stocks; ^GSPC, ^DJI for indexes; EURUSD=X, USDJPY=X for currencies; GC=F, CL=F for commodities"
    )
    today = datetime.date.today()
    min_year = today.year - 15
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From date", value=datetime.date(min_year, 1, 1), min_value=datetime.date(min_year, 1, 1), max_value=today)
    with col2:
        end_date = st.date_input("To date", value=today, min_value=datetime.date(min_year, 1, 1), max_value=today)
    submitted = st.form_submit_button("Fetch, Save & Download")

def parse_tickers(tickers_input):
    return [t.strip() for t in tickers_input.split(',') if t.strip()]

def fetch_data(ticker, start, end):
    try:
        df = yf.download(ticker, start=start, end=end, progress=False)
        if df.empty:
            return None
        df = df.reset_index()
        # Standardize columns
        df = df.rename(columns={"Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
        df = df[["date", "open", "high", "low", "close", "volume"]]
        return df
    except Exception as e:
        st.warning(f"Error fetching {ticker}: {e}")
        return None

def save_to_mysql(asset_type, ticker, df, start, end):
    # Use st.secrets for Streamlit Cloud
    try:
        conn = mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            port=int(st.secrets["DB_PORT"])
        )
        table_name = f"{asset_type.lower()}_{re.sub(r'[^a-zA-Z0-9_]', '_', ticker)}_{start.replace('-', '')}_to_{end.replace('-', '')}"
        create_table = f'''
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            asset_type VARCHAR(20),
            ticker VARCHAR(32),
            date DATE,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume BIGINT
        )'''
        insert_row = f'''
        INSERT INTO `{table_name}` (asset_type, ticker, date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor = conn.cursor()
        cursor.execute(create_table)
        for _, row in df.iterrows():
            cursor.execute(insert_row, (
                asset_type, ticker, str(row['date']), float(row['open']), float(row['high']), float(row['low']), float(row['close']), int(row['volume'])
            ))
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

if submitted:
    selected_assets = parse_tickers(tickers_input)
    if not selected_assets:
        st.error("Please enter at least one symbol.")
    else:
        st.info(f"Fetching data for {', '.join(selected_assets)} from {start_date} to {end_date}...")
        all_data = []
        for ticker in selected_assets:
            df = fetch_data(ticker, str(start_date), str(end_date))
            if df is None or df.empty:
                st.warning(f"No data for {ticker}")
                continue
            st.success(f"Fetched {len(df)} rows for {ticker}")
            ok, err = save_to_mysql(asset_type, ticker, df, str(start_date), str(end_date))
            if ok:
                st.success(f"Saved {ticker} data to MySQL!")
            else:
                st.error(f"MySQL error for {ticker}: {err}")
            df["asset_type"] = asset_type
            df["ticker"] = ticker
            all_data.append(df)
        if all_data:
            result_df = pd.concat(all_data, ignore_index=True)
            st.dataframe(result_df.head(20))
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download All Data as CSV", csv, file_name="historical_data.csv", mime="text/csv")
        else:
            st.error("No data fetched for selected assets and date range.")
