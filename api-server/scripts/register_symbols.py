import argparse
import polars as pl
import psycopg


def main():
    df = (
        pl.read_csv("data/krx_listed_issues_20240725.csv")
        .filter(pl.col("주식종류") == "보통주")
        .sort("상장일")
        .select(
            [
                pl.col("한글 종목약명").alias("name"),
                pl.col("상장일")
                .str.to_datetime(format="%Y/%m/%d")
                .dt.strftime("%Y-%m-%d")
                .alias("listing_date"),
                pl.concat_str(
                    [
                        "단축코드",
                        pl.when(pl.col("시장구분") == "KOSPI")
                        .then(pl.lit(".KS"))
                        .otherwise(pl.lit(".KQ")),
                    ]
                ).alias("yfsymbol"),
            ]
        )
    )
    print(df)

    with psycopg.connect("dbname=stockdb user= password=") as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO symbols (name, listing_date, yfsymbol) VALUES (%s, %s, %s)",
                df.rows(),
            )


if __name__ == "__main__":
    main()
