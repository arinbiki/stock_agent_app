import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from app.scraper import get_stock_data
from app.database import connect_to_db, save_data_to_db

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        years = int(request.form.get('years', 1))
        if not ticker:
            flash('Please enter a stock ticker.')
            return redirect(url_for('index'))
        try:
            end = pd.Timestamp.today()
            start = end - pd.DateOffset(years=years)
            df = get_stock_data(ticker, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
            if df is None or df.empty:
                flash('No data found for ticker.')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error fetching data: {e}')
            return redirect(url_for('index'))
        conn, db_error = connect_to_db()
        if conn is None:
            flash(f'Database connection failed: {db_error}')
            return redirect(url_for('index'))
        try:
            save_data_to_db(conn, ticker, df)
            conn.close()
            flash('Data saved to MySQL database!')
        except Exception as e:
            flash(f'Error saving data: {e}')
            return redirect(url_for('index'))
        return render_template('result.html', ticker=ticker, df=df)
    return render_template('flask_index.html')

if __name__ == '__main__':
    app.run(debug=True)
