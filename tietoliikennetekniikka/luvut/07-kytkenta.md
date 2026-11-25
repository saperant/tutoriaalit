# Kytkentätavat ja viive

Puhelinverkko varasi jokaiselle puhelulle oman yhteyden koko puhelun
ajaksi. Internet lähettää paketteja, jotka jakavat linkit ja odottavat
vuoroaan jonoissa. Tämä luku vertaa kytkentätapoja ja purkaa paketin
viiveen osiin.

## Piirikytkentä ja pakettikytkentä

**Piirikytkentä** varaa yhteydelle kiinteän kapasiteetin (aikavälin tai
taajuuden) koko yhteyden ajaksi. Viive on vakio ja kapasiteetti taattu,
mutta varattu kapasiteetti on hukassa, kun yhteydessä on hiljaista.
**Pakettikytkentä** lähettää datan paketteina, jotka käyttävät linkkiä
vain silloin, kun niitä on. Linkki jaetaan tilastollisesti: koska
kaikki eivät lähetä yhtä aikaa, samalla linkillä voi olla paljon
enemmän käyttäjiä kuin sen kapasiteetti riittäisi kaikille yhtä aikaa.

```{.python tiedosto="esimerkit/07-tilastollinen.py" osa="vertailu"}
```

```{.python tiedosto="esimerkit/07-tilastollinen.py" osa="simulaatio"}
```

```{.tuloste tiedosto="esimerkit/07-tilastollinen.odotettu"}
```

Piirikytkentä palvelee kymmentä käyttäjää. Pakettikytkentä palvelee
35:tä niin, että linkki on ylikuormassa vain 0,04 % ajasta. Tätä
**tilastollisen multipleksoinnin hyötyä** vastaan pakettikytkentä
luopuu takuista: Internet on **best-effort**-verkko, joka yrittää
toimittaa paketit mutta ei lupaa nopeutta, viivettä eikä edes
perillemenoa. Takuut rakennetaan päälle tarvittaessa (TCP:n
uudelleenlähetys, palvelun laatu, luku Jonot ja palvelun laatu).
Piirikytkennän ajatus elää edelleen, kun kapasiteetti varataan
kiinteästi: matkaviestinverkon radioresurssit ja kuituverkon OTN-kanavat
ovat varattuja, vaikka niiden päällä kulkee paketteja.

## Viiveen osat

Paketin viive linkillä on neljän osan summa:

| Osa | Syy | Riippuu |
|-----|-----|---------|
| siirtoviive | bittien lähettäminen linjalle | paketin koko / linkin nopeus |
| etenemisviive | signaalin kulku | etäisyys / signaalin nopeus |
| jonoviive | odotus lähtöjonossa | kuormitus |
| käsittelyviive | otsakkeen käsittely reitittimessä | laite (mikrosekunteja) |

![Paketin kulku lähettäjältä reitittimen kautta vastaanottajalle
(periaatekuva, ei mittakaavassa). Aika kulkee alaspäin. Kaistan
korkeus on siirtoviive ja sen kaltevuus etenemisviive. Reititin
lähettää paketin eteenpäin vasta, kun se on saapunut kokonaan,
käsitelty ja päässyt jonon kärkeen.](kuvat/viive.png){width=75%}

Esimerkki laskee osat kolmen linkin reitille:

```{.python tiedosto="esimerkit/07-viive.py" osa="viive"}
```

```{.tuloste tiedosto="esimerkit/07-viive.odotettu"}
```

Pitkällä matkalla etenemisviive hallitsee, eikä nopeampi liittymä
lyhennä sitä: Helsingin ja Frankfurtin välillä valo kulkee kuidussa
8 ms suuntaansa, oli linkki kuinka nopea tahansa. Hitaalla linkillä
siirtoviive on merkittävä isoille paketeille, ja jonoviive vaihtelee
kuormituksen mukaan ja aiheuttaa viiveen vaihtelun (*jitter*).

## Kaistan ja viiveen tulo

Liukuvan ikkunan protokollassa (luku Virheiden havaitseminen ja
korjaus) linjalla on matkalla korkeintaan ikkunan verran
kuittaamatonta dataa kerrallaan. Jotta linkki pysyy täynnä, ikkunan on
oltava vähintään kaistan ja kierrosajan tulo (*bandwidth-delay
product*, BDP):

```{.python tiedosto="esimerkit/07-bdp.py" osa="bdp"}
```

```{.tuloste tiedosto="esimerkit/07-bdp.odotettu"}
```

Ilman ikkunan skaalausta TCP:n 64 KiB:n ikkuna rajaa
Tokion-yhteyden 2 megabittiin sekunnissa, vaikka linkki olisi
gigabitin. Nykyiset käyttöjärjestelmät skaalaavat ikkunan
automaattisesti, mutta sama ilmiö näkyy sovellustasolla: jos
sovellus odottaa vastausta jokaiseen pyyntöön ennen seuraavaa,
läpäisy on viestin koko jaettuna kierrosajalla.

## Käytännössä

- **Viive ei parane kaistalla.** Kun käyttäjä valittaa hitaudesta
  kaukaisen palvelimen kanssa, kaistan lisääminen ei auta. Auttaa
  palvelimen tuominen lähemmäs (CDN, alueelliset palvelut) ja
  kierrosten vähentäminen (TLS 1.3, HTTP/2 ja HTTP/3, pyyntöjen
  niputus).
- **Mittaa kierrosaika ja BDP.** Puskurien, ikkunoiden ja
  rinnakkaisten yhteyksien mitoitus lähtee niistä.
- **Pidä jonot lyhyinä.** Ylisuuret puskurit kasvattavat viivettä
  sekunteihin (*bufferbloat*). Aktiivinen jonon hallinta (CoDel, FQ-
  CoDel) pitää viiveen pienenä kuormassakin.
- **Best-effort on suunnittelupäätös.** Pakettiverkko on halpa ja
  joustava, koska se ei lupaa mitään. Sovelluksen on siedettävä
  viiveen vaihtelua ja pakettien katoamista.

## Itsearviointi

- Osaat vertailla piiri- ja pakettikytkentää ja laskea tilastollisen
  multipleksoinnin hyödyn binomijakaumalla.
- Osaat jakaa paketin viiveen siirto-, etenemis-, jono- ja
  käsittelyviiveeseen ja arvioida, mikä niistä hallitsee.
- Osaat laskea kaistan ja viiveen tulon ja selittää, miksi pieni
  ikkuna rajaa nopeutta pitkillä yhteyksillä.
