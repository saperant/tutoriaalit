-- @alku skeema
-- Yksi tietokanta, mutta jokaisella moduulilla omat taulunsa. Taulun
-- etuliite kertoo omistajan; toisen moduulin tauluja ei lueta suoraan.
CREATE TABLE myynti_tilaus (
    id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asiakas VARCHAR(100) NOT NULL,
    tuote   VARCHAR(100) NOT NULL,
    maara   INT NOT NULL CHECK (maara > 0)
);
CREATE TABLE varasto_saldo (
    tuote VARCHAR(100) PRIMARY KEY,
    saldo INT NOT NULL CHECK (saldo >= 0)
);
CREATE TABLE laskutus_lasku (
    id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tilaus_id BIGINT NOT NULL,
    asiakas   VARCHAR(100) NOT NULL
);
-- @loppu skeema
