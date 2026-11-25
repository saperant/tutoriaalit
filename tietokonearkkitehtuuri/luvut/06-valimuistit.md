# Välimuistit

Liukuhihnamalli oletti, että muisti vastaa yhdessä jaksossa. Todellisuus
on toinen. Nykyisen suorittimen ydin tekee jakson kolmanneksessa
nanosekunnissa, mutta DRAM-muistista luku kestää 60–100 ns: satoja
jaksoja. Ero on kasvanut vuosikymmeniä (*memory wall*), koska
suorittimien nopeus kasvoi aikoinaan 50 % vuodessa ja DRAM-viive
paranee vain muutaman prosentin vuodessa.

Ratkaisu on muistihierarkia: pieniä, nopeita muisteja lähellä ydintä ja
suuria, hitaita kauempana. Tyypilliset luvut nykyiselle työpöytä- tai
palvelinytimelle:

| Taso | Koko | Viive (jaksoja) |
|------|------|-----------------|
| rekisterit | ~200 × 64 bittiä (fyysiset) | 0 |
| L1-data | 32–64 KiB | 4–5 |
| L2 | 0,5–2 MiB | 12–16 |
| L3 (jaettu) | 8–100 MiB | 40–70 |
| DRAM | gigatavuja | 200–400 |

Hierarkia toimii, koska ohjelmat noudattavat **paikallisuutta**:

- **Ajallinen paikallisuus**: juuri käytettyyn dataan viitataan pian
  uudelleen (silmukan muuttujat, pino, kuumat funktiot).
- **Tilallinen paikallisuus**: juuri käytetyn datan naapuriin viitataan
  pian (taulukon seuraava alkio, rakenteen seuraava kenttä, seuraava
  käsky).

Välimuisti hyödyntää ajallista paikallisuutta pitämällä viimeksi
käytetyn datan tallessa ja tilallista tuomalla kerralla kokonaisen
**lohkon** (*cache line*, tyypillisesti 64 tavua).

## Osoitteen jako

Välimuisti on taulukko rivejä. Jokaisella rivillä on lohkon data,
**tagi** (mistä osoitteesta lohko on) ja kelpoisuusbitti. Osoite
jaetaan kolmeen kenttään:

```{.dot otsikko="Kaksitiinen joukkoassosiatiivinen välimuisti: indeksi valitsee joukon, joukon teiden tagit verrataan rinnakkain osoitteen tagiin, ja osunut tie antaa datan"}
digraph {
  rankdir=TB; nodesep=0.35; ranksep=0.38;
  edge [fontsize=8];
  node [shape=record];
  os [label="{osoite|{<t>tagi|<i>indeksi|<s>siirtymä}}"];
  t0 [label="{tie 0, joukko i|{<t>V + tagi|<d>lohkon data}}"];
  t1 [label="{tie 1, joukko i|{<t>V + tagi|<d>lohkon data}}"];
  v0 [label="=", shape=circle, width=0.3, fixedsize=true];
  v1 [label="=", shape=circle, width=0.3, fixedsize=true];
  mux [label="valitaan osunut tie", shape=invtrapezium];
  ulos [label="tavu suorittimelle\n(tai huti)", shape=box];
  os:i -> t0 [label="valitsee joukon"];
  os:i -> t1;
  os:t -> v0; os:t -> v1;
  t0:t -> v0; t1:t -> v1;
  v0 -> mux [label="osuma 0"]; v1 -> mux [label="osuma 1"];
  t0:d -> mux; t1:d -> mux;
  mux -> ulos;
  os:s -> ulos [label="valitsee tavun", style=dashed, constraint=false];
}
```

Kenttien leveydet seuraavat välimuistin mitoista: siirtymässä on
$\log_2(\text{lohkon koko})$ bittiä, indeksissä
$\log_2(\text{joukkojen määrä})$ bittiä, ja loput ovat tagia.

- **Siirtymä** kertoo tavun paikan lohkossa.
- **Indeksi** valitsee joukon (*set*), johon lohko voi sijoittua.
- **Tagi** erottaa samaan joukkoon kuvautuvat lohkot toisistaan.

