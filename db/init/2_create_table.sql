CREATE TABLE symbols (
    id     integer               PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    symbol character varying(10) NOT NULL,
    name   character varying(20) NOT NULL
);
CREATE INDEX symbols_name_idx ON symbols (name);

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
CREATE UNIQUE INDEX quotes_symbol_idx ON quotes (symbols, date);
