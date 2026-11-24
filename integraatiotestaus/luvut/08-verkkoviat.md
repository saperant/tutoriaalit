# Verkkovikojen simulointi

Testiympäristön verkko on täydellinen: kontti on samalla koneella,
viive on mikrosekunteja eikä yhteys katkea koskaan. Tuotannossa verkko
hidastuu, yhteys katkeaa kesken kyselyn ja palvelu vastaa välillä 503.
Koodi, jota ei ole koskaan ajettu näissä oloissa, käyttäytyy niissä
arvaamattomasti: aikaraja puuttuu, uudelleenyritykset kertautuvat tai
yhteysallas jää täyteen kuolleita yhteyksiä.

Integraatiotestissä viat tuotetaan tarkoituksella. Yleisin tapa on
asettaa testattavan koodin ja riippuvuuden väliin välityspalvelin, jota
testi ohjaa: se voi lisätä viivettä, katkaista yhteydet tai hylätä uudet.
Tunnetuin tällainen on Shopifyn Toxiproxy, jolle Testcontainersissa on
moduuli. Tässä luvussa periaate toteutetaan pienellä omalla
*vikaproxyllä*, jotta mekanismi näkyy kokonaan.

## Vikaproxy

Vikaproxy välittää TCP-yhteydet kohteeseen ja ottaa ohjeita
HTTP-portista. Välitys on muutama rivi asyncio-koodia; viive lisätään
jokaisen datapalan väliin:

```{.python tiedosto="esimerkit/apukuva/vikaproxy.py" osa="valitys"}
```

Hallinta on yksinkertainen: `POST /viive?ms=N`, `POST /katkaise` ja
`POST /palauta`. Proxy on samassa apukuvassa kuin hintapalvelun
väärennös, ja se käynnistetään eri komennolla:

```{.python tiedosto="esimerkit/testiapu/kontit.py" osa="vikaproxy"}
```

## Kontit samaan verkkoon

Proxy ja kohde ovat omassa Docker-verkossaan, jossa ne tavoittavat
toisensa nimillä. Testi puhuu vain proxylle sen kartoitetun portin
kautta:

```{.dot otsikko="Testi, vikaproxy ja kohde omassa Docker-verkossa"}
digraph {
  rankdir=LR;
  testi [label="testi\n(isäntä)"];
  subgraph cluster_verkko {
    label="Docker-verkko"; style="rounded,dashed";
    proxy [label="vikaproxy\n8666 data, 8474 ohjaus"];
    kohde [label="hinnat:8080\ntai tietokanta:5432"];
  }
  testi -> proxy [label="kartoitettu portti"];
  testi -> proxy [label="POST /viive", style=dashed];
  proxy -> kohde [label="verkon sisäinen nimi"];
}
```

```{.python tiedosto="esimerkit/testit/test_viat.py" osa="verkko"}
```

Verkon nimet (*network aliases*) ovat konttien välistä liikennettä
varten. Testi itse ei näe niitä, koska se on verkon ulkopuolella; se
käyttää kartoitettuja portteja kuten aina.

## Viive ja aikaraja

Hinta-asiakkaalla on jokaiselle yritykselle aikaraja. Testi tarkistaa,
että aikaraja todella laukeaa ja että asiakas toipuu, kun verkko
paranee:

```{.python tiedosto="esimerkit/testit/test_viat.py" osa="viivetesti"}
```

`finally` palauttaa proxyn, vaikka testi epäonnistuisi; muuten yksi
epäonnistunut testi rikkoisi kaikki seuraavat samaa proxya käyttävät.
Viive (1000 ms) on selvästi aikarajaa (300 ms) suurempi, jotta testi ei
ole herkkä koneen kuormalle. Raja-arvon lähellä testaaminen (290 ms vastaan
310 ms) on varma tapa tehdä epävakaa testi.

## Yhteysallas ja katkos

Tietokannan kohdalla kiinnostavaa on yhteysallas. Kun yhteys katkeaa,
altaaseen jää kuollut yhteys, ja ilman tarkistusta seuraava kysely
epäonnistuu, vaikka verkko olisi jo kunnossa. SQLAlchemyn
`pool_pre_ping` tarkistaa yhteyden ennen käyttöä:

```{.python tiedosto="esimerkit/testit/test_viat.py" osa="katkotesti"}
```

Ilman `pool_pre_ping`-asetusta viimeinen kysely epäonnistuisi
kuolleeseen yhteyteen. Tällainen vika näkyy tuotannossa tyypillisesti
tietokannan uudelleenkäynnistyksen jälkeen ensimmäisinä virheinä, ja
ilman testiä sitä on vaikea toistaa.

## Vikamatriisi

Samaa järjestelyä voi käyttää kartoittamaan, miten asiakas käyttäytyy
eri vioissa. Seuraava esimerkki ajaa hinta-asiakkaan viittä vikaa vastaan
ja tulostaa tuloksen:

```{.python tiedosto="esimerkit/luku08/vikamatriisi.py" osa="matriisi"}
```

```{.tuloste tiedosto="esimerkit/luku08/vikamatriisi.odotettu"}
```

Kaksi tilapäistä 503:a selviää kolmella yrityksellä, kolme ei. Viive ja
katkos päättyvät samaan virheeseen, mikä on asiakkaan kannalta oikein:
kutsujaa kiinnostaa, saatiinko hinta, ei syyn yksityiskohdat. Vian syy
kuuluu lokiin ja metriikoihin.

## Mitä kannattaa simuloida

| Vika | Mitä paljastaa |
|--------------------------|------------------------------------------|
| viive yli aikarajan | puuttuva tai liian pitkä aikaraja |
| katkos kesken yhteyden | kuolleet yhteydet altaassa, puolikkaat vastaukset |
| hylätyt uudet yhteydet | yhteyden muodostuksen aikaraja, uudelleenyritykset |
| tilapäiset 5xx-vastaukset | uudelleenyritykset ja niiden raja |
| hidas mutta toimiva | aikarajan ja kuorman suhde, jonojen kasvu |
| kaistan rajoitus | suurten vastausten käsittely, aikaraja vastaan koko |

Toxiproxyssä nämä ovat valmiita *toxiceja* (latency, timeout,
bandwidth, slicer, reset_peer), ja ne voi asettaa erikseen lähtevälle ja
tulevalle liikenteelle. Taito *Hajautetut järjestelmät* simuloi samoja
vikoja deterministisessä simulaattorissa; integraatiotesti on oikean
verkkopinon versio samasta ajatuksesta.

## Käytännössä

- Testaa jokaisesta ulkoisesta kutsusta vähintään viive yli aikarajan ja
  katkos. Ne ovat tuotannon yleisimmät viat.
- Palauta proxy aina `finally`-lohkossa tai fixturen purussa.
- Valitse viiveet niin, että testi ei ole herkkä koneen kuormalle:
  selvästi yli tai selvästi alle rajan.
- Tarkista toipuminen: vian jälkeen seuraavan kutsun on onnistuttava.

## Itsearviointi

- Osaat asettaa välityspalvelimen testattavan koodin ja riippuvuuden
  väliin samassa Docker-verkossa.
- Osaat testata aikarajan ja uudelleenyritykset viivettä ja tilapäisiä
  virheitä vastaan.
- Osaat selittää, miksi yhteysallas tarvitsee yhteyden tarkistuksen, ja
  testata toipumisen katkoksesta.
- Osaat valita simuloitavat viat ja perustella, mitä kukin paljastaa.
