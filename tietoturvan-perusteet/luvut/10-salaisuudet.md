# Salaisuudet ja tunnistetietojen vuodot

Salasanat, API-avaimet, tietokantatunnukset ja yksityiset avaimet ovat
**salaisuuksia**. Vuotanut salaisuus ohittaa kaikki muut suojaukset:
hyökkääjä ei murtaudu, hän kirjautuu. Tunnistetietojen vuodot ja
varastetut tunnukset ovat vuodesta toiseen tietomurtojen yleisimpiä
alkupisteitä. Tämä luku käsittelee kolmea vuotokanavaa: koodi,
asetukset ja lokit. Salaisuuksien hallinta kehitysprosessissa ja
tuotannossa jatkuu taidoissa *Tietoturva kehitystyössä* ja
*Palveluarkkitehtuurin tietoturva*.

## Salaisuudet eivät kuulu koodiin

Versionhallintaan päätynyt salaisuus on vuotanut, vaikka se poistettaisiin
seuraavassa muutoksessa: historia säilyttää sen, ja jokainen kopio
repositoriosta sisältää sen. Julkisista repositorioista avaimia
haravoidaan automaattisesti minuuteissa. Ainoa korjaus on **vaihtaa
salaisuus**; historian siivous ei riitä.

Salaisuuksia voi etsiä koodista automaattisesti. Etsintä perustuu
kahteen keinoon: tunnettuihin muotoihin (esimerkiksi AWS-avaimet
alkavat `AKIA`) ja **entropiaan**, joka kertoo, kuinka satunnaiselta
merkkijono näyttää:

```{.python tiedosto="esimerkit/10-skannaus.py" osa="saannot"}
```

```{.tuloste tiedosto="esimerkit/10-skannaus.odotettu"}
```

Tavallinen teksti on noin 3–4 bittiä merkkiä kohden, satunnainen avain
lähempänä merkkijoukon maksimia (base64: 6 bittiä). Valmiit työkalut,
kuten gitleaks ja trufflehog, sisältävät satoja sääntöjä ja ajetaan
sekä commit-koukussa että CI:ssä. Ne eivät löydä kaikkea, joten
ensisijainen suojaus on tapa, jossa salaisuudet eivät koskaan ole
koodissa.

## Salaisuudet ajoympäristöstä

Sovellus saa salaisuudet ajoympäristöstä: ympäristömuuttujista,
salaisuusvarastosta (esimerkiksi HashiCorp Vault, pilvipalvelujen
KMS) tai tiedostoista, joihin vain palvelulla on lukuoikeus. Kaksi
yksityiskohtaa estää yleisiä vuotoja:

```{.python tiedosto="esimerkit/10-salaisuus.py" osa="salaisuus"}
```

```{.tuloste tiedosto="esimerkit/10-salaisuus.odotettu"}
```

- **Ei oletusarvoa.** `os.environ.get("SALASANA", "kehitys123")`
  toimii huomaamatta tuotannossa kehityssalasanalla, jos muuttuja
  unohtuu. Puuttuva salaisuus pysäyttää käynnistyksen.
- **Ei näkymistä tulosteissa.** Kääreluokka, jonka `repr` ei paljasta
  arvoa, estää salaisuuden päätymisen lokeihin, virheilmoituksiin ja
  debug-tulosteisiin, kun asetusolio tulostetaan kokonaisena.

Ympäristömuuttujat eivät ole täydellinen ratkaisu: ne periytyvät
lapsiprosesseille, näkyvät saman käyttäjän prosesseille
(`/proc/<pid>/environ`) ja päätyvät joskus virheraportteihin.
Tuotannossa salaisuusvarasto, joka antaa lyhytikäisiä tunnuksia, on
parempi.

## Lokit vuotokanavana

Lokit kopioidaan moniin paikkoihin: lokipalveluun, varmuuskopioihin,
tukihenkilöiden koneille. Niihin päätyy salaisuuksia huomaamatta:
URL-osoitteen kyselyparametrit, otsakkeet, virheilmoitukset, joissa on
koko pyyntö. Ensisijainen suojaus on olla lokittamatta niitä, mutta
peittävä suodatin on hyvä viimeinen puolustuslinja:

```{.python tiedosto="esimerkit/10-lokit.py" osa="suodatin"}
```

```{.tuloste tiedosto="esimerkit/10-lokit.odotettu"}
```

Ensimmäinen rivi näyttää, miksi salasanaa ei koskaan lähetetä
URL-osoitteessa: osoite tallentuu palvelimen, välityspalvelinten ja
selaimen historiaan. Henkilötiedot, kuten henkilötunnukset ja
korttinumerot, ovat lokeissa samanlainen ongelma, ja niihin liittyy
lisäksi tietosuoja-asetuksen vaatimuksia (luku *Lainsäädäntö ja
etiikka*).

## Käytännössä

- **Ei salaisuuksia versionhallintaan.** `.env` `.gitignore`-tiedostoon,
  esimerkkitiedosto ilman arvoja (`.env.example`) ja skannaus
  commit-koukussa ja CI:ssä.
- **Vuotanut salaisuus vaihdetaan heti.** Historian siivous on
  lisätoimi, ei korjaus.
- **Lyhytikäiset ja rajatut tunnukset.** Tunnus, joka vanhenee tunnissa
  ja toimii vain yhteen resurssiin, on vuotaessaan pieni vahinko.
- **Jokaisella palvelulla omat tunnukset.** Yhteinen salasana estää
  sekä vuodon rajaamisen että selvittämisen.
- **Kääri salaisuudet tyyppiin.** Tyyppi, joka ei tulostu, estää
  vahinkovuodot paremmin kuin ohje "älä tulosta salasanaa".
- **Lokita tapahtumat, älä dataa.** "Kirjautuminen epäonnistui
  käyttäjälle aino", ei koko pyyntöä.

## Itsearviointi

- Osaat kertoa, miksi versionhallintaan päätynyt salaisuus on
  vaihdettava, ja estää vuodot ennalta.
- Osaat lukea salaisuudet ajoympäristöstä ilman oletusarvoja ja estää
  niiden näkymisen tulosteissa.
- Osaat kirjoittaa lokisuodattimen, joka peittää tunnistetiedot.
- Osaat selittää, miten salaisuuksien skannaus toimii ja mitkä ovat
  sen rajat.
