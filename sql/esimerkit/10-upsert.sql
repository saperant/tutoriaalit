-- UPSERT ja RETURNING: varastosaldon päivitys.
.headers on
.mode box

-- @alku taulu
CREATE TABLE varasto (
    tuote_id INTEGER PRIMARY KEY,
    saldo    INTEGER NOT NULL CHECK (saldo >= 0),
    paivitetty TEXT NOT NULL
) STRICT;
INSERT INTO varasto VALUES (1, 40, '2026-11-01'), (2, 15, '2026-11-01');
-- @loppu taulu

-- @alku upsert
-- Saapuva erä: lisää uusi tuote tai kasvata olemassa olevan saldoa.
INSERT INTO varasto (tuote_id, saldo, paivitetty)
VALUES (2, 10, '2026-11-20'), (3, 25, '2026-11-20')
ON CONFLICT (tuote_id) DO UPDATE
    SET saldo      = saldo + excluded.saldo,
        paivitetty = excluded.paivitetty
RETURNING tuote_id, saldo;
-- @loppu upsert

-- @alku returning
-- Ehdollinen vähennys: onnistuu vain, jos saldo riittää.
UPDATE varasto SET saldo = saldo - 5
WHERE tuote_id = 3 AND saldo >= 5
RETURNING tuote_id, saldo AS uusi_saldo;
-- @loppu returning
