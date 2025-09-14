
import os
import mysql.connector
from mysql.connector import Error

def connect_to_db():
	"""
	Connect to MySQL database using credentials from environment variables.
	Returns a tuple: (connection, error_message). If successful, error_message is None.
	"""
	try:
		host = os.environ.get('DB_HOST')
		user = os.environ.get('DB_USER')
		password = os.environ.get('DB_PASSWORD')
		dbname = os.environ.get('DB_NAME')
		port = int(os.environ.get('DB_PORT', 3306))
		print(f"Connecting to MySQL with host={host}, user={user}, db={dbname}, port={port}")
		connection = mysql.connector.connect(
			host=host,
			user=user,
			password=password,
			database=dbname,
			port=port
		)
		if connection.is_connected():
			return connection, None
	except Error as e:
		print(f"Error connecting to MySQL: {e}")
		return None, str(e)
	return None, 'Unknown error'


def save_data_to_db(connection, ticker, df):
	"""
	Save stock data from DataFrame to a MySQL table named with the stock symbol and date range.
	Table name format: {ticker}_from_{start}_to_{end}
	"""
	# Get min and max date from DataFrame
	start_date = str(df['Date'].min()).replace('-', '')
	end_date = str(df['Date'].max()).replace('-', '')
	table_name = f"{ticker.lower()}_from_{start_date}_to_{end_date}"
	# MySQL table names must be alphanumeric and underscores only
	import re
	table_name = re.sub(r'[^a-zA-Z0-9_]', '_', table_name)

	create_table_query = f'''
	CREATE TABLE IF NOT EXISTS `{table_name}` (
		id INT AUTO_INCREMENT PRIMARY KEY,
		ticker VARCHAR(10),
		date DATE,
		open FLOAT,
		high FLOAT,
		low FLOAT,
		close FLOAT,
		volume BIGINT
	)'''
	insert_query = f'''
	INSERT INTO `{table_name}` (ticker, date, open, high, low, close, volume)
	VALUES (%s, %s, %s, %s, %s, %s, %s)
	'''
	try:
		cursor = connection.cursor()
		cursor.execute(create_table_query)
		for _, row in df.iterrows():
			cursor.execute(
				insert_query,
				(
					ticker,
					str(row['Date']),
					float(row['Open']),
					float(row['High']),
					float(row['Low']),
					float(row['Close']),
					int(row['Volume'])
				)
			)
		connection.commit()
		cursor.close()
	except Exception as e:
		print(f"Error saving data to MySQL: {e}")
