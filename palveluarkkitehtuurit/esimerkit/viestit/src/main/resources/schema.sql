-- Jokaisella palvelulla oma skeema. Palvelu ei lue eikä kirjoita
-- toisen skeemaa; tieto kulkee vain viesteinä.

-- @alku myynti
CREATE SCHEMA myynti;
CREATE TABLE myynti.tilaus (
    id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asiakas VARCHAR(100) NOT NULL,
    tuote   VARCHAR(100) NOT NULL,
    maara   INT NOT NULL,
    summa   DECIMAL(10, 2) NOT NULL,
    tila    VARCHAR(20) NOT NULL
);
CREATE TABLE myynti.lahtevat (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    viesti_id   VARCHAR(36) NOT NULL UNIQUE,
    kohde       VARCHAR(100) NOT NULL,
    tyyppi      VARCHAR(50) NOT NULL,
    korrelaatio VARCHAR(36) NOT NULL,
    runko       VARCHAR(4000) NOT NULL,
    lahetetty   TIMESTAMP
);
-- @loppu myynti

-- @alku varasto
CREATE SCHEMA varasto;
CREATE TABLE varasto.saldo (
    tuote VARCHAR(100) PRIMARY KEY,
    saldo INT NOT NULL CHECK (saldo >= 0)
);
CREATE TABLE varasto.varaus (
    tilaus_id VARCHAR(36) PRIMARY KEY,
    tuote     VARCHAR(100) NOT NULL,
    maara     INT NOT NULL
);
CREATE TABLE varasto.saapuneet (
    viesti_id VARCHAR(100) PRIMARY KEY,
    tyyppi    VARCHAR(50) NOT NULL,
    runko     VARCHAR(4000) NOT NULL
);
-- @loppu varasto

CREATE SCHEMA maksut;
CREATE TABLE maksut.veloitus (
    tilaus_id VARCHAR(36) PRIMARY KEY,
    summa     DECIMAL(10, 2) NOT NULL
);
CREATE TABLE maksut.saapuneet (
    viesti_id VARCHAR(100) PRIMARY KEY,
    tyyppi    VARCHAR(50) NOT NULL,
    runko     VARCHAR(4000) NOT NULL
);

CREATE SCHEMA toimitus;
CREATE TABLE toimitus.lahetys (tilaus_id VARCHAR(36) PRIMARY KEY);
CREATE SCHEMA laskutus;
CREATE TABLE laskutus.lasku (tilaus_id VARCHAR(36) PRIMARY KEY);
