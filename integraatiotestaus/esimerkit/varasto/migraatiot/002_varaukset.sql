-- Varaukset. Aikaleima tallennetaan aikavyöhykkeen kanssa.
CREATE TABLE varaukset (
    tunnus bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku    text NOT NULL REFERENCES tuotteet (sku),
    maara  integer NOT NULL CHECK (maara > 0),
    luotu  timestamptz NOT NULL DEFAULT now()
);
