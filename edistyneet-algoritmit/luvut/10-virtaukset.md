# Verkkovirtaukset

*Virtausverkko* on suunnattu verkko, jonka jokaisella kaarella on
*kapasiteetti*: kuinka paljon tavaraa, dataa tai vettä kaari voi
kuljettaa aikayksikössä. Kysymys kuuluu: kuinka paljon *lähteestä* $s$
voidaan lähettää *nieluun* $t$? Virran on noudatettava kahta
ehtoa. Kaaren virta on enintään sen kapasiteetti, ja jokaiseen
välisolmuun tulee yhtä paljon kuin sieltä lähtee.

Maksimivirtaus on yllättävän yleinen malli. Paritus, aikataulutus,
kuvan segmentointi, verkon luotettavuus ja projektien valinta
palautuvat siihen. Lisäksi se on *duaali* minimileikkaukselle: pienin
kokonaiskapasiteetti, jonka poistaminen erottaa $t$:n $s$:stä, on yhtä
suuri kuin suurin virta.

## Jäännösverkko ja lisäyspolut

Ahne yritys etsiä polku $s \to t$, lähettää sitä pitkin niin paljon
kuin mahtuu ja toistaa, jää usein vajaaksi. Varhainen huono valinta
voi tukkia paremman reitin. *Jäännösverkko* korjaa tämän. Jokaisella
kaarella $u \to v$, jolla kulkee virta $f$, on jäännöskapasiteetti
$c - f$ eteenpäin ja $f$ taaksepäin. Takaperin kulkeva *vastakaari*
tarkoittaa virran perumista. *Lisäyspolku* on $s \to t$-polku
jäännösverkossa, ja Fordin–Fulkersonin menetelmä lisää virtaa
lisäyspolkuja pitkin, kunnes niitä ei enää ole.

Toteutuksessa kaari ja sen vastakaari tallennetaan pareittain
indekseihin $e$ ja $e \oplus 1$. Vastakaaren virta on aina
alkuperäisen kaaren virran vastaluku, joten molempien
jäännöskapasiteetit saadaan samasta tiedosta:

```{.cpp tiedosto="esimerkit/virtaus.hpp" osa="verkko"}
```

## Edmonds–Karp

Fordin–Fulkersonin menetelmä ei kerro, mikä lisäyspolku valitaan.
Huono valinta voi kokonaislukukapasiteeteilla viedä virran arvon
verran kierroksia, ja irrationaalisilla kapasiteeteilla menetelmä ei
välttämättä pääty lainkaan. *Edmondsin–Karpin* algoritmi (1972)
valitsee aina lyhimmän polun leveyshaulla. Silloin jokaisen solmun
etäisyys lähteestä on kasvava, ja jokainen kaari voi olla polun
pullonkaula enintään $V/2$ kertaa. Polkuja on siis $O(VE)$, ja aika
on $O(VE^2)$.

```{.cpp tiedosto="esimerkit/virtaus.hpp" osa="ek"}
```

## Dinic

*Dinicin* algoritmi (1970) tekee kerralla kaikki samanpituiset
lisäykset. Leveyshaku jakaa solmut tasoihin etäisyyden mukaan.
Syvyyshaku lähettää virtaa vain tasolta seuraavalle, kunnes tasoverkossa
ei ole enää polkua. Tämä on *estävä virta*. Jokainen vaihe kasvattaa
lyhimmän lisäyspolun pituutta, joten vaiheita on enintään $V$.
Syvyyshaun osoitin `seuraava_` muistaa umpikujaan johtaneet kaaret,
joten vaihe vie ajan $O(VE)$ ja koko algoritmi $O(V^2 E)$.
Yksikkökapasiteeteilla ja kaksijakoisissa verkoissa raja on
$O(E\sqrt{V})$. Käytännössä Dinic on lähes aina selvästi nopeampi kuin
Edmonds–Karp.

```{.cpp tiedosto="esimerkit/virtaus.hpp" osa="dinic"}
```

## Minimileikkaus

*Leikkaus* $(S, T)$ jakaa solmut kahteen osaan niin, että $s \in S$ ja
$t \in T$. Sen kapasiteetti on $S$:stä $T$:hen kulkevien kaarten
kapasiteettien summa. Jokainen virta kulkee jokaisen leikkauksen
läpi, joten virta on enintään pienimmän leikkauksen kapasiteetti.
*Max-flow min-cut -lause* (Ford ja Fulkerson 1956) sanoo, että raja
saavutetaan. Kun lisäyspolkuja ei enää ole, $s$:stä jäännösverkossa
saavutettavat solmut muodostavat $S$:n. Jokainen $S$:stä $T$:hen
kulkeva kaari on täynnä, ja jokainen $T$:stä $S$:ään kulkeva on tyhjä.

```{.cpp tiedosto="esimerkit/virtaus.hpp" osa="leikkaus"}
```

