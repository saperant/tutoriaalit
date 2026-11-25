# Haarautumisen ennustus

Edellisen luvun liukuhihnassa haara ratkeaa EX-vaiheessa. Siihen
mennessä kaksi seuraavaa käskyä on jo noudettu, ja jos haara toteutuu,
ne on hylättävä. Jos haaroja on 15 % käskyistä ja niistä puolet toteutuu,
CPI kasvaa $0{,}15 \times 0{,}5 \times 2 = 0{,}15$ jaksoa. Syvässä
liukuhihnassa, jossa virhe maksaa 15 jaksoa, ja leveässä ytimessä, joka
noutaa neljä käskyä jaksossa, sama virhe hukkaa kymmeniä käskypaikkoja.
Nykyisen suorittimen suorituskyky riippuu enemmän ennustimen
tarkkuudesta kuin melkein mistään muusta.

Ratkaisu on *arvata* haaran suunta heti noudossa ja jatkaa arvatulta
polulta. Jos arvaus osuu, mitään ei menetetä. Jos se menee pieleen,
väärän polun käskyt hylätään ennen kuin ne ehtivät muuttaa
arkkitehtuurista tilaa (rekisteritiedostoa tai muistia), ja hinta on
sama kuin ilman ennustusta.

## Mitä pitää ennustaa

Noudon on tiedettävä jo IF-vaiheessa, ennen kuin käsky on edes purettu:

1. **Onko tämä haara?** Käskyn tyyppi selviää vasta purussa.
2. **Mihin se hyppää?** Kohde lasketaan EX-vaiheessa.
3. **Toteutuuko se?** Ehto ratkeaa EX-vaiheessa.

Kaksi ensimmäistä ratkaisee **haarakohdepuskuri** (BTB, *branch target
buffer*): pieni välimuisti, joka kertoo PC:n perusteella, onko
osoitteessa haara ja mikä on sen edellinen kohde. Kolmas on
**suunnan ennustimen** tehtävä. Simulaattorin malli olettaa täydellisen
BTB:n: oikein ennustettu toteutuva haara ei maksa mitään.

## Staattiset ennusteet

Yksinkertaisin ennuste on "ei hypätä": noudetaan aina PC + 4. Se ei
vaadi laitteistoa, mutta silmukan loppuhaara toteutuu lähes aina, joten
ennuste on väärin juuri tavallisimmassa tapauksessa.

Parempi staattinen sääntö on **BTFN** (*backward taken, forward not
taken*): taaksepäin hyppäävä haara on todennäköisesti silmukka ja
toteutuu, eteenpäin hyppäävä ohittaa harvinaisen tapauksen
(virheenkäsittely, `if`) eikä toteudu. Kääntäjä voi tukea sääntöä
järjestämällä koodin niin, että todennäköinen polku jatkuu suoraan
(`[[likely]]`, `__builtin_expect`, profiiliohjattu optimointi).

## Dynaamiset ennustimet

Dynaaminen ennustin muistaa haaran aiemman käytöksen. Tila on
taulukossa, jota indeksoidaan PC:n alimmilla biteillä:

```{.cpp tiedosto="esimerkit/yhteinen/liukuhihna.hpp" osa="ennustimet"}
```

**Yksibittinen** ennustin muistaa viimeisimmän suunnan. Silmukan
lopussa se erehtyy kahdesti: viimeisellä kierroksella (ennuste "hyppää",
tulos "ei") ja seuraavan silmukan ensimmäisellä kierroksella (ennuste
"ei", tulos "hyppää").

**Kaksibittinen** ennustin on kyllästyvä laskuri 0..3. Toteutuminen
kasvattaa ja toteutumattomuus pienentää laskuria, ja arvot 2 ja 3
ennustavat hypyn:

| Tila | Ennuste | Toteutui → | Ei toteutunut → |
|------|---------|------------|-----------------|
| 0 (vahva ei) | ei hypätä | 1 | 0 |
| 1 (heikko ei) | ei hypätä | 2 | 0 |
| 2 (heikko kyllä) | hypätään | 3 | 1 |
| 3 (vahva kyllä) | hypätään | 3 | 2 |

