# Rajatut kontekstit ja palvelujen jako

Vaikein palveluarkkitehtuurin kysymys ei ole tekninen vaan se, mihin
rajat vedetään. Huono raja pakottaa kaksi palvelua muuttumaan aina
yhdessä, ja silloin niiden erottaminen tuotti vain verkkokutsuja.
Domain-driven design (DDD, Eric Evans 2003) antaa tähän käsitteet,
joita kutsutaan *strategiseksi suunnitteluksi*.

## Sama sana, eri merkitys

Verkkokaupassa "tuote" tarkoittaa eri asioita eri osissa:

| Konteksti | Tuote on | Tärkeät tiedot |
|-----------|----------|----------------|
| Myynti | myytävä nimike | nimi, hinta, kuvaus, kuvat |
| Varasto | fyysinen tavara | nimikekoodi, hyllypaikka, saldo, paino |
| Toimitus | paketti | mitat, paino, vaarallisuusluokka |
| Laskutus | laskurivi | hinta, ALV-kanta, tilikoodi |

Yksi yhteinen `Tuote`-luokka kaikille kasvaa kentistä, joista kukin
käyttäjä tarvitsee pienen osan, ja jokainen muutos koskettaa kaikkia.
DDD:n vastaus on *rajattu konteksti* (*bounded context*): alue, jonka
sisällä jokaisella käsitteellä on yksi täsmällinen merkitys ja oma
mallinsa. Kontekstin sisällä puhutaan sen *yhteistä kieltä*
(*ubiquitous language*): samat sanat koodissa, tietokannassa ja
keskusteluissa liiketoiminnan kanssa.

Rajattu konteksti on luonteva palvelun tai moduulin raja. Kontekstin
sisällä muutokset ovat tiheitä ja tiedot kytkeytyvät tiukasti;
kontekstien välillä kulkee vähän ja harkittua tietoa.

## Rajojen löytäminen

Kolme kysymystä auttaa:

1. **Liiketoimintakyvykkyys.** Mitä organisaatio tekee: myy,
   varastoi, toimittaa, laskuttaa. Kyvykkyydet muuttuvat hitaammin kuin
   prosessit ja organisaatiokaaviot.
2. **Kielen raja.** Missä sama sana alkaa tarkoittaa eri asiaa?
   Siinä on todennäköisesti kontekstin raja.
3. **Muutoksen yhteisyys.** Mitkä asiat muuttuvat yhdessä? Ne kuuluvat
   samaan kontekstiin, vaikka näyttäisivät erillisiltä.

*Event storming* on työpajamenetelmä, jossa liiketoiminnan ja
kehittäjien kanssa kirjataan seinälle järjestelmän tapahtumat
("Tilaus tehty", "Maksu hylätty") aikajärjestyksessä. Tapahtumien
ryhmät ja niiden väliset siirtymät paljastavat kontekstit ja
aggregaatit.

Huono jakoperuste on tekninen kerros (käyttöliittymäpalvelu,
logiikkapalvelu, tietokantapalvelu) tai yksittäinen taulu
(*entity service*: asiakaspalvelu, tuotepalvelu, tilauspalvelu, joista
jokainen vain lukee ja kirjoittaa yhtä taulua). Kumpikin johtaa siihen,
että jokainen ominaisuus vaatii muutoksen ja kutsuketjun usean palvelun
läpi.

## Aggregaatti on johdonmukaisuuden raja

*Aggregaatti* on joukko olioita, jotka muuttuvat yhdessä ja joiden
säännöt tarkistetaan yhdessä transaktiossa: tilaus riveineen, ei
tilaus ja asiakas. Taustapalveluissa aggregaatti oli tallennuksen
yksikkö. Palveluarkkitehtuurissa se on myös rajan sääntö: yksi
transaktio muuttaa yhtä aggregaattia, ja aggregaattien välinen
johdonmukaisuus saavutetaan tapahtumilla. Kun tämä sääntö on voimassa
jo monoliitissa, aggregaatit voi jakaa palveluihin ilman, että
transaktioita tarvitsee purkaa.

## Kontekstikartta

Kontekstit eivät ole irrallisia; ne tarvitsevat toistensa tietoja.
*Kontekstikartta* kuvaa, miten ne liittyvät ja kuka mukautuu kehen:

| Suhde | Merkitys | Esimerkki |
|-------|----------|-----------|
| Asiakas–toimittaja | alavirran tarpeet vaikuttavat ylävirran rajapintaan | myynti ja varasto |
| Mukautuja (*conformist*) | alavirta käyttää ylävirran mallia sellaisenaan | raportointi lukee myynnin tapahtumia |
| Korruption estokerros | alavirta kääntää ylävirran mallin omakseen | uusi järjestelmä vanhan päällä (luku 12) |
| Avoin palvelu ja julkaistu kieli | ylävirta tarjoaa vakaan, dokumentoidun rajapinnan | myynnin tapahtumat |
| Jaettu ydin | pieni yhteinen malli, jota molemmat muuttavat sopien | rahamäärä ja valuutta |
| Erilliset tiet | ei integraatiota | eri liiketoiminta-alueet |

