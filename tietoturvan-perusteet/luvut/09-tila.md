# Kilpailutilanteet ja asetukset

Tämän luvun virheet eivät näy, kun koodia lukee rivi kerrallaan. Ne
syntyvät ajasta (kaksi asiaa tapahtuu samaan aikaan) tai ympäristöstä
(ohjelma ajetaan asetuksilla, joita kukaan ei tarkistanut).

## TOCTOU: tarkistuksen ja käytön väli

**TOCTOU** (*time of check to time of use*) on kilpailutilanne, jossa
ohjelma tarkistaa ehdon ja toimii sen perusteella, mutta ehto ehtii
muuttua välissä. Klassinen esimerkki on tiedoston kirjoittaminen
jaettuun hakemistoon, kuten `/tmp`:

```{.python tiedosto="esimerkit/09-toctou.py" osa="haavoittuva"}
```

Tarkistuksen ja kirjoituksen välissä toinen käyttäjä luo samannimisen
symbolisen linkin, joka osoittaa uhrin tärkeään tiedostoon.
Kirjoitus seuraa linkkiä ja korvaa kohteen. Testissä väliin ehtiminen
on tehty varmaksi kutsumalla hyökkääjän funktiota; todellisuudessa
hyökkääjä yrittää toistuvasti, kunnes ajoitus osuu.

Korjaus on tehdä tarkistus ja käyttö **yhtenä atomisena
operaationa**. Käyttöjärjestelmän `O_EXCL` luo tiedoston vain, jos
nimeä ei ole olemassa, ja `O_NOFOLLOW` kieltäytyy seuraamasta
symbolista linkkiä:

```{.python tiedosto="esimerkit/09-toctou.py" osa="korjattu"}
```

```{.tuloste tiedosto="esimerkit/09-toctou.odotettu"}
```

Väliaikaistiedostot kannattaa luoda `tempfile`-modulilla, joka tekee
tämän oikein ja antaa oikeudet vain omistajalle. Sama periaate koskee
kaikkea: avaa ja käsittele tiedostokahvaa, älä nimeä, jonka kohde voi
vaihtua.

## Kilpailutilanne liiketoimintalogiikassa

TOCTOU ei rajoitu tiedostoihin. Kaksi samanaikaista nostopyyntöä
lukevat saman saldon ennen kuin kumpikaan kirjoittaa, ja molemmat
läpäisevät tarkistuksen:

```{.python tiedosto="esimerkit/09-nosto.py" osa="haavoittuva"}
```

Korjaus siirtää ehdon samaan lauseeseen muutoksen kanssa. Tietokanta
suorittaa ehdollisen päivityksen atomisesti, ja muutettujen rivien
määrä kertoo, onnistuiko nosto:

```{.python tiedosto="esimerkit/09-nosto.py" osa="korjattu"}
```

```{.tuloste tiedosto="esimerkit/09-nosto.odotettu"}
```

Sama virhe esiintyy alennuskoodeissa (sama kertakäyttökoodi kahdessa
rinnakkaisessa tilauksessa), varastosaldoissa ja äänestyksissä.
Hyökkääjä laukaisee kymmeniä pyyntöjä samanaikaisesti, jolloin
rinnakkaisuus on varmaa eikä harvinaista. Muita korjaustapoja ovat
rivilukko (`SELECT … FOR UPDATE`), riittävä eristystaso ja
yksilöivä rajoite (*unique constraint*), joka estää saman koodin
toisen käytön (taito *SQL ja relaatiotietokannat*, transaktiot).

## Väärät oletusasetukset

Moni tietomurto ei hyödynnä koodin virhettä lainkaan vaan asetusta:
oletussalasana, julkinen tallennussäilö, debug-tila tuotannossa tai
ylläpitoliittymä internetissä. Asetukset kannattaa suunnitella niin,
että **oletusarvot ovat turvallisia** ja vaarallinen valinta vaatii
nimenomaisen muutoksen:

```{.python tiedosto="esimerkit/09-asetukset.py" osa="asetukset"}
```

Lisäksi asetukset tarkastetaan automaattisesti ennen käynnistystä. Jos
tuotantoon on menossa kehitysympäristön asetuksia, käynnistys
pysähtyy:

```{.python tiedosto="esimerkit/09-asetukset.py" osa="tarkastus"}
```

```{.tuloste tiedosto="esimerkit/09-asetukset.odotettu"}
```

| Asetus | Miksi vaarallinen |
|--------|-------------------|
| debug tuotannossa | pinojäljet, asetukset ja joskus etäkonsoli näkyvät hyökkääjälle |
| TLS-tarkistus pois | välimieshyökkäys mahdollinen, ks. luku *Kryptografia käyttäjän näkökulmasta* |
| CORS `*` tunnisteiden kanssa | mikä tahansa sivusto voi lukea vastaukset |
| `0.0.0.0` ylläpitoliittymälle | kuuntelee kaikissa verkoissa, myös internetissä |
| oletustunnukset | löytyvät valmistajan ohjeista ja hyökkäyslistoista |
| liian laajat pilvioikeudet | yksi vuotanut avain avaa kaiken |

## Käytännössä

- **Älä tarkista ja toimi erikseen.** Atominen operaatio, kahvan
  käyttö nimen sijaan, ehdollinen päivitys tai lukko.
- **Oleta rinnakkaisuus.** Hyökkääjä lähettää pyynnöt samanaikaisesti
  tarkoituksella. Jokainen "kerran"-sääntö (kertakäyttökoodi, yksi
  ääni, saldo) toteutetaan tietokannan rajoitteella tai atomisella
  päivityksellä.
- **Turvalliset oletukset.** Asetustiedosto, jossa ei ole mitään, on
  turvallinen; vaarallinen valinta näkyy koodikatselmoinnissa.
- **Tarkasta asetukset koneellisesti.** Käynnistyksen tarkistukset,
  infrastruktuuri koodina ja sen staattinen analyysi löytävät virheet
  ennen tuotantoa.
- **Kovenna ympäristö.** Poista tarpeettomat palvelut, vaihda kaikki
  oletustunnukset ja seuraa valmistajan koventamisohjeita (esimerkiksi
  CIS Benchmarks).

## Itsearviointi

- Osaat tunnistaa TOCTOU-kilpailutilanteen tiedostojärjestelmässä ja
  korjata sen atomisella operaatiolla.
- Osaat korjata rinnakkaisten pyyntöjen kilpailutilanteen ehdollisella
  päivityksellä tai tietokannan rajoitteella.
- Osaat suunnitella asetukset, joiden oletusarvot ovat turvallisia.
- Osaat kirjoittaa käynnistyksen yhteydessä ajettavan asetusten
  tarkastuksen.