Yksi poikkeus ei käännä vahvaa ennustetta: silmukan viimeinen kierros
siirtää laskurin 3:sta 2:een, ja seuraava silmukka ennustetaan heti
oikein. Kaksibittinen laskuri on J. E. Smithin vuonna 1981 kuvaama
rakenne, ja se on yhä kaikkien monimutkaisempien ennustimien
rakennuspalikka.

## Mittaus

Esimerkki ajaa jokaisen testiohjelman kuudella ennustimella. Jokainen
ohjelma saa uuden ennustimen, jotta tila ei periydy edellisestä
(gshare-ennustin esitellään alempana). Lopuksi se laskee, montako eri
haarakäskyä ohjelmissa on ja kuinka usein ne toteutuvat:

```{.cpp tiedosto="esimerkit/05-ennustimet.cpp" osa="haarat"}
```

```{.tuloste tiedosto="esimerkit/05-ennustimet.odotettu"}
```

![Ennustimien tarkkuus ohjelmittain (tulosteen ensimmäinen taulukko).
Katkoviiva on kolikonheiton taso.](kuvat/ennustimet.png){width=80%}

Tulosten tulkinta:

- **Silmukat ovat helppoja.** `summa`- ja `lista`-ohjelmissa melkein
  kaikki haarat ovat silmukan loppuhaaroja, ja jo BTFN osuu 98–99 %.
  "Aina ei" on lähes aina väärässä.
- **Datasta riippuvat haarat ovat vaikeita.** `kupla`-ohjelman
  vertailuhaara riippuu satunnaisista arvoista. Mikään paikallinen
  ennustin ei pääse yli 83 %:n, ja CPI jää 1,2:een.
- **Kaksibittinen voittaa yksibittisen** silloin, kun haarat
  toteutuvat enimmäkseen samaan suuntaan pienin poikkeuksin
  (`kupla`, `matriisi`).
- **Jakaminen** (*aliasing*). Rivi "2-bittinen (1)" käyttää yhtä
  laskuria kaikille haaroille. Kun ohjelmassa on vähän haaroja, jotka
  käyttäytyvät samoin, haitta on pieni, mutta `kupla`-ohjelmassa
  vertailuhaara ja silmukkahaarat sotkevat toistensa tilan (82 % → 76 %).

## Korrelaatio ja globaali historia

`fib`-ohjelmassa on vain yksi haara, `blt a0, t0, pieni`, ja se toteutuu
täsmälleen puolet kerroista. Staattiset ennusteet ja kaksibittinen
laskuri jäävät 50 %:iin, koska haaran oma historia ei kerro juuri
mitään: suunta riippuu rekursion syvyydestä. Yksibittinen ennustin
pääsee 62 %:iin, koska se ennustaa edellisen suunnan ja rekursiopuussa
sama suunta toistuu hieman useammin kuin vaihtuu. Sekin on kaukana
silmukkaohjelmien 97–99 %:sta.

Haarojen suunnat kuitenkin *korreloivat* keskenään. Rekursiopuussa
lehteä (toteutuva haara) seuraa usein toinen lehti tai sisäsolmu
säännöllisessä kuviossa. **Globaali historia** on siirtorekisteri,
johon jokaisen haaran suunta lisätään bittinä. **gshare**-ennustin
(McFarling 1993) indeksoi laskuritaulukkoa historian ja PC:n
XOR-yhdistelmällä, joten sama haara saa eri laskurin eri historioilla:

```{.cpp tiedosto="esimerkit/05-ennustimet.cpp" osa="gshare"}
```

`fib`-ohjelmassa gshare nostaa tarkkuuden 50 %:sta 91 %:iin. Hinta
näkyy muualla: historia levittää yhden haaran usealle laskurille, joten
oppiminen kestää kauemmin ja taulukko täyttyy nopeammin. Lyhyissä
silmukkaohjelmissa (`summa`, `lista`) gshare on huonompi kuin
paikallinen laskuri.

