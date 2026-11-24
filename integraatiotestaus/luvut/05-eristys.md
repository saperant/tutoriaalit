# Testidata, migraatiot ja eristys

Integraatiotestin tietokanta on yhteinen: istunnon aikana kaikki testit
käyttävät samaa konttia. Jotta testit eivät riippuisi toisistaan, jokaisen
testin on aloitettava tunnetusta tilasta ja jätettävä tila sellaiseksi,
ettei seuraava testi huomaa mitään. Tämä luku käsittelee kolme kysymystä:
mistä skeema tulee, miten testit eristetään ja millaista testidatan
pitäisi olla.

## Skeema migraatioista

Testitietokannan skeeman on oltava *sama* kuin tuotannossa. Varmin tapa
on luoda se samoilla migraatioilla, joilla tuotantokanta päivitetään.
Silloin testi testaa samalla myös migraatiot: rikkinäinen migraatio
pysäyttää testisarjan heti istunnon alussa.

Varastopalvelun migraatiot ovat numeroituja SQL-tiedostoja:

```{.sql tiedosto="esimerkit/varasto/migraatiot/001_tuotteet.sql"}
```

```{.sql tiedosto="esimerkit/varasto/migraatiot/002_varaukset.sql"}
```

Ajaja kirjaa tehdyt migraatiot tauluun, joten sitä voi kutsua toistuvasti:

```{.python tiedosto="esimerkit/varasto/migraatiot.py" osa="migroi"}
```

Tuotannossa sama tehdään työkalulla: Pythonissa Alembic, Javassa Flyway
tai Liquibase. Periaate on sama, ja testi kutsuu työkalua samoin kuin
käyttöönotto. Vältä erillistä testiskeemaa (esimerkiksi ORM:n
`create_all()` testeissä ja migraatiot tuotannossa): ne erkanevat
toisistaan, ja testit hyväksyvät skeeman, jota tuotannossa ei ole.

## Kolme eristystapaa

Eristykseen on kolme yleistä tapaa. Seuraava esimerkki ajaa kaikki kolme
samassa kontissa:

```{.python tiedosto="esimerkit/luku05/eristys.py" osa="peruutus"}
```

```{.python tiedosto="esimerkit/luku05/eristys.py" osa="tyhjennys"}
```

```{.python tiedosto="esimerkit/luku05/eristys.py" osa="pohja"}
```

```{.tuloste tiedosto="esimerkit/luku05/eristys.odotettu"}
```

| Tapa | Nopeus | Toimii, kun | Ei toimi, kun |
|----------|--------|--------------------------|--------------------------|
| peruutus | nopein | testi käyttää fixturen yhteyttä | koodi avaa omia yhteyksiä tai commitoi itse |
| tyhjennys | kohtalainen | koodi tekee omat transaktionsa | testit ajetaan rinnakkain samaan kantaan |
| oma kanta pohjasta | hitain | tarvitaan täysi eristys | pohjaan on avoimia yhteyksiä |

**Peruutus** on oletus, ja varastopalvelun testit käyttävät sitä
(luku 4). Se ei kuitenkaan sovi testiin, joka tarvitsee *useita
erillisiä transaktioita*: samanaikaisuustesti, jossa kahdeksan säiettä
varaa samaa tuotetta, ei voi elää yhden yhteyden sisällä.

**Tyhjennys** (`TRUNCATE`) sopii koodiin, joka avaa omat yhteytensä,
kuten taustatyöhön tai HTTP-rajapintaa kutsuvaan testiin. Tyhjennettävät
taulut on lueteltava, ja viiteavaimet on otettava huomioon (`TRUNCATE`
useita tauluja kerralla tai `CASCADE`).

**Pohjasta kopioitu kanta** (`CREATE DATABASE … TEMPLATE`) antaa jokaiselle
testille täysin oman tietokannan. Kopio on tiedostotason kopio, joten se
on paljon nopeampi kuin migraatioiden ajaminen, mutta silti hitaampi kuin
transaktio. Rajoitus: PostgreSQL ei kopioi kantaa, johon on yhteyksiä,
joten pohja on pidettävä erillään.

