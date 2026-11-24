# Asiakkaan ennustus ja täsmäytys

Jos asiakas näyttää vain palvelimen vahvistaman tilan, oma hahmo liikkuu
vasta kiertoviiveen jälkeen. 150 ms:n viive näppäimestä liikkeeseen
tuntuu siltä, että hahmo kahlaa liejussa. Ratkaisu on *asiakkaan
ennustus* (client-side prediction): asiakas simuloi oman hahmonsa heti
samalla koodilla kuin palvelin. Palvelin pysyy auktoriteettina, ja kun
sen vastaus saapuu, asiakas *täsmäyttää* (reconciliation) ennusteensa.

## Syötteet numeroituina

Liikesääntö on jaettua koodia: sama funktio ajetaan asiakkaalla ja
palvelimella.

```{.cpp tiedosto="esimerkit/06-ennustus.cpp" osa="simulaatio"}
```

Asiakas soveltaa syötteen heti, tallentaa sen kuittaamattomien jonoon
ja lähettää sen numeroituna. Pakettiin voi laittaa myös muutaman
edellisen syötteen, jolloin yksittäinen kadonnut paketti ei hukkaa
syötettä:

```{.cpp tiedosto="esimerkit/06-ennustus.cpp" osa="asiakas"}
```

Palvelin käsittelee jokaisen syötteen kerran ja järjestyksessä ja
kertoo vastauksessa viimeisimmän käsittelemänsä:

```{.cpp tiedosto="esimerkit/06-ennustus.cpp" osa="palvelin"}
```

## Täsmäytys

Palvelimen tila on vanha: se kuvaa hetkeä, jolloin syöte numero
`kasitelty` oli käsitelty. Asiakas ottaa sen pohjaksi, poistaa
kuitatut syötteet jonosta ja simuloi jäljellä olevat uudelleen. Jos
ennustus oli oikea, tulos on sama kuin asiakkaan nykyinen ennuste, eikä
mitään tapahdu.

```{.cpp tiedosto="esimerkit/06-ennustus.cpp" osa="tasmaytys"}
```

```{.tuloste tiedosto="esimerkit/06-ennustus.odotettu"}
```

Hyvällä yhteydellä ennustus ei koskaan erehdy, ja oma liike tuntuu
viiveettömältä, vaikka vahvistus saapuu 156 ms:n päästä. 5 %:n
häviöllä palvelimelta jää syötteitä saamatta, ja asiakkaan ennuste
korjataan 16 kertaa. Kun jokaisessa paketissa on kolme viimeisintä
syötettä, korjauksia ei tarvita lainkaan: kolme peräkkäistä hävikkiä on
harvinaista. Tönäisy on tapahtuma, jota asiakas ei voinut ennustaa;
siitä seuraa yksi kahden metrin korjaus.

## Korjauksen pehmennys

Suuri korjaus näkyy hyppäyksenä. Pienet korjaukset pehmennetään
näytössä: hahmon *näytetty* sijainti liukuu kohti täsmäytettyä
muutaman ruudun aikana, kun simulaation sijainti korjataan heti. Suuret
erot (teleportti, kuolema) näytetään sellaisenaan, koska liukuminen
seinän läpi olisi pahempi kuin hyppy.

## Käytännössä

- **Sama simulaatiokoodi asiakkaalla ja palvelimella.** Ennustus toimii
  vain, jos askel on deterministinen kummallakin (kiinteä aika-askel,
  kvantisoidut arvot, samat törmäystarkistukset).
- **Ennusta vain omaa hahmoa** ja sen välittömiä seurauksia (oma
  ammus, oma animaatio). Muiden pelaajien aikeita ei voi tietää.
- **Toista syötteitä paketeissa.** Muutama tavu lisää säästää
  korjauksia huonolla yhteydellä.
- **Rajoita kuittaamattomien määrää.** Jos jono kasvaa yli sekunnin,
  yhteys on katkennut; älä simuloi satoja syötteitä joka ruutu.
- **Hinta:** jokainen vastaanotettu tila maksaa kuittaamattomien
  syötteiden uudelleensimuloinnin. Fysiikkaraskaassa pelissä se
  rajoittaa, kuinka paljon ennustetaan.

## Itsearviointi

- Osaat toteuttaa asiakkaan ennustuksen numeroiduilla syötteillä ja
  kuittaamattomien jonolla.
- Osaat täsmäyttää ennusteen palvelimen tilaan simuloimalla
  kuittaamattomat syötteet uudelleen.
- Osaat selittää, miksi syötteiden toistaminen paketeissa vähentää
  korjauksia.
- Osaat kertoa, mitä asiakas voi ennustaa ja mitä ei.
