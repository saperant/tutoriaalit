# Säiepooli

Säiepooli on joukko pitkäikäisiä työntekijäsäikeitä, jotka ottavat
tehtäviä yhteisestä jonosta. Pooli erottaa kaksi päätöstä toisistaan:
*mitä* tehdään (tehtävät) ja *millä* (säikeet). Säikeiden määrä valitaan
koneen mukaan kerran, ja tehtäviä voi olla miljoonia. Lähes jokainen
rinnakkainen kirjasto (Intel TBB, OpenMP:n tehtävät, Javan
`ExecutorService`, .NETin `ThreadPool`, Rustin Rayon) on pohjimmiltaan
pooli.

## Rakenne

Tämän luvun pooli on tarkoituksella yksinkertainen: yksi jono, yksi lukko
ja yksi ehtomuuttuja. Lähetys käärii tehtävän `std::packaged_task`iin,
jolloin paluuarvo ja poikkeus kulkevat futuren kautta kutsujalle:

```{.cpp tiedosto="esimerkit/yhteinen/saiepooli.hpp" osa="luokka"}
```

Työntekijä odottaa, kunnes jonossa on tehtävä tai pooli suljetaan. Tehtävä
otetaan jonosta lukon alla mutta *suoritetaan lukon ulkopuolella*, jotta
muut työntekijät pääsevät jonoon sillä välin:

```{.cpp tiedosto="esimerkit/yhteinen/saiepooli.hpp" osa="tyoskentele"}
```

Kolme yksityiskohtaa:

- **`std::move_only_function`** (C++23) kelpaa jonon alkioksi, koska
  `packaged_task` on vain siirrettävä. `std::function` vaatisi
  kopioitavuuden.
- **Purkujärjestys.** Hajotin asettaa sulkulipun ja herättää kaikki.
  Työntekijät tyhjentävät jonon ja palaavat. Sen jälkeen jäsenet
  tuhotaan käänteisessä määrittelyjärjestyksessä: ensin `tyontekijat_`,
  jonka `jthread`it odottavat säikeet, vasta sitten jono, ehtomuuttuja ja
  lukko. Jos säiesäiliö olisi määritelty ensimmäisenä, säikeet käyttäisivät
  jo tuhottua lukkoa.
- **Herätys lukon ulkopuolella.** `notify_one` kutsutaan lukon
  vapauttamisen jälkeen, jotta herännyt säie ei joudu heti odottamaan
  samaa lukkoa.

## Käyttö

Alkulukujen laskeminen jakautuu lohkoiksi, ja jokainen lohko on oma
tehtävänsä. Tulokset luetaan futureista lähetysjärjestyksessä, joten
tuloste on aina sama riippumatta siitä, missä järjestyksessä työntekijät
lohkot laskivat:

```{.cpp tiedosto="esimerkit/03-saiepooli.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/03-saiepooli.odotettu"}
```

Lohkot eivät ole yhtä työläitä: suurten lukujen jakajien tarkistus kestää
pidempään. Kun tehtäviä on enemmän kuin säikeitä, pooli tasaa kuormaa
itsestään, sillä vapautunut työntekijä ottaa seuraavan tehtävän. Luku
*Rinnakkaiset algoritmit ja työnjako* mittaa tämän.

## Poolin lukkiutuminen

Pooli voi lukkiutua ilman yhtään lukkovirhettä. Jos tehtävä lähettää
alitehtävän samaan pooliin ja jää odottamaan sen tulosta, se varaa
työntekijän odottamiseen. Kun kaikki työntekijät odottavat alitehtäviä,
jonossa olevia alitehtäviä ei suorita kukaan. Yhden työntekijän poolissa
tilanne syntyy aina:

```{.cpp tiedosto="esimerkit/03-odotus.cpp" osa="jumi"}
```

Isommassa poolissa sama tapahtuu vain, kun riittävän moni tehtävä odottaa
yhtä aikaa. Virhe ilmenee siis kuormassa eikä testeissä. Ratkaisuja on
neljä:

1. **Älä odota poolissa.** Tehtävä lähettää jatkon (*continuation*), joka
   suoritetaan, kun alitehtävä on valmis. Ulompi tehtävä palaa heti:

```{.cpp tiedosto="esimerkit/03-odotus.cpp" osa="ratkaisu"}
```

