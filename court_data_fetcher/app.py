from flask import Flask, render_template, request
from scraper import scrape_case_details
import sqlite3
from datetime import datetime

app = Flask(__name__)

def log_to_db(case_type, case_number, year, raw_html):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_type TEXT,
        case_number TEXT,
        year TEXT,
        timestamp TEXT,
        raw_html TEXT
    )''')
    cursor.execute('INSERT INTO logs (case_type, case_number, year, timestamp, raw_html) VALUES (?, ?, ?, ?, ?)',
                (case_type, case_number, year, datetime.now().isoformat(), raw_html))
    conn.commit()
    conn.close()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch():
    case_type = request.form['case_type']
    case_number = request.form['case_number']
    year = request.form['year']

    try:
        result, raw_html = scrape_case_details(case_type, case_number, year)
        log_to_db(case_type, case_number, year, raw_html)
        return render_template('result.html', result=result)
    except Exception as e:
        return f"<h3>Error: {str(e)}</h3>"

if __name__ == '__main__':
    app.run(debug=True)