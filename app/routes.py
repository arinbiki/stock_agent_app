

from flask import Blueprint, render_template, send_file, make_response

from flask import request, redirect, url_for, flash
import pandas as pd

from . import scraper
from .database import connect_to_db, save_data_to_db


main = Blueprint('main', __name__)

@main.route('/')
def home():
	return render_template('index.html')


@main.route('/scrape', methods=['POST'])
def scrape():
	years = int(request.form.get('years', 1))
	ticker = request.form.get('ticker')
	if not ticker:
		flash('Please enter a stock ticker.')
		return redirect(url_for('main.home'))

	try:
		import pandas as pd
		end = pd.Timestamp.today()
		start = end - pd.DateOffset(years=years)
		df = scraper.get_stock_data(ticker, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
		if df is None or df.empty:
			flash('No data found for ticker.')
			return redirect(url_for('main.home'))
	except Exception as e:
		flash(f'Error fetching data: {e}')
		return redirect(url_for('main.home'))

	# Save to database only
	conn, db_error = connect_to_db()
	if conn is None:
		flash(f'Database connection failed: {db_error}')
		return redirect(url_for('main.home'))
	try:
		save_data_to_db(conn, ticker, df)
		conn.close()
		flash('Data saved to MySQL database!')
	except Exception as e:
		flash(f'Error saving data: {e}')
		return redirect(url_for('main.home'))

	return redirect(url_for('main.home'))
