# Fuzzaus

*Fuzzaus* syöttää ohjelmalle valtavan määrän automaattisesti tuotettuja
syötteitä ja tarkkailee, kaatuuko se. *Kattavuusohjattu* fuzzeri
(*coverage-guided*) seuraa, mitä koodin haaroja kukin syöte suoritti,
ja jatkaa niiden syötteiden muuntelua, jotka löysivät jotain uutta.
Yhdessä sanitoijien kanssa se on tehokkain tunnettu tapa löytää
jäsentimien muistivirheitä: se ei väsy, se kokeilee rajatapauksia, joita
kukaan ei keksisi kirjoittaa, ja jokainen löydös on toistettava syöte.

## Kohde ja kohdefunktio

Jäsennin lukee TLV-viestejä: tyyppi, pituus ja data.

```{.c tiedosto="esimerkit/08-fuzzaus/tlv.h"}
```

Siinä on kaksi virhettä. Nimitietue kopioidaan kiinteään kenttään
tarkistamatta pituutta, ja versiotietueen numero on taulukon indeksi
ilman rajatarkistusta. Jälkimmäinen on vaikeampi löytää, koska se
vaatii tietueen, jonka data alkaa merkeillä `VERS`:

```{.c tiedosto="esimerkit/08-fuzzaus/tlv.c" osa="nimi"}
```

```{.c tiedosto="esimerkit/08-fuzzaus/tlv.c" osa="versio"}
```

*libFuzzer* on Clangin mukana tuleva fuzzeri. Testattavalle koodille
kirjoitetaan *kohdefunktio* (*fuzz target*, *harness*), joka saa
syötteen tavutaulukkona:

```{.c tiedosto="esimerkit/08-fuzzaus/fuzz_tlv.c" osa="kohde"}
```

Hyvä kohdefunktio on nopea, deterministinen ja vapauttaa kaiken, mitä
se varaa. Se ei lue tiedostoja eikä verkkoa, eikä sen tulos saa riippua
aiemmista kutsuista. Kohde käännetään fuzzerin ja sanitoijien kanssa:

```{.bash tiedosto="esimerkit/08-fuzzaus/aja.sh" osa="kaanna"}
```

## Korpus ja ajo

Fuzzeri aloittaa *korpuksesta*: kansiosta, jossa on kelvollisia
esimerkkisyötteitä. Tässä niitä on kaksi pientä viestiä. Fuzzeri
muuntelee niitä (vaihtaa, lisää ja poistaa tavuja, yhdistää syötteitä)
ja tallentaa korpukseen jokaisen muunnelman, joka kasvatti kattavuutta.
Ajo tehdään tässä kiinteällä siemenellä ja rajatulla ajomäärällä:

```{.bash tiedosto="esimerkit/08-fuzzaus/aja.sh" osa="sumenna"}
```

```{.tuloste tiedosto="esimerkit/08-fuzzaus/odotettu" osa="t1"}
```

Löydös tuli alle sekunnissa. Huomaa, että virheen havaitsi UBSan eikä
ASan: nimikenttä on tietueen `viesti` sisällä, ja ylivuoto jatkui
saman tietueen muihin kenttiin. ASan seuraa varauksia, ei kenttiä,
joten tietueen sisäinen ylivuoto (*intra-object overflow*) jää siltä
huomaamatta. UBSan:n rajatarkistus (`-fsanitize=bounds`) tuntee
taulukon tyypin ja huomasi liian suuren indeksin. Sanitoijat täydentävät
toisiaan, ja fuzzaus kannattaa tehdä molempien kanssa.

## Minimointi

Fuzzerin löytämä syöte on usein pitkä ja sekava. Minimointi etsii
lyhyemmän syötteen, joka kaatuu samalla tavalla:

```{.bash tiedosto="esimerkit/08-fuzzaus/aja.sh" osa="minimoi"}
```

```{.tuloste tiedosto="esimerkit/08-fuzzaus/odotettu" osa="t2"}
```

Minimoitu syöte on parempi virheraportin liitteeksi ja
regressiotestiksi: siitä näkee nopeammin, mikä tavu laukaisi virheen.

## Vertailujen seuraaminen

Kun nimen tarkistus on korjattu (`KORJAUS=1`), fuzzaus jatkuu. Versio-
virhe vaatii syötteen, jossa on oikealla paikallaan neljä tiettyä
tavua. Sokea arvaus onnistuisi keskimäärin kerran neljässä miljardissa,
mutta libFuzzer seuraa vertailuja (`memcmp`, `strcmp` ja
kokonaislukuvertailut) ja kokeilee niiden toisen puolen arvoja
syötteessä:

