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

![Ylhäällä hyvän yhteyden ensimmäiset 400 ms. Syöte 5 lähtee hetkellä
100 ms, ja sen vahvistava tila palaa vasta, kun asiakas on jo
lähettänyt syötteet 6–13; ne simuloidaan uudelleen saapuneen tilan
päälle. Alhaalla tönäisyajo: ennuste kulkee palvelimen tilan edellä ja
asiakkaalle saapunut tila sen jäljessä. Palvelimen tönäisy hetkellä
6000 ms näkyy asiakkaalla yhtenä korjauksena noin 80 ms
myöhemmin.](kuvat/tasmaytys.png){width=95%}

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

## Aika ja tikit

Tähän asti on oletettu, että asiakas tietää, mille palvelimen tikille
sen syöte kuuluu. Koneiden kellot eivät kuitenkaan ole samassa ajassa,
eikä viive ole vakio. Asiakas arvioi palvelimen ajan samalla tavalla
kuin johdannon ping mittasi kiertoviiveen: se lähettää oman
kellonaikansa, palvelin vastaa omallaan, ja ero lasketaan olettaen,
että meno ja paluu kestivät yhtä kauan.

```{.cpp tiedosto="esimerkit/06-tikit.cpp" osa="kello"}
```

Oletus ei päde yksittäiselle näytteelle, koska värinä osuu suuntiin
eri tavoin. Näyte, jonka kiertoviive on pienin, on jonottanut vähiten
kumpaankin suuntaan, joten sen arvio on paras.

Pelkkä kellonaika ei vielä riitä. Syötteen on oltava palvelimella
*ennen* tikkiä, jota se koskee, joten asiakas käy palvelinta edellä
yhden suunnan viiveen ja pienen varan verran. Palvelin kertoo
jokaisesta syötteestä, kuinka monta tikkiä etuajassa se saapui, ja
asiakas säätää tahtiaan sen mukaan.

```{.cpp tiedosto="esimerkit/06-tikit.cpp" osa="tahti"}
```

```{.tuloste tiedosto="esimerkit/06-tikit.odotettu"}
```

![Vasemmalla kellon arvion virhe minuutin ajalta: yksittäiset näytteet
heittävät jopa 15 ms, pienimmän kiertoviiveen näyte selvästi vähemmän.
Oikealla syötteen etumatka. Asiakas aloittaa kolme tikkiä myöhässä,
kirii 19 ms:n tikeillä kahdessa sekunnissa tavoitteeseen ja kirii
uudelleen, kun viive kasvaa hetkellä 10 s.](kuvat/tikit.png){width=95%}

Ensimmäisen sekunnin aikana lähes jokainen syöte on myöhässä, toisella
enää yksi ja sen jälkeen ei yksikään. Kun reitin viive kasvaa 40 ms, kahden tikin vara
riittää juuri: etumatka putoaa nollaan, mutta syötteet ehtivät silti, ja
asiakas kirii varan takaisin. Tahtia säädetään muutaman prosentin
verran eikä kelloa siirretä kerralla, koska hyppy näkyisi pelaajalle
nykäyksenä tai kahtena samaan aikaan ajettuna tikkinä. Vara on kauppaa:
suurempi vara kestää enemmän värinää mutta lisää viivettä, jolla
palvelin näkee pelaajan syötteet.

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
- Osaat arvioida palvelimen kellon kiertoviiveestä ja selittää, miksi
  pienimmän kiertoviiveen näyte on luotettavin.
- Osaat pitää asiakkaan tikit palvelimen edellä säätämällä asiakkaan
  tahtia palvelimen palautteesta.
