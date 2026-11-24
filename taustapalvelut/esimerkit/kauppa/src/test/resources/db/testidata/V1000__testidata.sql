-- Testikäyttäjät. Tiivisteet on laskettu sovelluksen PasswordEncoderilla;
-- selväkieliset salasanat ovat vain testeissä.
INSERT INTO kayttaja (tunnus, salasana, rooli) VALUES
    ('aino',
     '{bcrypt}$2a$10$rA5BHtODneVqQOGkR56w9OhgxYFYI0O2v75q2kL/rdECJ5n5pRYye',
     'ASIAKAS'),
    ('pekka',
     '{bcrypt}$2a$10$lswynRN7Yw/sh.j22KolYuV649Ol0KAmHojkyFWD0mB.Q4r8LG0GK',
     'ASIAKAS'),
    ('yllapito',
     '{bcrypt}$2a$10$5FVIR9LTEN8KH6K/BCcpiuOyEzXejjHqqM6O9rq6Bn79FBx.cTLnK',
     'YLLAPITAJA');

INSERT INTO tuote (nimi, hinta_sentteina, saldo) VALUES
    ('Kahvipavut 500 g', 1290, 100),
    ('Vihreä tee', 590, 50),
    ('Kahvikuppi', 1500, 3),
    ('Maitovaahdotin', 3990, 10);