```{.tuloste tiedosto="esimerkit/08-fuzzaus/odotettu" osa="t3"}
```

Kun molemmat virheet on korjattu (`KORJAUS=2`), sama ajo ei löydä
mitään. Korpus kasvoi kahdesta syötteestä kymmeniin, ja se kannattaa
tallentaa: seuraava ajo jatkaa siitä, mihin edellinen jäi.

```{.tuloste tiedosto="esimerkit/08-fuzzaus/odotettu" osa="t4"}
```

Kiinteä siemen ei tee ajosta täysin toistettavaa: vertailujen
seuraaminen käyttää käskyjen osoitteita, joihin osoitteiden
satunnaistus vaikuttaa, ja löydöksen tavut ja korpuksen koko vaihtelevat
ajosta toiseen. Siksi skripti tulostaa vain virheen lajin ja kohdan.
Tavallisessa fuzzauksessa toistettavuutta ei tarvitakaan: fuzzeri
ajetaan tunteja tai päiviä, ja jokainen löydös tallennetaan
tiedostoksi, joka toistaa kaatumisen.

## Regressiotestit

Jokainen löydös lisätään regressiotestiksi. libFuzzer-kohde ajaa sille
annetut tiedostot kerran ilman fuzzausta, joten testi on yksinkertainen:

```{.bash tiedosto="esimerkit/08-fuzzaus/regressio.sh" osa="regressio"}
```

```{.tuloste tiedosto="esimerkit/08-fuzzaus/odotettu" osa="t5"}
```

Testi kuuluu tavalliseen CI:hin. Fuzzaus itse ajetaan erikseen,
esimerkiksi yöllä tai jatkuvana palveluna.

## AFL++

*AFL++* on toinen laajasti käytetty kattavuusohjattu fuzzeri. Se ajaa
kohdetta erillisinä prosesseina, joten se sopii myös ohjelmiin, joille
ei ole kohdefunktiota. Saman libFuzzer-kohteen voi kääntää sille
suoraan:

```{.bash tiedosto="esimerkit/08-fuzzaus/aja.sh" osa="afl"}
```

```{.tuloste tiedosto="esimerkit/08-fuzzaus/odotettu" osa="t6"}
```

AFL++:n ajo ei ole deterministinen, joten skripti tarkistaa vain, että
kaatuva syöte löytyi minuutin aikarajassa ja että se kaatuu myös
sanitoijakäännöksessä. Ympäristömuuttujat ohittavat tarkistuksia, jotka
ovat tarpeen vain pitkissä ajoissa (prosessorin taajuusasetus, ytimen
`core_pattern`).

## Fuzzaus osana kehitystä

- **OSS-Fuzz** on Googlen ylläpitämä palvelu, joka fuzzaa jatkuvasti
  yli tuhatta avointa projektia ja raportoi löydökset ylläpitäjille.
  Projekti tarjoaa kohdefunktiot ja käännösohjeen.
- **ClusterFuzzLite** ja vastaavat työkalut ajavat lyhyen fuzzauksen
  jokaisessa muutospyynnössä.
- **Rakenteiset syötteet** kannattaa tuottaa sanakirjalla
  (`-dict=`) tai rakennetietoisella muuntelijalla, jos muoto on
  monimutkainen.
- **Kohdefunktio on rajapinnan testi.** Jos jäsennin on vaikea fuzzata,
  se on usein myös vaikea testata ja ylläpitää.

## Käytännössä

- **Kirjoita kohdefunktio jokaiselle jäsentimelle**, joka käsittelee
  ulkopuolista dataa: tiedostomuodot, protokollat, asetukset.
- **Fuzzaa sanitoijien kanssa** (ASan ja UBSan), koska ilman niitä
  suurin osa muistivirheistä ei kaada ohjelmaa.
- **Aloita hyvästä korpuksesta** ja tallenna se versionhallintaan tai
  artefaktiksi.
- **Minimoi löydös ja lisää se regressiotestiksi** ennen korjausta.

## Itsearviointi

- Osaat kirjoittaa libFuzzer-kohdefunktion ja kääntää sen sanitoijien
  kanssa.
- Osaat selittää, miten kattavuusohjattu fuzzeri ja vertailujen
  seuraaminen löytävät syvällä olevia virheitä.
- Osaat minimoida löydöksen ja tehdä siitä regressiotestin.
- Osaat perustella, miksi ASan ei havaitse tietueen sisäistä ylivuotoa
  ja mikä sen havaitsee.
