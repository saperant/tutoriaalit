# Auditointi ja havainnointi

Kun murto tapahtuu, ensimmäiset kysymykset ovat: mitä hyökkääjä teki,
mihin se pääsi ja milloin se alkoi. Vastaukset löytyvät vain
lokeista, jotka on kirjoitettu ennen murtoa, joita hyökkääjä ei ole
voinut muuttaa ja joista ei ole vuotanut lisää salaisuuksia.

## Mitä kirjataan

Auditointitapahtuma vastaa kysymyksiin kuka, mitä, mille, milloin,
minkä pyynnön osana ja millä tuloksella:

```{.java tiedosto="esimerkit/havainnointi/src/main/java/fi/tutoriaalit/palveluturva/havainnointi/Tapahtuma.java" osa="tapahtuma"}
```

Kirjataan ainakin:

- **todennus ja sen epäonnistuminen**, myös hylätyt TLS-kättelyt
- **valtuutuspäätökset**, erityisesti estot
- **muutokset ja arkaluonteisen tiedon luku**: kenen tiedot luettiin
- **hallinnolliset toimet:** oikeuksien, käytäntöjen ja avainten
  muutokset
- **välittäjäketju:** palvelu ja käyttäjä, jonka puolesta se toimi
  (`act`-väite, luku 6)

**Korrelaatiotunniste** kulkee pyynnön mukana palvelusta toiseen
(W3C Trace Context, `traceparent`), jotta yhden pyynnön tapahtumat
voidaan koota eri palvelujen lokeista.

## Mitä ei kirjata

Loki on usein laajemmin luettavissa kuin tietokanta, ja sitä
säilytetään pitkään. Tokenit, salasanat, avaimet ja täydet
korttinumerot eivät kuulu sinne:

```{.java tiedosto="esimerkit/havainnointi/src/main/java/fi/tutoriaalit/palveluturva/havainnointi/Peittaja.java" osa="peita"}
```

```{.java tiedosto="esimerkit/havainnointi/src/test/java/fi/tutoriaalit/palveluturva/havainnointi/HavainnointiTest.java" osa="peitaTesti"}
```

Peittäminen kentän nimen perusteella kattaa tavalliset tapaukset,
mutta vapaa teksti vuotaa silti: virheilmoitukseen kopioitu
`Authorization`-otsake tai pyynnön runko. Siksi arvoista etsitään myös
tunnettuja muotoja. Parasta on, ettei arkaluonteista tietoa koskaan
välitetä lokikutsulle.

## Muuttumaton loki

Taidossa *Tietoturvan perusteet* auditointiloki ketjutettiin
tiivisteillä: jokainen rivi sisältää edellisen tiivisteen, joten
muutos keskellä katkaisee ketjun. Ketju ei kuitenkaan suojaa siltä,
joka pääsee kirjoittamaan lokiin: hän voi laskea ketjun uudelleen.
Palvelukokonaisuudessa ketjun pää allekirjoitetaan säännöllisesti
avaimella, jota lokia kirjoittava palvelu ei omista, ja
tarkistuspisteet tallennetaan muualle:

```{.java tiedosto="esimerkit/havainnointi/src/main/java/fi/tutoriaalit/palveluturva/havainnointi/Auditointiloki.java" osa="tarkistuspiste"}
```

```{.java tiedosto="esimerkit/havainnointi/src/main/java/fi/tutoriaalit/palveluturva/havainnointi/Auditointiloki.java" osa="kirjaa"}
```

Tarkistus laskee ketjun alusta ja vertaa sitä allekirjoitettuihin
tarkistuspisteisiin:

```{.java tiedosto="esimerkit/havainnointi/src/main/java/fi/tutoriaalit/palveluturva/havainnointi/Auditointiloki.java" osa="tarkista"}
```

```{.java tiedosto="esimerkit/havainnointi/src/test/java/fi/tutoriaalit/palveluturva/havainnointi/HavainnointiTest.java" osa="lokiTesti"}
```

Pilvessä sama saadaan valmiina: auditointilokit kirjoitetaan
erilliselle tilille, tallennuksen muuttumattomuuslukolla (*object
lock*, WORM), ja palvelu allekirjoittaa lokitiedostojen tiivisteet
(AWS CloudTrailin *log file validation*).

## Lokit erilliseen paikkaan

Hyökkääjä, joka saa ylläpito-oikeudet, poistaa ensimmäiseksi jäljet.
Auditointilokit lähetetään siksi heti erilliseen järjestelmään, johon
tuotannon ylläpitäjillä on vain kirjoitusoikeus. Lokien poisto ja
auditoinnin pysäytys estetään organisaatiotasolla (luku 9).

## Käytännössä

- **Rakenteiset tapahtumat.** JSON-rivit, joissa on aina samat kentät,
  ovat haettavia; vapaa teksti ei ole.
- **Korrelaatiotunniste kaikkialle.** Ilman sitä yhden pyynnön
  tapahtumien kokoaminen kymmenestä palvelusta on arvailua.
- **Peitä ennen kirjausta.** Lokiin päätynyttä salaisuutta ei saa
  pois kaikista kopioista; se on kierrettävä.
- **Säilytys ja tietosuoja.** Auditointilokit sisältävät
  henkilötietoja. Säilytysaika perustellaan, ja pääsy rajataan.
- **Kellot synkronissa.** NTP kaikkialla; muuten aikajana on väärä.

## Itsearviointi

- Osaat luetella, mitä auditointitapahtumaan kirjataan ja mitä ei.
- Osaat peittää salaisuudet ja korttinumerot lokista ja kertoa
  peittämisen rajat.
- Osaat selittää, miksi tiivisteketju tarvitsee allekirjoitetut,
  muualle tallennetut tarkistuspisteet.
- Osaat suunnitella lokien tallennuksen niin, ettei tuotannon
  ylläpitäjä voi poistaa niitä.
