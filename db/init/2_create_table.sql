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
    open      numeric(10, 2) NOT NULL,
    high      numeric(10, 2) NOT NULL,
    low       numeric(10, 2) NOT NULL,
    close     numeric(10, 2) NOT NULL,
    volume    integer        NOT NULL
);
SELECT create_hypertable('quotes', by_range('date'));
CREATE UNIQUE INDEX quotes_symbol_idx ON quotes (symbol_id, date);