```{.tuloste tiedosto="esimerkit/03-odotus.odotettu"}
```

2. **Auta odottaessa.** Odottava työntekijä suorittaa jonon muita tehtäviä,
   kunnes sen oma tulos valmistuu. TBB ja työnvarastavat poolit tekevät
   näin (luku *Rinnakkaiset algoritmit ja työnjako*).
3. **Erilliset poolit.** Estävät tehtävät (I/O, odotukset) ajetaan eri
   poolissa kuin laskenta.
4. **Korutiinit.** C++20:n korutiini keskeyttää itsensä odotuksen ajaksi ja
   vapauttaa säikeen. Kirjastot kuten `cppcoro` ja `libunifex` sekä C++26:n
   `std::execution` rakentavat tämän varaan.

## Poolin koko

- **Laskentaan** (*CPU-bound*) säikeitä tarvitaan suunnilleen yhtä monta
  kuin prosessilla on käytettävissään ytimiä. Ylimääräiset säikeet
  lisäävät vain kontekstinvaihtoja ja välimuistin kuormaa.
- **Odottaviin tehtäviin** (*I/O-bound*) säikeitä tarvitaan enemmän:
  karkeasti ytimet kertaa (1 + odotusaika / laskenta-aika). Usein parempi
  ratkaisu on asynkroninen I/O, jolloin säie ei odota lainkaan.
- **Kontissa** `hardware_concurrency()` voi ilmoittaa isännän ytimet,
  vaikka cgroup rajoittaa suoritinajan pariin ytimeen. Rajan voi lukea
  tiedostosta `/sys/fs/cgroup/cpu.max`, tai poolin koon voi antaa
  asetuksena.

## Mitä tuotantopoolissa on lisää

Esimerkkipooli kattaa olennaisen, mutta tuotantokäytössä tarvitaan usein
lisää:

- **Työnvarastaminen**: jokaisella työntekijällä on oma jono, ja tyhjä
  työntekijä varastaa toisilta. Yksi yhteinen lukko on muuten pullonkaula,
  kun tehtävät ovat lyhyitä.
- **Rajattu jono ja vastapaine**: lähettäjä odottaa, kun jonossa on liikaa
  tehtäviä (luku *Ehtomuuttujat ja muut odotusvälineet*).
- **Prioriteetit ja peruutus**: kiireelliset tehtävät ohi jonon, ja
  vanhentuneet tehtävät pois `stop_token`illa.
- **Mittarit**: jonon pituus, odotusaika ja tehtävien kesto. Ilman niitä
  poolin mitoitus on arvailua.

## Käytännössä

- **Käytä valmista poolia, kun sellainen on.** TBB, Asio:n
  `thread_pool`, Folly ja Qt:n `QThreadPool` ovat testattuja. Oma pooli on
  perusteltu, kun tarvitaan vain vähän ja riippuvuus on raskas, kuten tässä.
- **Tehtävän on oltava riittävän iso.** Lähetys maksaa lukon, varauksen
  ja herätyksen, eli mikrosekunnin luokkaa. Tuhannen kertolaskun tehtävä
  on liian pieni; lohkot kokoavat työtä.
- **Älä odota poolin tehtävässä saman poolin tulosta.** Käytä jatkoja tai
  poolia, joka auttaa odottaessaan.
- **Poikkeukset futureen.** `packaged_task` hoitaa tämän. Jos pooli ajaa
  pelkkiä `void`-tehtäviä ilman futurea, poikkeus on otettava kiinni ja
  kirjattava, muuten työntekijä kuolee ja ohjelma päättyy.
- **Hallittu sulkeminen.** Hajotin suorittaa jonon loppuun. Jos
  keskeneräiset tehtävät pitää hylätä, siitä tehdään oma, nimetty
  operaatio.

## Itsearviointi

- Osaat toteuttaa säiepoolin, joka palauttaa tulokset ja poikkeukset
  futureina ja sulkeutuu hallitusti.
- Osaat selittää, miksi jäsenten määrittelyjärjestys ratkaisee poolin
  purkamisen oikeellisuuden.
- Osaat tunnistaa poolin lukkiutumisen ja välttää sen jatkokutsulla tai
  erillisellä poolilla.
- Osaat mitoittaa poolin laskentaan ja odottaviin tehtäviin.
