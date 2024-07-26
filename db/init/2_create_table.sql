CREATE TABLE symbols (
    id           integer               PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name         character varying(20) NOT NULL,
    listing_date date                  NOT NULL,
    yfsymbol     character varying(10) NOT NULL
);
CREATE INDEX symbols_name_idx ON symbols (name);
CREATE INDEX symbols_yfsymbol_idx ON symbols (yfsymbol);

CREATE TABLE quotes (
    date      date           NOT NULL,
    symbol_id integer        NOT NULL REFERENCES symbols,
    open      numeric(12, 2),
    high      numeric(12, 2),
    low       numeric(12, 2),
    close     numeric(12, 2),
    volume    bigint
);
SELECT create_hypertable('quotes', by_range('date'));
CREATE UNIQUE INDEX quotes_symbol_idx ON quotes (symbol_id, date);

CREATE TABLE quote_logs (
    symbol_id  integer PRIMARY KEY,
    updated_at date    NOT NULL
);
