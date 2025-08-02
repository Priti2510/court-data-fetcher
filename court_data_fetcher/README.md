# Court-Data Fetcher & Mini-Dashboard

## Description
Fetches case details and order PDFs from Faridabad District Court using Python, Flask, and Playwright.

## Setup
1. Install Python deps:
```bash
pip install -r requirements.txt
playwright install
```
2. Run the app:
```bash
python app.py
```
3. Open `http://localhost:5000`

## Docker
```bash
docker build -t court-fetcher .
docker run -p 5000:5000 court-fetcher
```

## CAPTCHA
Manually solve CAPTCHA in browser when prompted.

## License
MIT