## Satunnaiset nimet ja rinnakkaisuus

Kun testi kirjoittaa pysyvästi, sen data voi törmätä muiden testien tai
aiemman, kesken jääneen ajon dataan. Yksinkertainen ratkaisu on
yksilöllinen tunnus: samanaikaisuustesti luo tuotteen satunnaisella
SKU:lla eikä siivoa jälkiään lainkaan.

```{.python tiedosto="esimerkit/testit/test_samanaikaisuus.py" osa="samanaikaisuus"}
```

Testi on samalla tärkeä integraatiotesti: ehdollinen `UPDATE … WHERE
saldo >= :m` on atominen, joten kahdeksasta yrityksestä onnistuu tasan
kolme. Jos tallennus lukisi saldon ensin ja päivittäisi sen sitten
erillisellä lauseella, testi paljastaisi ylivarauksen, jota mikään
väärennös ei näytä.

## Deterministinen testidata

Satunnaiset tunnukset ovat eristystä varten. Itse testidatan pitää olla
determinististä: sama testi tekee joka kerta saman asian, ja epäonnistunut
testi voidaan toistaa. Pieni rakentajafunktio pitää datan lyhyenä ja
näyttää testissä vain olennaisen:

```{.python tiedosto="esimerkit/testiapu/data.py" osa="rakentajat"}
```

`tuote(saldo=0)` kertoo lukijalle, että testissä merkitsee saldo eikä
nimi. Kun tietomalliin lisätään kenttä, oletusarvo lisätään yhteen
paikkaan eikä sataan testiin. Sama malli tunnetaan nimillä *test data
builder* ja *object mother*.

Vältä tuotantodatan kopioita testidatana. Ne ovat suuria, hitaita,
sisältävät usein henkilötietoja eivätkä kerro, mitä testi tarkistaa.
Jos tuotannon datan muotoja pitää kokeilla, tee niistä pieni
anonymisoitu otos, joka on versionhallinnassa.

## Aika testidatassa

Aikaleimat ovat testidatan yleisin epävakauden lähde: testi, joka
olettaa "nyt" olevan tietty päivä tai että kaksi peräkkäistä lausetta
saavat eri aikaleiman, epäonnistuu satunnaisesti. Varastopalvelu
järjestää varaukset tunnuksen eikä aikaleiman mukaan, ja testit
tarkistavat aikaleimasta vain sen, että aikavyöhyke on mukana. Kun
testattava logiikka riippuu ajasta, anna aika parametrina tai kellona,
jonka testi voi asettaa.

## Käytännössä

- Luo testiskeema samoilla migraatioilla kuin tuotanto.
- Käytä oletuksena transaktion peruutusta; siirry tyhjennykseen tai
  omaan kantaan vain, kun testattava koodi tekee omat transaktionsa.
- Anna pysyvästi kirjoittaville testeille yksilölliset tunnukset, jolloin
  ne eivät tarvitse siivousta eivätkä törmää rinnakkaisiin ajoihin.
- Rakenna testidata pienillä rakentajilla, jotka näyttävät vain
  testin kannalta olennaisen.
- Älä anna testin riippua kellonajasta tai toisen testin datasta.

## Itsearviointi

- Osaat perustella, miksi testiskeema luodaan tuotannon migraatioilla.
- Osaat valita peruutuksen, tyhjennyksen ja pohjasta kopioidun kannan
  välillä ja kertoa kunkin rajoitukset.
- Osaat kirjoittaa samanaikaisuustestin, joka käyttää oikeita
  transaktioita ja pysyy erillään muista testeistä.
- Osaat kirjoittaa testidatan rakentajan ja selittää, miksi data on
  determinististä mutta tunnukset satunnaisia.
