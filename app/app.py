from flask import Flask, render_template

from flask import request
from .scraper import get_stock_data
from .database import connect_to_db, save_data_to_db

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


# Route to handle scraping and saving
@app.route('/scrape', methods=['POST'])
def scrape():
    ticker = request.form.get('ticker')
    if not ticker:
        return 'No ticker provided', 400
    df = get_stock_data(ticker)
    if df is None or df.empty:
        return 'No data found for ticker', 404
    conn = connect_to_db()
    if conn is None:
        return 'Database connection failed', 500
    save_data_to_db(conn, ticker, df)
    conn.close()
    return f'Successfully saved data for {ticker}!'

if __name__ == '__main__':
    app.run(debug=True)
