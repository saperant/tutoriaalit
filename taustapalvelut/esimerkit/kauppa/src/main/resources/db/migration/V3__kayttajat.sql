CREATE TABLE kayttaja (
    tunnus   VARCHAR(50)  PRIMARY KEY,
    salasana VARCHAR(100) NOT NULL,   -- tiiviste, ei koskaan selväkieli
    rooli    VARCHAR(20)  NOT NULL
);
