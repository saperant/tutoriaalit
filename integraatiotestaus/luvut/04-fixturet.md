# Pytest-fixturet ja konttien elinkaari

Kontti on kallis: PostgreSQL käynnistyy pari sekuntia, ja koko
testisarjassa voi olla satoja tietokantaa käyttäviä testejä. Jos
jokainen testi käynnistäisi oman tietokantansa, sarja kestäisi
minuutteja. Pytestin fixturet ratkaisevat tämän laajuuksilla: kallis
resurssi luodaan kerran, halpa eristys jokaiselle testille.

## Laajuudet

Fixturen laajuus (`scope`) kertoo, kuinka pitkään sen arvo elää:

| Laajuus | Luodaan | Esimerkki |
|---------|---------|-----------|
| `session` | kerran koko testiajolle | tietokantakontti, kuvan rakennus |
| `package` | kerran pakettia kohti | harvoin tarpeen |
| `module` | kerran testitiedostoa kohti | tiedoston oma Docker-verkko |
| `class` | kerran testiluokkaa kohti | luokan yhteinen data |
| `function` | jokaiselle testille (oletus) | transaktio, tyhjä Redis |

Fixture voi käyttää vain samaa tai laajempaa laajuutta: testikohtainen
transaktio voi käyttää istunnon tietokantaa, mutta ei päinvastoin.
Laajuuksien kerrostuminen näkyy, kun pytest ajetaan valitsimella
`--setup-show`. Seuraava tiedosto ei käynnistä kontteja, vaan näyttää
pelkän rakenteen:

```{.python tiedosto="esimerkit/luku04/test_laajuudet.py" osa="laajuudet"}
```

```{.tuloste tiedosto="esimerkit/luku04/laajuudet.odotettu"}
```

`S`, `M` ja `F` ovat istunto, moduuli ja funktio. Tietokanta luodaan
kerran, skeema kerran tiedostolle ja transaktio jokaiselle testille, ja
ne puretaan käänteisessä järjestyksessä.

## Varastopalvelun fixturet

Yhteiset fixturet ovat tiedostossa `testit/conftest.py`, jonka pytest
lataa automaattisesti. Istunnon alussa käynnistetään PostgreSQL ja
migroidaan skeema:

```{.python tiedosto="esimerkit/testit/conftest.py" osa="istunto"}
```

`yield` jakaa fixturen kahtia: sitä ennen oleva koodi on alustus,
jälkeen tuleva purku. Kontti on `with`-lauseessa, joten se poistetaan,
vaikka testit epäonnistuisivat.

Testikohtainen eristys on transaktio, joka perutaan testin lopuksi:

```{.python tiedosto="esimerkit/testit/conftest.py" osa="yhteys"}
```

Tämä toimii, koska tallennusluokka osaa käyttää valmiiksi avattua
yhteyttä: silloin sen omat transaktiot ovat tallennuspisteitä
(`SAVEPOINT`) testin transaktion sisällä. Kun testi päättyy, uloin
transaktio perutaan ja kaikki testin kirjoitukset katoavat.

```{.python tiedosto="esimerkit/varasto/varasto.py" osa="pg"}
```

Ratkaisu on yleinen: Spring perii testin transaktion samalla tavalla
(`@Transactional` testiluokassa), ja SQLAlchemyn ORM:ssä sama tehdään
asetuksella `join_transaction_mode="create_savepoint"`. Luku 5
käsittelee tilanteet, joissa transaktio ei riitä.

## Muut riippuvuudet fixtureina

Redis käynnistetään samoin kerran istunnolle, ja jokainen testi saa
tyhjän tietokannan. `flushdb` on nopea, joten tässä eristys on
tyhjennys eikä transaktio:

```{.python tiedosto="esimerkit/testit/conftest.py" osa="muut"}
```

Tiedostossa on myös hintapalvelun väärennös: apukuva rakennetaan kerran
istunnolle, ja kontti on istunnon laajuinen, koska testit eivät muuta
sen tilaa pysyvästi. Testit, jotka käynnistävät palvelun eri asetuksin
(luku 9), luovat oman konttinsa.

## Hinta mitattuna

Kirjoittajan koneella testisarjan 30 testiä kestävät noin 30 sekuntia,
joista valtaosa on konttien käynnistystä. Kiinteä osuus jakautuu suunnilleen
näin (suuntaa-antavia lukuja kuormitetulta koneelta):

| Vaihe | Kesto | Kertaa |
|-------|-------|--------|
| PostgreSQL-kontin käynnistys ja valmius | 2–4 s | istunnossa 1 |
| Redis-kontin käynnistys | alle 1 s | istunnossa 1 |
| apukuvan rakennus välimuistista | alle 1 s | istunnossa 1 |
| testin transaktio ja peruutus | alle 10 ms | testiä kohti |

Jos tietokanta olisi testikohtainen, käynnistys toistuisi jokaiselle
tietokantatestille, ja sarja kestäisi minuutteja. Laajuus on siis
integraatiotestien tärkein suorituskykypäätös.

## Rinnakkaiset testit

Pytest-xdist-laajennus ajaa testejä rinnakkaisissa prosesseissa. Silloin
istuntolaajuinen fixture luodaan *jokaisessa prosessissa*, eli neljä
prosessia käynnistää neljä tietokantaa. Se on usein juuri oikein:
prosessit eivät näe toistensa dataa, ja kontteja on vähän. Jos kontin
käynnistys on hyvin kallis, prosessit voivat jakaa yhden kontin, jolloin
testien on eristettävä datansa muilla keinoin (luku 5).

## Käytännössä

- Käynnistä kontit istunnon laajuisina ja eristä testit halvemmalla:
  transaktiolla, tyhjennyksellä tai omalla skeemalla.
- Kirjoita purku `yield`-fixtureen tai `with`-lauseeseen, jotta se
  tapahtuu myös epäonnistuneen testin jälkeen.
- Pidä yhteiset fixturet `conftest.py`:ssä ja anna niille nimet, jotka
  kertovat mitä ne ovat (`pg`, `kone`, `yhteys`), ei miten ne tehdään.
- Kun testi tarvitsee poikkeavan riippuvuuden (eri versio, eri
  asetus), luo se testissä tai erillisessä fixturessa. Älä muuta
  yhteisen kontin tilaa.

## Itsearviointi

- Osaat valita fixturen laajuuden resurssin hinnan ja eristystarpeen
  mukaan.
- Osaat lukea `--setup-show`-tulosteen ja selittää alustusten ja
  purkujen järjestyksen.
- Osaat kirjoittaa fixturen, joka perii testin transaktion
  tallennuspisteillä ja peruu kaiken lopuksi.
- Osaat selittää, miten rinnakkaisajo muuttaa istuntolaajuisten
  fixturejen käyttäytymistä.
