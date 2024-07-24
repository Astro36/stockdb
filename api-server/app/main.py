from fastapi import FastAPI
import polars as pl
import psycopg
import requests


app = FastAPI()
conn = psycopg.connect("dbname=stockdb user= password=")


@app.get("/quotes/{symbol}/")
def get_market_prices(symbol: str):
    with conn.cursor() as cur:
        symbol_id = cur.execute(
            "SELECT id FROM symbols WHERE symbol = %s LIMIT 1;",
            (symbol,),
        ).fetchone()[0]
        records = cur.execute(
            """
            SELECT
                date, open, high, low, close, volume
            FROM quotes q
                JOIN symbols s ON s.id = q.symbol_id
            WHERE symbol = %s;
            """,
            (symbol,),
        ).fetchall()

        if len(records) < 1:
            df = fetch_market_prices_from_yfinance(symbol, "1719811158")
            for row in df.iter_rows(named=True):
                cur.execute(
                    "INSERT INTO quotes VALUES (%s, %s, %s, %s, %s, %s, %s);",
                    (
                        row["date"],
                        symbol_id,
                        row["open"],
                        row["high"],
                        row["low"],
                        row["close"],
                        row["volume"],
                    ),
                )
            conn.commit()


def fetch_market_prices_from_yfinance(symbol: str, start="846944000"):
    r = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start}&period2=1721800800&interval=1d&events=div%7Csplit%7Cearn",
        headers={"User-Agent": "insomnia/9.3.2"},
    )
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
    # split_ratios = [
    #     [timestamp, event["numerator"] / event["denominator"]]
    #     for timestamp, event in data["chart"]["result"][0]["events"]["splits"].items()
    # ]
    return df