Joukossa on yksi tai useampi **tie** (*way*). Kun haetaan, indeksi
valitsee joukon, ja joukon kaikkien teiden tagit verrataan
rinnakkain osoitteen tagiin. Osuma tarkoittaa, että jokin kelvollinen
tie täsmää.

| Rakenne | Teitä | Joukkoja | Hinta |
|---------|-------|----------|-------|
| suora kuvaus | 1 | rivit | yksi vertailija, nopein |
| joukkoassosiatiivinen | 2–16 | rivit / tiet | tiet vertailijaa ja multiplekseri |
| täysin assosiatiivinen | rivit | 1 | vertailija jokaiselle riville |

Simulaattorin välimuisti on parametrisoitava. Se ei tallenna dataa, vain
tagit ja tilan, koska osumasuhde riippuu vain osoitteista:

```{.cpp tiedosto="esimerkit/yhteinen/valimuisti.hpp" osa="asetukset"}
```

```{.cpp tiedosto="esimerkit/yhteinen/valimuisti.hpp" osa="valimuisti"}
```

Ensimmäinen esimerkki jakaa osoitteet kenttiin 256 tavun suoraan
kuvatussa välimuistissa, jossa on 16 tavun lohkot ja siis 16 riviä:

```{.cpp tiedosto="esimerkit/06-rakenne.cpp" osa="kentat"}
```

```{.tuloste tiedosto="esimerkit/06-rakenne.odotettu" rivit="1-9"}
```

Ensimmäiset rivit näyttävät tilallisen paikallisuuden: 0x100 hutii ja
tuo koko lohkon 0x100–0x10f, joten 0x104 ja 0x10c osuvat. 0x110 on jo
seuraavassa lohkossa. Sitten 0x200 kuvautuu samaan riviin 0 kuin 0x100
(eri tagi) ja syrjäyttää sen. Kun ohjelma vuorottelee näiden kahden
lohkon välillä, jokainen viite hutii, vaikka välimuistin 16 rivistä
14 on käyttämättä. Tämä on **ristiriitahuti** (*conflict miss*), suoran
kuvauksen pahin heikkous.

## Koko ja lohkokoko

Saman esimerkin toinen osa ajaa matriisitulon 3 900 datamuistiviitettä
eri kokoisten ja eri lohkokokoisten välimuistien läpi:

```{.cpp tiedosto="esimerkit/06-rakenne.cpp" osa="koko"}
```

```{.tuloste tiedosto="esimerkit/06-rakenne.odotettu" rivit="11-17"}
```

![Osumasuhde lohkokoon funktiona suoraan kuvatussa välimuistissa
(sama data kuin taulukossa). Pienessä välimuistissa käyrä kääntyy
laskuun, kun lohko kasvaa yli 16 tavun.](kuvat/osumasuhde.png){width=72%}

Matriiseja on kolme 576 tavun kappaletta, yhteensä 1 728 tavua.
Havainnot:

- **Koko ratkaisee eniten.** Kun välimuisti on 2 KiB, koko työjoukko
  mahtuu, ja jäljelle jäävät vain ensikäynnin hudit.
- **Suurempi lohko auttaa**, koska matriisin rivi luetaan
  peräkkäin: 4 tavun lohkolla jokainen uusi sana hutii, 16 tavun
  lohkolla vain joka neljäs.
- **Liian suuri lohko haittaa pienessä välimuistissa.** 256 tavun
  välimuistissa on 128 tavun lohkoilla vain kaksi riviä, ja kolmen
  matriisin viitteet syrjäyttävät toisensa jatkuvasti: osumasuhde laskee
  67 %:sta 37 %:iin. Lisäksi jokainen huti siirtää enemmän dataa, joten
  hudin *hinta* kasvaa.

Nykyisissä suorittimissa lohko on lähes aina 64 tavua: kompromissi
tilallisen paikallisuuden, väylän leveyden ja ristiriitojen välillä.

## Assosiatiivisuus ja korvaus

Assosiatiivisuus vähentää ristiriitahutia, koska samaan joukkoon
kuvautuvat lohkot mahtuvat eri teihin. Kun joukko on täynnä, on
valittava uhri. Yleiset **korvauspolitiikat**:

