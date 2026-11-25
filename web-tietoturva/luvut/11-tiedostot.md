# Tiedostot, uudelleenohjaukset ja turvaotsakkeet

Tämä luku kokoaa kolme aihetta, jotka ovat yksinään pieniä mutta
yhdessä usein murron alku: käyttäjien lataamat tiedostot, avoimet
uudelleenohjaukset ja HTTP-vastausten turvaotsakkeet.

## Tiedostojen lataus

Ladattu tiedosto on syöte, joka tallennetaan ja jaetaan muille.
Haavoittuva toteutus luottaa käyttäjän antamaan nimeen ja päättelee
tyypin nimestä:

```{.typescript tiedosto="esimerkit/src/11-tiedostot/lataus.ts" osa="haavoittuva"}
```

Siinä on kaksi aukkoa. Nimi `../ohitus.png` kirjoittaa hakemiston
ulkopuolelle (polun ohitus), ja `kuva.html` jaetaan HTML-sivuna
sovelluksen omasta alkuperästä. Sen skripti toimii kuin tallennettu
XSS (luku 3).

Korjattu toteutus:

1. **tunnistaa tyypin sisällöstä** sallittujen luettelosta, ei nimestä
   eikä asiakkaan ilmoittamasta tyypistä,
2. **rajoittaa koon**,
3. **antaa tiedostolle palvelimen nimen** (UUID) ja tallentaa sen
   jakelupolun ulkopuolelle,
4. **jakaa tiedoston turvallisesti**: oikea `Content-Type`,
   `nosniff` (selain ei arvaa tyyppiä sisällöstä),
   `Content-Disposition: attachment` ja CSP:n `sandbox`.

```{.typescript tiedosto="esimerkit/src/11-tiedostot/lataus.ts" osa="tunnistus"}
```

```{.typescript tiedosto="esimerkit/src/11-tiedostot/lataus.ts" osa="korjattu"}
```

```{.typescript tiedosto="esimerkit/src/11-tiedostot/tiedostot.test.ts" osa="lataus"}
```

Näytösajossa kolme viimeistä riviä ovat otsakkeet, joilla ladattu kuva
jaetaan takaisin. Korjattu versio vastaa skriptin lataukseen tilalla
415 (*unsupported media type*):

```{.tuloste tiedosto="esimerkit/naytos/11-lataus.odotettu"}
```

Parhaassa tapauksessa käyttäjien tiedostot jaetaan **eri
verkkotunnuksesta** (esimerkiksi `kayttajasisalto.example`), jolloin
selain eristää ne sovelluksesta kokonaan. Kuvat voidaan lisäksi
käsitellä uudelleen (pienentää ja tallentaa uutena tiedostona), mikä
poistaa upotetut hyötykuormat ja metatiedot (sijainti). Suurissa
palveluissa tiedostot tarkistetaan myös haittaohjelmien varalta.

## Avoimet uudelleenohjaukset

Parametri `?seuraava=` palauttaa käyttäjän kirjautumisen tai
uloskirjautumisen jälkeen oikealle sivulle. Jos se hyväksyy minkä
tahansa osoitteen, oikean sivuston linkki ohjaa kalastelusivulle:
linkki näyttää luotettavalta, koska se alkaa oikealla
verkkotunnuksella. OAuth-virroissa avoin uudelleenohjaus voi lisäksi
vuotaa valtuutuskoodin (luku 8).

```{.typescript tiedosto="esimerkit/src/11-tiedostot/ohjaus.ts" osa="ohjaus"}
```

```{.typescript tiedosto="esimerkit/src/11-tiedostot/tiedostot.test.ts" osa="ohjaus-testi"}
```

```{.tuloste tiedosto="esimerkit/naytos/11-ohjaus.odotettu"}
```

Selaimet tulkitsevat `//pankki-kirjaudu.example` ja
`/\pankki-kirjaudu.example` toiseksi palvelimeksi, joten pelkkä
"alkaa vinoviivalla" ei riitä. Turvallisin on tallentaa paluukohde
istuntoon tai käyttää tunnisteita (`?seuraava=tilit`) osoitteiden
sijaan.

## Turvaotsakkeet

```{.typescript tiedosto="esimerkit/src/11-tiedostot/ohjaus.ts" osa="otsakkeet"}
```

| Otsake | Torjuu |
|--------|--------|
| `Strict-Transport-Security` | HTTPS:n ohituksen: selain ei yritä HTTP:tä vuoteen |
| `Content-Security-Policy` | XSS:n (luku 3), clickjackingin (`frame-ancestors`), lomakkeiden lähetyksen vieraaseen osoitteeseen (`form-action`) |
| `X-Content-Type-Options: nosniff` | tyypin arvailun: teksti ei muutu skriptiksi |
| `Referrer-Policy` | osoitteiden (tokenit, polut) vuotamisen toisille sivustoille |
| `Permissions-Policy` | kameran, mikrofonin ja sijainnin käytön upotetuilta sivuilta |
| `Cross-Origin-Opener-Policy` | ikkunaviittausten kautta tehtävät hyökkäykset ja Spectre-tyyppiset vuodot |
| `Cross-Origin-Resource-Policy` | resurssien upottamisen toisille sivustoille |

Otsakkeet asetetaan yhdessä paikassa (välikerros, käänteinen
välityspalvelin tai CDN) kaikille vastauksille, ja niiden olemassaolo
testataan (luku 12). Virhesivut ovat usein se paikka, josta otsakkeet
unohtuvat. Ne eivät myöskään saa näyttää pinojälkiä tai
tietokantavirheitä: esimerkkien apukehys palauttaa sisäisestä virheestä
vain yleisen viestin ja kirjaa yksityiskohdat lokiin.

## Käytännössä

- **Tiedostot:** tyyppi sisällöstä, koko rajattu, palvelimen nimi,
  jakelu toisesta verkkotunnuksesta tai `attachment` ja `sandbox`.
- **Uudelleenohjaukset:** vain suhteelliset polut tai tunnisteet;
  testaa `//`- ja `/\`-muodot.
- **Otsakkeet keskitetysti** kaikille vastauksille, myös virheille.
  HSTS:n `preload`-lista vasta, kun kaikki aliverkkotunnukset ovat
  HTTPS:n takana.
- **Hinta:** otsakkeet ovat ilmaisia, mutta tiukka CSP ja COOP voivat
  rikkoa upotuksia ja ponnahdusikkunoita (esimerkiksi maksupalvelun
  ikkunan). Ota ne käyttöön raportointitilassa ja seuraa rikkomuksia
  ennen pakotusta.

## Itsearviointi

- Osaat toteuttaa turvallisen tiedostojen latauksen ja jakelun.
- Osaat estää avoimen uudelleenohjauksen ja tunnet sen ohitustavat.
- Osaat valita turvaotsakkeet ja kertoa, mitä kukin torjuu.
- Osaat estää sisäisten virheiden paljastumisen vastauksissa.
