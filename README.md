# Stock Agent App

A Streamlit-based application for scraping historical stock data and saving it to a MySQL database.

## Features
- Enter a stock ticker and date range
- Fetch historical stock data using yfinance
- Save data to a remote MySQL database (each symbol/date-range in a separate table)
- Clean, modern Streamlit UI

## Setup
1. Clone this repository:
   ```sh
   git clone https://github.com/arinbiki/stock_agent_app.git
   cd stock_agent_app
   ```
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On Mac/Linux
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up your `.env` file with your MySQL credentials:
   ```env
   DB_HOST=your_host
   DB_PORT=your_port
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_NAME=your_db
   ```
5. Run the Streamlit app:
   ```sh
   streamlit run streamlit_app.py
   ```

## Usage
- Enter the stock ticker (e.g., AAPL), start year, and end year.
- Click "Scrape and Save" to fetch and store the data.
- Data is saved in a new MySQL table for each symbol and date range.

## License
MIT
