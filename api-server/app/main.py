from datetime import datetime, timedelta
from fastapi import FastAPI, Response
import os
import polars as pl
import psycopg
import requests


app = FastAPI()
conn = psycopg.connect(f"host=db dbname={os.getenv("POSTGRES_DB")} user={os.getenv("POSTGRES_USER")} password={os.getenv("POSTGRES_PASSWORD")}")


@app.get("/symbols")
def get_listed_issues():
    with conn.cursor() as cur:
        symbols = [row[0] for row in cur.execute("SELECT yfsymbol FROM symbols;").fetchall()]
        return symbols


@app.get("/quotes/{symbol}")
def get_market_prices(symbol: str):
    with conn.cursor() as cur:
        updated_at_record = cur.execute(
            "SELECT updated_at FROM quote_logs l JOIN symbols s ON s.id = l.symbol_id WHERE yfsymbol = %s",
            (symbol,),
        ).fetchone()
        if updated_at_record and (updated_at_record[0] + timedelta(days=1)) >= datetime.now().date():
            records = cur.execute(
                """
                SELECT
                    date, open, high, low, close, volume
                FROM quotes q
                    JOIN symbols s ON s.id = q.symbol_id
                WHERE yfsymbol = %s;
                """,
                (symbol,),
            ).fetchall()
            df = pl.DataFrame(records, schema=["date", "open", "high", "low", "close", "volume"])
            return Response(content=df.write_csv())

        symbol_id, listing_date = cur.execute(
            "SELECT id, listing_date FROM symbols WHERE yfsymbol = %s LIMIT 1;",
            (symbol,),
        ).fetchone()

        listing_timestamp = (
            int(datetime.combine(listing_date, datetime.min.time()).timestamp()) if listing_date.year >= 1970 else 0
        )
        end_datetime = datetime.now() - timedelta(days=1)
        end_timestamp = int(end_datetime.timestamp())

        if (df := fetch_market_prices_from_yfinance(symbol, start=listing_timestamp, end=end_timestamp)) is not None:
            cur.executemany(
                f"INSERT INTO quotes VALUES (%s, {symbol_id}, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;",
                df.rows(),
            )
            cur.execute(
                "INSERT INTO quote_logs VALUES (%s, %s) ON CONFLICT (symbol_id) DO UPDATE SET updated_at = %s;",
                (symbol_id, end_datetime, end_datetime),
            )
            conn.commit()
            return Response(content=df.write_csv())

        return Response(status_code=404)


def fetch_market_prices_from_yfinance(symbol: str, start="846944000", end=int(datetime.now().timestamp())):
    if start < 846944000:  # 2000-01-04
        start = 846944000
    r = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start}&period2={end}&interval=1d&events=div%7Csplit%7Cearn",
        headers={"User-Agent": "insomnia/9.3.2"},
    )
    if r.status_code == 200:
        data = r.json()
        df = pl.DataFrame(
            {
                "date": data["chart"]["result"][0]["timestamp"],
                "open": data["chart"]["result"][0]["indicators"]["quote"][0]["open"],
                "high": data["chart"]["result"][0]["indicators"]["quote"][0]["high"],
                "low": data["chart"]["result"][0]["indicators"]["quote"][0]["low"],
                "close": data["chart"]["result"][0]["indicators"]["quote"][0]["close"],
                "volume": data["chart"]["result"][0]["indicators"]["quote"][0]["volume"],
            }
        ).with_columns(pl.from_epoch("date").dt.strftime("%Y-%m-%d"))
        return df
    return None
