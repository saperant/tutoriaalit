-- Tuotteet. SKU on yksilöivä kirjainkoosta riippumatta: "abc-1" ja
-- "ABC-1" ovat sama nimike.
CREATE TABLE tuotteet (
    sku   text PRIMARY KEY,
    nimi  text NOT NULL,
    saldo integer NOT NULL CHECK (saldo >= 0)
);
CREATE UNIQUE INDEX tuotteet_sku_pienin ON tuotteet (lower(sku));
