-- @alku v4
-- Asiakkaan antama Idempotency-Key sidotaan luotuun tilaukseen.
-- Pääavain estää saman avaimen käsittelyn kahdesti.
CREATE TABLE idempotenssi (
    asiakas   VARCHAR(50)  NOT NULL,
    avain     VARCHAR(100) NOT NULL,
    tilaus_id BIGINT REFERENCES tilaus (id),
    PRIMARY KEY (asiakas, avain)
);
-- @loppu v4
