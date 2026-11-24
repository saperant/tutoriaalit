# Viiveen kompensointi

Interpoloinnin takia ampuja näkee vastustajan siellä, missä tämä oli
oman yhteyden viiveen ja puskurin verran sitten. Kun laukaus saapuu
palvelimelle, kohde on jo liikkunut. Jos palvelin tarkistaa osuman
kohteen nykyiseen paikkaan, täydellinen tähtäys menee ohi, ja pelaajan
on opeteltava tähtäämään kohteen eteen viiveen verran: huono kokemus ja
riippuvainen omasta yhteydestä.

## Takaisinkelaus

*Viiveen kompensointi* (lag compensation) kelaa kohteet ampujan
näkemään hetkeen. Palvelin pitää lyhyen historian kaikkien osuma-alueiden
sijainneista, ja laukauksen mukana asiakas kertoo, minkä hetken
maailmaa se näytti (palvelimen tikki ja interpoloinnin kohta).

```{.cpp tiedosto="esimerkit/08-takaisinkelaus.cpp" osa="historia"}
```

```{.cpp tiedosto="esimerkit/08-takaisinkelaus.cpp" osa="laukaus"}
```

```{.tuloste tiedosto="esimerkit/08-takaisinkelaus.odotettu"}
```

Ilman kelausta täydellisestä tähtäyksestä osuu vain 12–22 %.
Kelauksella osuu kaikki, kunhan viive on hyväksytyn rajan sisällä.
250 ms:n yhteydellä kelaus rajataan, eikä kompensointi enää auta:
liian suuri viive ei saa antaa etua.

## Reiluus: ammuttiin seinän takana

Kompensoinnilla on hinta, jonka maksaa kohde. Viimeinen sarake kertoo,
kuinka usein osuma rekisteröityi, vaikka kohde oli palvelimen
nykyhetkessä jo seinän takana. Kohteen näkökulmasta hän ehti suojaan
ja kuoli silti. Mitä suurempi ampujan viive, sitä pidemmälle kohde
ehtii, ja siksi kelaukselle asetetaan yläraja (tyypillisesti
200–400 ms). Raja on suunnittelupäätös: kenen kokemus painaa
enemmän, ampujan vai kohteen.

Kompensoinnin muotoja:

- **Ampujan etu** (favor the shooter): kelataan ampujan näkemään
  hetkeen. Yleisin malli toimintapeleissä.
- **Palvelimen nykyhetki**: ei kelausta, ammuksilla on lentoaika ja
  pelaaja oppii johtamaan tähtäystä. Sopii hitaille ammuksille.
- **Kohteen suoja**: osuma hylätään, jos kohde on ollut suojassa
  kauemmin kuin raja. Kompromissi.

## Käytännössä

- **Historia tikeittäin, kelaus osumantarkistusta varten.** Kelaa vain
  osuma-alueet, ei koko pelitilaa, ja palauta ne heti tarkistuksen
  jälkeen.
- **Asiakas kertoo näyttöhetken; palvelin rajaa sen.** Raja suojaa sekä
  huonoja yhteyksiä että huijareita, jotka väittävät nähneensä
  kauempaa menneisyyttä.
- **Interpoloi historiasta samalla tavalla kuin asiakas.** Muuten
  kelattu paikka poikkeaa siitä, mitä ampuja näki.
- **Tee rajat näkyviksi.** Kerro pelaajille, millä pingillä
  kompensointi lakkaa, ja ohjaa korkean viiveen pelaajat lähemmille
  palvelimille.
- **Hinta:** historian muisti ja kelauksen laskenta joka laukaukselle;
  reiluusongelmat, joita ei voi poistaa, vain tasapainottaa.

## Itsearviointi

- Osaat selittää, miksi ilman kompensointia täydellinen tähtäys menee
  ohi.
- Osaat toteuttaa palvelimen historian ja osumantarkistuksen
  takaisinkelauksella.
- Osaat perustella kelauksen ylärajan ja sen vaikutuksen ampujaan ja
  kohteeseen.
