-- Lyhytosoitepalvelun tietokanta. Koodi on pääavain, joten haku on
-- yksi indeksihaku, ja koodin perusteella taulun voi myöhemmin osioida
-- tiivisteellä (PARTITION BY HASH (koodi)).
CREATE SEQUENCE linkki_numero;

CREATE TABLE linkit (
    koodi  text PRIMARY KEY,
    osoite text NOT NULL CHECK (length(osoite) <= 2048),
    luotu  timestamptz NOT NULL DEFAULT now()
);
