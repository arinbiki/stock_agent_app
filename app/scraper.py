
import yfinance as yf
import pandas as pd

def get_stock_data(ticker, start=None, end=None):
	"""
	Fetch historical stock data for the given ticker using yfinance.
	Optionally specify start and end dates (YYYY-MM-DD).
	Returns a DataFrame with columns: Date, Open, High, Low, Close, Volume
	"""
	try:
		data = yf.download(ticker, start=start, end=end, progress=False)
		if data.empty:
			return None
		data = data.reset_index()
		# Ensure columns are named as expected
		data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
		return data
	except Exception as e:
		print(f"Error fetching data for {ticker}: {e}")
		return None