Siksi oikeat suorittimet yhdistävät ennustimia. **Turnausennustin**
(*tournament*, Alpha 21264) pitää rinnakkain paikallista ja globaalia
ennustinta sekä kolmatta laskuria, joka valitsee kummankin haaran
kohdalla paremmin onnistuneen. **TAGE** (Seznec 2006) käyttää useita
taulukoita eri pituisilla historioilla ja valitsee pisimmän osuvan;
se ja sen johdannaiset ovat nykyisten suorittimien perusta. AMD:n
Zen-ytimissä on lisäksi perseptroniin perustuva ennustin. Hyvä
nykyennustin saavuttaa tyypillisissä ohjelmissa 95–99 %:n tarkkuuden.

## Hypyt ja paluut

`fib`-ohjelman CPI jää gsharenkin kanssa 1,43:een. Syy ei ole
haaroissa vaan kutsuissa ja paluissa. Mallissa `jalr` ratkeaa
EX-vaiheessa ja maksaa aina kaksi jaksoa, ja jokaisessa kutsussa on
kaksi `jalr`-käskyä (`call` ja `ret`). 3 193 kutsua × 2 käskyä × 2 jaksoa
= 12 772 jaksoa eli 0,36 CPI:tä.

Oikeat suorittimet ratkaisevat tämän kahdella rakenteella:

- **Paluuosoitepino** (RAS, *return address stack*): `call` työntää
  paluuosoitteen pieneen laitteistopinoon, ja `ret` ennustetaan pinon
  päällimmäiseksi. Ennuste on lähes aina oikein, kunhan rekursio ei ole
  syvempi kuin pino (tyypillisesti 16–32 alkiota). RISC-V:n
  spesifikaatio kertoo, mitkä `jal`- ja `jalr`-käytöt ovat kutsuja ja
  paluita (rd tai rs1 on `ra`), jotta laitteisto osaa käyttää pinoa.
- **Epäsuorien hyppyjen ennustin**: virtuaalifunktiot, `switch`-taulut
  ja tulkkien käskysilmukka hyppäävät rekisterin osoittamaan paikkaan.
  BTB muistaa viimeisimmän kohteen, ja historiaa käyttävä ennustin
  (ITTAGE) erottaa eri kohteet eri tilanteissa.

## Käytännössä

- **Ennustettavat haarat ovat halpoja, ennustamattomat kalliita.**
  Haaran hinta ei riipu siitä, toteutuuko se, vaan siitä, ennustetaanko
  se oikein. Klassinen esimerkki: lajitellun taulukon läpikäynti
  ehtolauseella on moninkertaisesti nopeampi kuin lajittelemattoman.
- **Haaraton koodi.** Ennustamattoman haaran voi korvata ehdollisella
  siirrolla (`cmov`, RISC-V:n Zicond-laajennuksen `czero`), maskeilla tai
  taulukkohaulla. Kääntäjä tekee tämän usein itse; tarkista
  disassemblysta.
- **Mittaa haarojen ohiennustukset.** Linuxissa `perf stat -e
  branches,branch-misses` kertoo ohjelman ohiennustusosuuden. Yli
  5 %:n osuus kertoo yleensä datasta riippuvista haaroista kuumassa
  silmukassa.
- **Ennustus on tietoturvariski.** Spectre-hyökkäykset (2018)
  kouluttavat ennustimen ohjaamaan uhrin spekulatiivisen suorituksen
  polulle, joka vuotaa salaisuuden välimuistin tilaan. Väärän polun
  käskyt eivät muuta arkkitehtuurista tilaa, mutta ne muuttavat
  mikroarkkitehtuurista. Katso luku 11.

## Itsearviointi

- Osaat laskea haarautumisen vaikutuksen CPI:hin haarojen osuudesta,
  ennustustarkkuudesta ja virheen hinnasta.
- Osaat simuloida kaksibittisen laskurin käsin silmukalle ja selittää,
  miksi se voittaa yksibittisen.
- Osaat selittää globaalin historian ja gsharen indeksoinnin sekä
  sen, milloin se auttaa ja milloin haittaa.
- Osaat kertoa, mitä BTB ja paluuosoitepino ennustavat ja miksi suunnan
  ennustin ei yksin riitä.