Kartta on nimensä mukaisesti kuva. Esimerkkikaupan kontekstit ja
niiden suhteet:

```{.dot otsikko="Verkkokaupan kontekstikartta. Nuoli kulkee ylävirrasta alavirtaan eli siihen suuntaan, johon malli ja tieto virtaavat. Nuolen teksti kertoo, miten alavirta suhtautuu ylävirran malliin."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.9;
  myynti [label="Myynti\n(avoin palvelu,\njulkaistu kieli)", penwidth=1.6];
  varasto [label="Varasto"]; toimitus [label="Toimitus"];
  laskutus [label="Laskutus"]; raportointi [label="Raportointi"];
  vanha [label="Vanha\nasiakasrekisteri", style="rounded,dashed"];
  asiakkaat [label="Asiakkuudet\n(uusi)"];
  varasto -> myynti [label="asiakas–toimittaja"];
  myynti -> toimitus [label="tapahtumat"];
  myynti -> laskutus [label="tapahtumat;\njaettu ydin: raha"];
  myynti -> raportointi [label="mukautuja"];
  vanha -> asiakkaat [label="korruption\nestokerros"];
}
```

Myynnin tapahtuma on esimerkki *julkaistusta kielestä*. Se kertoo vain
sen, mitä tilauksesta on tarpeen tietää muualla, ja sen muoto on
sopimus:

```{.java tiedosto="esimerkit/modulaarinen/src/main/java/fi/tutoriaalit/palvelut/kauppa/myynti/TilausTehty.java"}
```

Uuden järjestelmän asiakasmalli on taas esimerkki omasta mallista,
joka on suojattu vanhan järjestelmän käsitteiltä korruption
estokerroksella. Mallissa ei ole vanhan järjestelmän kirjainkoodeja
eikä päivämäärämerkkijonoja:

```{.java tiedosto="esimerkit/uudistus/src/main/java/fi/tutoriaalit/palvelut/uudistus/uusi/Asiakas.java"}
```

## Tiedon omistus

Jokainen tieto on yhden kontekstin omaa: se on ainoa, joka saa muuttaa
sitä. Muut saavat tiedon kolmella tavalla:

1. **Kysymällä** omistajan rajapinnasta, kun tarvitaan tuore arvo
   (saldo ennen tilausta). Hinta: synkroninen riippuvuus.
2. **Kopioimalla tapahtumista** oman näkymänsä, kun riittää lähes tuore
   arvo (laskutus tallentaa tilauksen tiedot). Hinta: kopio voi olla
   hetken vanha, ja muodon muutokset on hallittava.
3. **Viittaamalla** tunnisteella, kun tietoa ei tarvita lainkaan
   (toimitus tietää tilauksen numeron, ei hintaa).

Kaikkien palvelujen yhteinen tietokanta näyttää helpolta tavalta
jakaa tietoa, mutta se kumoaa rajat: skeeman muutos rikkoo palveluja,
joita muuttaja ei tunne, eikä yksikään palvelu voi julkaista
tietomallinsa muutosta itsenäisesti (luku 7).

## Käytännössä

- **Jaa kyvykkyyksien ja kielen mukaan, ei kerrosten tai taulujen.**
  Jos jokainen uusi ominaisuus koskettaa kolmea palvelua, rajat ovat
  väärässä paikassa.
- **Yksi transaktio, yksi aggregaatti.** Aggregaattien välillä
  johdonmukaisuus tapahtumilla; silloin jako palveluihin ei vaadi
  hajautettuja transaktioita.
- **Piirrä kontekstikartta.** Se kertoo, missä tarvitaan
  korruption estokerros ja mitkä rajapinnat ovat julkista kieltä, jota
  ei saa rikkoa.
- **Kopioi tieto tietoisesti.** Tapahtumista koottu paikallinen kopio
  poistaa synkronisen riippuvuuden, mutta sen viive ja muodon
  muutokset on hyväksyttävä.
- **Hinnat:** väärä raja on kallein virhe, koska se vaatii datan
  siirtoa ja sopimusten muutoksia usean tiimin yli.

## Itsearviointi

- Osaat selittää rajatun kontekstin ja yhteisen kielen ja tunnistaa
  kontekstin rajan käsitteiden merkityksen muuttumisesta.
- Osaat perustella, miksi jako kerroksiin tai tauluihin tuottaa
  huonoja palveluja.
- Osaat kuvata kontekstikartan suhteet ja valita, milloin tarvitaan
  korruption estokerros.
- Osaat valita, haetaanko toisen kontekstin tieto kysymällä,
  kopioimalla tapahtumista vai pelkällä viittauksella.