Lause antaa myös mallin vertailutestille. Pienessä verkossa voidaan
käydä läpi kaikki $2^{n-2}$ leikkausta ja verrata pienintä niistä
kummankin algoritmin tulokseen:

```{.cpp tiedosto="esimerkit/10-virtaus.cpp" osa="raaka"}
```

Esimerkkiverkko kuvaa konesalien välisiä yhteyksiä. Kuinka nopeasti
varmuuskopiot voidaan siirtää A:sta F:ään, ja mitkä yhteydet ovat
pullonkaula? Kapasiteetit ovat Gbit/s: A–B 10, A–C 10, B–C 2, B–D 4,
B–E 8, C–E 9, E–D 6, D–F 10 ja E–F 10.

```{.tuloste tiedosto="esimerkit/10-virtaus.odotettu"}
```

```{.dot tiedosto="kaaviot/virtaus-leikkaus.dot" otsikko="Konesaliverkon maksimivirta 19 ja sen todistava minimileikkaus (virta/kapasiteetti; leikkauksen kaaret punaisina; esimerkin tulosteesta)"}
```

Kuvassa näkyy max-flow min-cut -lauseen sisältö: leikkauksen kaaret
A–B ja C–E ovat täynnä, ja ainoa $T$:stä $S$:ään kulkeva kaari B–C on
tyhjä. Leikkaus kertoo, mitä yhteyksiä kannattaa vahvistaa: niin kauan kuin
yhteydet A–B ja C–E pysyvät ennallaan, virta ei voi kasvaa yli
19 Gbit/s, vaikka muita yhteyksiä vahvistettaisiin. Se kertoo myös,
mitkä yhteydet ovat kriittisiä luotettavuuden kannalta.

## Kaksijakoinen paritus

Opiskelijat toivovat aiheita, ja jokainen aihe annetaan enintään
yhdelle opiskelijalle. Kuinka moni saa aiheen? Tehtävä on *suurin
paritus* kaksijakoisessa verkossa. *Kuhnin* algoritmi etsii jokaiselle
vasemmalle solmulle *lisäyspolun*, joka vuorottelee parittomia ja
paritettuja kaaria ja päättyy vapaaseen oikeaan solmuun. Polun kaarten
vaihtaminen kasvattaa paritusta yhdellä. Bergen lauseen mukaan
paritus on suurin, kun lisäyspolkuja ei ole.

```{.cpp tiedosto="esimerkit/10-paritus.cpp" osa="kuhn"}
```

Sama tehtävä on virtaus. Lähteestä kulkee kaari kuhunkin vasempaan
solmuun, toiveista tulee kaaria vasemmalta oikealle ja jokaisesta
oikeasta solmusta kulkee kaari nieluun, kaikki kapasiteetiltaan 1.
Kokonaislukukapasiteeteilla on aina olemassa kokonaislukuinen suurin
virta, ja lisäyspolkualgoritmit löytävät sellaisen, joten virta on
paritus. Dinicin algoritmi tekee tästä *Hopcroftin–Karpin* algoritmin,
jonka aika on $O(E \sqrt{V})$. Esimerkin funktio `virtauksena()`
rakentaa tämän verkon ja ratkaisee sen luvun alun Dinicin algoritmilla.

## Königin lause

Kun paritus ei kata kaikkia, syy kannattaa osata selittää.
*Solmupeite* on solmujoukko, joka koskettaa jokaista kaarta. Jokainen
parituksen kaari tarvitsee oman peitesolmunsa, joten peite on aina
vähintään parituksen kokoinen. *Königin lauseen* mukaan kaksijakoisessa
verkossa pienin peite on täsmälleen suurimman parituksen kokoinen.
Peite saadaan suurimmasta parituksesta. Ensin etsitään solmut $Z$,
jotka saavutetaan vapaista vasemmista solmuista vuorottelevilla
poluilla. Peite on silloin $(L \setminus Z) \cup (R \cap Z)$:

```{.cpp tiedosto="esimerkit/10-paritus.cpp" osa="konig"}
```

Peite on *todistus* siitä, että paritus on suurin. Vertailutesti
tarkistaa, että Kuhnin paritus, virtaus ja peite ovat samankokoisia,
että peite todella peittää kaikki kaaret ja että raaka haku ei löydä
pienempää peitettä.

```{.cpp tiedosto="esimerkit/10-paritus.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-paritus.odotettu"}
```

Kolme aihetta peittää kaikki toiveet: kukaan ei toivonut grafiikkaa,
joten viisi opiskelijaa jakaa kolme aihetta. Tällainen vastaus
kelpaa käyttäjälle paremmin kuin pelkkä luku.

## Mallinnus minimileikkauksena