- **LRU** (*least recently used*): poistetaan pisimpään käyttämättä ollut.
  Paras yleispolitiikka, mutta tarkka toteutus on kallis yli neljälle
  tielle, joten laitteisto käyttää likiarvoja (pseudo-LRU, puu-LRU).
- **FIFO**: poistetaan vanhin tuotu. Halpa, mutta ei huomioi käyttöä.
- **Satunnainen**: yksinkertaisin laitteisto, yllättävän kilpailukykyinen
  suurilla assosiatiivisuuksilla. Simulaattori käyttää deterministisen
  näennäissatunnaisen generaattorin, jotta tulos on toistettavissa.

```{.cpp tiedosto="esimerkit/06-assosiatiivisuus.cpp" osa="tiet"}
```

```{.tuloste tiedosto="esimerkit/06-assosiatiivisuus.odotettu" rivit="1-12"}
```

512 tavun välimuistissa kaksi tietä nostaa osumasuhteen 84 %:sta 88 %:iin,
mutta neljä tietä ja täysi assosiatiivisuus ovat *huonompia* kuin kaksi.
Tämä on LRU:n tunnettu heikkous: kun silmukka käy läpi hieman
välimuistia suuremman datajoukon, LRU poistaa aina juuri sen lohkon,
jota tarvitaan seuraavaksi. Suora kuvaus ja pieni assosiatiivisuus
"suojaavat" osan lohkoista sattumalta. Optimaalinen politiikka
(Béládyn MIN, poista lohko, jota tarvitaan kauimpana tulevaisuudessa)
vaatisi tulevaisuuden tuntemista. Nykyiset L3-välimuistit käyttävät
siksi mukautuvia politiikkoja (RRIP, DIP), jotka tunnistavat
läpikäyntikuviot ja suojaavat osan datasta.

## Hutien kolme lajia

Mark Hillin 3C-malli luokittelee hudit syyn mukaan:

- **Pakolliset** (*compulsory*, *cold*): lohkoon viitataan ensimmäistä
  kertaa. Vain suurempi lohko tai esihaku (*prefetch*) auttaa.
- **Kapasiteetti**: työjoukko ei mahdu. Myös samankokoinen täysin
  assosiatiivinen välimuisti hutisi. Auttaa vain suurempi välimuisti
  tai algoritmi, jonka työjoukko on pienempi.
- **Ristiriita**: lohko poistettiin, koska joukko oli täynnä, vaikka
  välimuistissa olisi ollut tilaa. Assosiatiivisuus auttaa.

Luokittelu saadaan simuloimalla rinnakkain todellista välimuistia ja
samankokoista täysin assosiatiivista LRU-välimuistia:

```{.cpp tiedosto="esimerkit/yhteinen/valimuisti.hpp" osa="kolme_c"}
```

```{.cpp tiedosto="esimerkit/06-assosiatiivisuus.cpp" osa="kolme_c"}
```

```{.tuloste tiedosto="esimerkit/06-assosiatiivisuus.odotettu" rivit="14-26"}
```

Pakollisia huteja on aina 108:
kolme 576 tavun matriisia on 108 lohkoa. 2 KiB:n välimuistissa ne ovat
ainoat. 256 tavun suoraan kuvatussa välimuistissa ristiriitahuteja on
enemmän kuin kapasiteettihuteja, ja neljä tietä poistaa niistä
kolmanneksen. 512 tavun välimuistissa 37 ristiriitahutia katoaa jo
kahdella tiellä, mutta 475 kapasiteettihutia jää, koska työjoukko on
yli kolme kertaa välimuistin kokoinen.

512 tavun kaksitiinen välimuisti hutii itse asiassa *vähemmän* kuin
täysin assosiatiivinen LRU-vertailukohta (edellisen taulukon LRU-ilmiö).
Silloin ristiriitahutien määrä olisi negatiivinen, ja simulaattori
pyöristää sen nollaan. 3C on siis selittävä malli, ei tarkka mittaus.

## Esihaku

