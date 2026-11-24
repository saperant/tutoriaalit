# Puut

Puu on yhtenäinen graafi, jossa ei ole kehiä. Se on graafien
yksinkertaisin ja ohjelmoinnissa yleisin muoto: hakemistorakenne,
HTML-dokumentti, jäsennyspuu, organisaatiokaavio, päätöspuu ja
hakupuut ovat kaikki puita. Puiden ominaisuudet takaavat, että
jokaiseen solmuun on yksikäsitteinen reitti, ja niistä seuraa, miksi
puurakenteita käsitellään luontevasti rekursiolla.

## Puun ominaisuudet

Seuraavat ehdot ovat $n$ solmun graafille yhtäpitäviä; mikä tahansa
niistä määrittelee puun:

1. Graafi on yhtenäinen ja kehätön.
2. Graafi on yhtenäinen, ja siinä on $n - 1$ kaarta.
3. Graafi on kehätön, ja siinä on $n - 1$ kaarta.
4. Minkä tahansa kahden solmun välillä on täsmälleen yksi polku.
5. Graafi on yhtenäinen, mutta minkä tahansa kaaren poisto rikkoo
   yhtenäisyyden.
6. Graafi on kehätön, mutta minkä tahansa kaaren lisäys synnyttää
   kehän.

Ominaisuus 2 todistetaan induktiolla: puussa on aina **lehti** (aste
1), ja sen poisto jättää $n - 1$ solmun puun. Ominaisuudet antavat
käytännön testin: kaarijoukko on puu, jos kaaria on $n - 1$ eikä
yksikään sulje kehää. Kehän havaitsee **union–find**-rakenne, joka
pitää kirjaa siitä, mihin komponenttiin kukin solmu kuuluu:

```{.python tiedosto="esimerkit/11-puut.py" osa="puu"}
```

```{.python tiedosto="esimerkit/11-puut.py" osa="ominaisuudet"}
```

## Puiden lukumäärä

Montako erilaista puuta on $n$ numeroidulla solmulla? **Cayleyn
kaava** antaa yllättävän siistin vastauksen: $n^{n-2}$. Kaavan voi
todistaa Prüferin koodilla, joka on bijektio puiden ja
$(n-2)$-pituisten jonojen välillä. Tarkistus kokeilee kaikki
$(n-1)$-kaariset osajoukot ja laskee, moniko on puu:

```{.python tiedosto="esimerkit/11-puut.py" osa="cayley"}
```

```{.tuloste tiedosto="esimerkit/11-puut.odotettu"}
```

Luku selittää, miksi **virittävien puiden** (*spanning tree*)
luettelointi on toivotonta: täydellisessä 20 solmun graafissa niitä on
$20^{18} \approx 2{,}6 \cdot 10^{23}$. Pienimmän painon virittävä puu
löytyy silti tehokkaasti ahneilla algoritmeilla (Kruskal käyttää juuri
yllä olevaa union–findia) taidossa *Algoritmit*.

## Juurelliset puut

**Juurellisessa puussa** yksi solmu on **juuri**, ja kaaret
suuntautuvat siitä poispäin. Jokaisella solmulla paitsi juurella on
yksi **vanhempi** ja mahdollisesti **lapsia**; lapsettomat solmut ovat
**lehtiä**. Solmun **syvyys** on sen etäisyys juuresta ja puun
**korkeus** suurin syvyys. Hakemistorakenne on juurellinen puu:

```{.python tiedosto="esimerkit/11-hakemistopuu.py" osa="solmu"}
```

```{.python tiedosto="esimerkit/11-hakemistopuu.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/11-hakemistopuu.odotettu"}
```

Jokainen metodi on rakenteellista rekursiota: tulos lasketaan lasten
tuloksista. Oikeellisuus seuraa induktiosta puun korkeuden suhteen
(luku *Todistaminen ja invariantit*), ja rekursio päättyy, koska
puussa ei ole kehiä. Rekursion syvyys on puun korkeus, joten
tasapainoisissa puissa se on logaritminen ja turvallinen, mutta
listaksi rappeutuneessa puussa lineaarinen (luku *Rekursio ja
rekursioyhtälöt*).

## Binääripuut

**Binääripuussa** jokaisella solmulla on enintään kaksi lasta. Täydessä
binääripuussa, jonka korkeus on $h$, on $2^{h+1} - 1$ solmua ja
$2^h$ lehteä; kääntäen $n$ solmun tasapainoisen puun korkeus on noin
$\log_2 n$. Tämä logaritmi on hakupuiden, kekojen ja lajittelun
alarajan taustalla: miljoona alkiota mahtuu 20 tason puuhun.
Binäärihakupuut ja keot käsitellään taidossa *Tietorakenteet*.

## Käytännössä

- **Tarkista, että rakenne todella on puu.** Viitteet, jotka voivat
  muodostaa kehän (esim. vanhempiviitteet käyttäjän syötteestä), on
  validoitava; muuten rekursio jää silmukkaan.
- **Käsittele puu rakenteellisella rekursiolla.** Koko, korkeus,
  summa ja haku ovat ”tulos lapsista ja solmusta”. Kirjoita perustapaus
  lehdelle ja yhdistä lasten tulokset.
- **Varo syviä puita.** Käyttäjän syötteestä rakennettu puu (sisäkkäinen
  JSON, hakemistorakenne) voi olla syvä. Kriittisessä koodissa käytä
  eksplisiittistä pinoa ja rajoita syvyyttä.
- **Käytä union–findia yhtenäisyyskysymyksiin.** ”Ovatko nämä samassa
  ryhmässä?” ja ”sulkeeko tämä kaari kehän?” ratkeavat lähes
  vakioajassa.
- **Pidä puu tasapainossa.** Hakupuun hyöty on logaritminen korkeus.
  Ilman tasapainotusta järjestyksessä lisätyt avaimet tekevät siitä
  listan.

## Itsearviointi

- Osaat luetella puun yhtäpitävät määritelmät ja tunnistaa
  ohjelmallisesti, onko kaarijoukko puu.
- Osaat soveltaa Cayleyn kaavaa ja selittää, miksi virittävien puiden
  luettelointi on mahdotonta suurille graafeille.
- Osaat määritellä juurellisen puun käsitteet (juuri, lapsi, lehti,
  syvyys, korkeus) ja käsitellä puuta rakenteellisella rekursiolla.
- Osaat selittää binääripuun korkeuden ja solmumäärän yhteyden ja sen
  merkityksen tehokkaille tietorakenteille.