Virtausalgoritmi on harvoin itse tehtävä. Työ on tunnistaa, että
tehtävän voi esittää verkkona, ja joskus vastaus on minimileikkaus
eikä virta. Leikkaus jakaa solmut kahteen joukkoon, joten se sopii
tehtäviin, joissa jokaisesta asiasta tehdään kyllä tai ei -päätös ja
päätösten välillä on riippuvuuksia.

*Projektien valinta* on tällainen tehtävä. Projekti tuottaa rahaa
mutta vaatii investointeja, ja sama investointi voi palvella useaa
projektia. Mitkä projektit kannattaa tehdä? Verkkoon tulee kaari
lähteestä jokaiseen projektiin (kapasiteettina tuotto), jokaisesta
investoinnista nieluun (hinta) ja projektista sen vaatimiin
investointeihin (ääretön). Lähteen puolelle jäävät projektit tehdään:

```{.cpp tiedosto="esimerkit/10-projektit.cpp" osa="malli"}
```

Ääretön kaari pakottaa riippuvuuden: jos projekti on lähteen puolella
ja sen investointi nielun puolella, leikkaus olisi ääretön. Äärellinen
leikkaus maksaa jokaisesta hylätystä projektista sen tuoton ja
jokaisesta tehdystä investoinnista sen hinnan, joten leikkauksen
minimointi on voiton maksimointia.

```{.cpp tiedosto="esimerkit/10-projektit.cpp" osa="esimerkki"}
```

```{.tuloste tiedosto="esimerkit/10-projektit.odotettu"}
```

Verkkokauppa (40) ja mobiilisovellus (25) jakavat maksurajapinnan ja
tunnistautumisen (yhteensä 42). Kumpikaan ei kannata yksin, mutta
yhdessä ne tuottavat 23. Raportointi ja arkistointi eivät yhdessäkään
ylitä tietovaraston hintaa. Ahne valinta projekti kerrallaan ei löydä
tätä ratkaisua. Vertailutesti käy pienissä tapauksissa läpi kaikki
projektijoukot. Sama rakenne ratkaisee kuvan jakamisen kohteeseen ja
taustaan sekä louhoksen kaivuujärjestyksen.

## Laajennuksia

- **Monta lähdettä ja nielua:** lisätään superlähde ja supernielu,
  joista on kaaret oikeisiin lähteisiin ja nieluihin.
- **Solmukapasiteetti:** solmu jaetaan kahdeksi, joiden välillä on
  kaari solmun kapasiteetilla.
- **Pienimmän kustannuksen virta:** kaarilla on myös hinta, ja
  lisäyspolkuna käytetään halvinta polkua (Bellman–Ford tai Dijkstra
  potentiaaleilla). Tämä ratkaisee *sijoitusongelman*, jossa
  painotettu paritus tehdään kustannuksiltaan pienimmäksi (vrt.
  unkarilainen menetelmä).
- **Ala- ja ylärajat:** kaaren virralle voidaan asettaa alaraja
  muuntamalla verkkoa. Aikataulutus ja kiertojen suunnittelu
  käyttävät tätä.

## Käytännössä

- Mallinna ensin, ratkaise sitten. Vaikein osa on yleensä verkon
  rakentaminen: mitä solmut ovat, mitä kaaret ovat ja mikä
  kapasiteetti kuvaa rajoitusta.
- Käytä Dinicin algoritmia oletuksena. Edmonds–Karp on helpompi
  ymmärtää, mutta harvoin riittävän nopea suurille verkoille.
- Kokonaislukukapasiteetit takaavat kokonaislukuisen ratkaisun. Älä
  muuta niitä liukuluvuiksi, jos ratkaisua tulkitaan valintoina.
- Tulosta minimileikkaus tai solmupeite virran rinnalla. Ne
  selittävät, miksi vastaus on se mikä on, ja ne ovat helppoja
  tarkistaa.
- Rekursiivinen syvyyshaku voi ylittää pinon koon miljoonien solmujen
  verkossa. Silloin syvyyshaku kirjoitetaan iteratiiviseksi tai pinon
  kokoa kasvatetaan.

## Itsearviointi

- Osaat selittää jäännösverkon ja vastakaaren merkityksen ja toteuttaa
  ne parittain tallennetuilla kaarilla.
- Osaat toteuttaa Edmondsin–Karpin ja Dinicin algoritmit ja kertoa
  niiden aikarajat ja syyn, miksi lyhin lisäyspolku takaa
  päättymisen.
- Osaat muodostaa minimileikkauksen suurimmasta virrasta ja käyttää
  max-flow min-cut -lausetta vertailutestin mallina.
- Osaat mallintaa kaksijakoisen parituksen virtauksena ja ratkaista
  sen Kuhnin algoritmilla.
- Osaat mallintaa riippuvuuksia sisältävän valintatehtävän
  minimileikkauksena ja selittää äärettömän kaaren merkityksen.
- Osaat muodostaa Königin lauseen mukaisen pienimmän solmupeitteen ja
  käyttää sitä parituksen optimaalisuuden todistuksena.