Pakollisia huteja ei voi poistaa välimuistin rakenteella, mutta ne voi
ennakoida. **Esihakija** (*prefetcher*) seuraa viitteitä ja tuo
todennäköisesti seuraavaksi tarvittavat lohkot välimuistiin ennen kuin
ohjelma pyytää niitä. Yksinkertaisin on seuraavan lohkon esihakija:

```{.cpp tiedosto="esimerkit/06-esihaku.cpp" osa="esihaku"}
```

Kolme ohjelmaa 256 tavun kaksitiisessä välimuistissa ilman esihakua ja
sen kanssa:

```{.tuloste tiedosto="esimerkit/06-esihaku.odotettu"}
```

- `summa` käy taulukon läpi peräkkäin. Sadasta hudista jää kaksi, ja
  98 esihakua sadasta osui tarpeeseen. Tämä selittää, miksi peräkkäinen
  läpikäynti on oikealla koneella nopeampi kuin pelkkä osumasuhde
  ennustaa: pakollisetkin hudit katoavat.
- `matriisi` *huononee*. Sisäsilmukka kulkee toista matriisia
  sarakkeittain 48 tavun askelin, joten seuraava lohko on väärä arvaus,
  ja pienessä välimuistissa turha lohko syrjäyttää hyödyllisen. Yli
  2 000 esihausta vain 295 käytettiin.
- `lista` hyötyy osittain, koska sen 64 solmua ovat pienellä alueella
  ja lista palaa viereiseen lohkoon usein ennen kuin esihaettu lohko on
  syrjäytynyt. Osuma on sattumaa, ei esihakijan ansiota: suuressa
  rakenteessa seuraava solmu on harvoin naapurilohkossa.

Oikeat esihakijat ovat siksi valikoivampia. **Askelesihakija** (*stride
prefetcher*) seuraa kunkin latauskäskyn peräkkäisten osoitteiden
erotusta ja hakee etukäteen vasta, kun sama askel on toistunut; se
löytäisi matriisin 48 tavun askeleen. **Virtaesihakija** tunnistaa
nousevan tai laskevan lohkojonon ja kulkee sen edellä usean lohkon
päässä, jotta data ehtii perille ennen käyttöä. Väärä esihaku maksaa
kaistaa ja voi syrjäyttää hyödyllistä dataa, joten esihakijat mittaavat
omaa osumatarkkuuttaan ja hiljenevät, kun arvaukset eivät osu.

## Käytännössä

- **Data kannattaa pakata.** Välimuisti siirtää aina koko lohkon. Jos
  rakenteesta käytetään kuumassa silmukassa vain yhtä kenttää, muut
  kentät kuluttavat välimuistia turhaan. Taulukoiden rakenne
  (*structure of arrays*) on usein nopeampi kuin rakenteiden taulukko.
- **Kahden potenssit ovat vaarallisia.** Jos taulukon rivin pituus on
  välimuistin joukkojen määrän monikerta, sarakkeen alkiot kuvautuvat
  samaan joukkoon. Rivin pidentäminen yhdellä lohkolla (*padding*)
  poistaa ristiriidat.
- **Mittaa, älä arvaa.** `perf stat -e cache-references,cache-misses`,
  `perf c2c` ja Valgrindin `cachegrind` (joka on simulaattori kuten
  tämänkin luvun malli) kertovat, missä hudit syntyvät.
- **Kirjoita esihakijalle.** Peräkkäinen ja vakioaskeleinen läpikäynti
  on esihakijalle ilmaista. Osoitinjahti (linkitetty lista, puu) ei ole
  ennustettava, ja siksi se on hidas: jokainen solmu on mahdollinen
  DRAM-huti.

## Itsearviointi

- Osaat jakaa osoitteen tagiksi, indeksiksi ja siirtymäksi annetulla
  koolla, lohkokoolla ja assosiatiivisuudella.
- Osaat simuloida käsin lyhyen viitejonon suoraan kuvatussa ja
  kaksitiisessä LRU-välimuistissa.
- Osaat luokitella hudit 3C-mallilla ja kertoa, mikä muutos auttaa
  kuhunkin lajiin.
- Osaat selittää, milloin seuraavan lohkon esihaku poistaa hudit ja
  milloin se lisää niitä.
