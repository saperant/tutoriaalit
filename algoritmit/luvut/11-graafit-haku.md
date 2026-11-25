# Leveys- ja syvyyshaku

Graafialgoritmien perusta on graafin läpikäynti: kaikkien solmujen
löytäminen, joihin lähtösolmusta pääsee. Läpikäyntejä on kaksi, ja ne
eroavat vain siinä, missä järjestyksessä löydetyt solmut käsitellään.
*Leveyshaku* (engl. breadth-first search, BFS) käsittelee ne
löytymisjärjestyksessä jonosta, *syvyyshaku* (engl. depth-first search,
DFS) viimeksi löydetyn ensin pinosta tai rekursiolla. Järjestyksen ero
antaa niille eri ominaisuudet: leveyshaku löytää lyhimmät polut,
syvyyshaku rakenteen, kuten syklit ja topologisen järjestyksen.

Molemmat ovat $\Theta(n + m)$ vierekkäisyyslistoilla, kun solmuja on
$n$ ja kaaria $m$: jokainen solmu käsitellään kerran ja jokainen kaari
katsotaan kerran (suuntaamattomassa graafissa kahdesti). Graafin
esitystavat ovat tietorakenteiden luvussa 10 ja graafien käsitteet
diskreetin matematiikan luvussa 10. Tämän luvun esimerkit käyttävät
pieniä graafeja, joiden esitys on mahdollisimman yksinkertainen:
ruutukartta ja vierekkäisyysmatriisi.

## Leveyshaku ja lyhin reitti

Robotti kulkee varaston käytäviä ruudusta naapuriruutuun, ja jokainen
siirto vie saman ajan. Mikä on lyhin reitti lähtöruudusta A
kohteeseen B? Kartta on graafi: ruudut ovat solmuja ja vierekkäiset
vapaat ruudut kaaria. Koska kaikilla kaarilla on sama paino,
leveyshaku ratkaisee tehtävän:

```{.c tiedosto="esimerkit/11-reitti.c" osa="bfs"}
```

Leveyshaku käsittelee solmut etäisyyden mukaan kasvavassa
järjestyksessä. Jonossa on aina ensin etäisyyden $d$ solmuja ja niiden
perässä etäisyyden $d + 1$ solmuja, koska jokainen solmu lisää jonon
loppuun vain naapureitaan, joiden etäisyys on yhtä suurempi. Kun solmu
löydetään ensimmäisen kerran, sen etäisyys on siis lopullinen, ja
etäisyystaulukko toimii myös merkintänä käsitellyistä solmuista.
Jokainen ruutu lisätään jonoon enintään kerran, joten jono mahtuu
ruutujen määrän kokoiseen taulukkoon.

Reitti saadaan *edeltäjätaulukosta*: jokaiselle ruudulle tallennetaan
ruutu, josta se löydettiin. Kohteesta kuljetaan edeltäjiä takaisin
lähtöön, ja polku piirretään kartalle tähdillä:

```{.tuloste tiedosto="esimerkit/11-reitti.odotettu"}
```

Haku lopetetaan, kun kohde otetaan jonosta. Tässä kartassa se
tapahtuu vasta, kun 82 kartan 95 vapaasta ruudusta on käsitelty, koska
kohde on kaukana. Avoimessa maastossa leveyshaku tutkii laajenevan ympyrän
kaikkiin suuntiin. A*-haku, joka on Dijkstran algoritmi (luku 12)
etäisyysarviolla täydennettynä, ohjaa haun kohti maalia, ja sitä
käytetään peleissä ja navigoinnissa.

Leveyshaku on oikea työkalu aina, kun kaikki askeleet maksavat saman
verran: pienin määrä siirtoja palapelissä, lyhin ystäväketju
sosiaalisessa verkostossa tai verkon reitittimien hyppyjen määrä.

## Syvyyshaku ja syklit

Syvyyshaku etenee niin syvälle kuin pääsee ja palaa vasta umpikujasta.
Rekursiivisena se on lyhyt, ja sen tärkein lisätieto on solmun *väri*:

- **Valkoinen:** solmua ei ole vielä löydetty.
- **Harmaa:** solmu on rekursiopinossa; sen jälkeläisiä käydään läpi.
- **Musta:** solmu ja kaikki siitä saavutettavat on käsitelty.

Suunnatussa graafissa kaari harmaaseen solmuun palaa pinossa olevaan
esi-isään ja sulkee syklin. Kaari mustaan solmuun ei sulje sykliä:
mustasta solmusta saavutettavat solmut on jo käsitelty loppuun, eikä
niistä ole polkua pinossa oleviin solmuihin, koska sykli olisi
muuten löytynyt jo silloin. Pelkkä "käyty"-merkintä ei siksi riitä
syklin tunnistamiseen: se ei erota harmaata solmua mustasta.

```{.c tiedosto="esimerkit/11-kaannos.c" osa="sykli"}
```

Kun sykli löytyy, sen solmut luetaan edeltäjätaulukosta kulkemalla
takaisin harmaaseen solmuun, ja järjestys käännetään kaarten
suuntaiseksi. Virheilmoitus, joka kertoo syklin, on paljon hyödyllisempi
kuin pelkkä "riippuvuuksissa on sykli".

Rekursiivisen syvyyshaun syvyys voi olla $n$, mikä on ongelma suurilla
graafeilla, kuten luvussa 2 todettiin. Pitkille poluille syvyyshaku
kirjoitetaan omalla pinolla.

## Topologinen järjestys

Käännösjärjestelmä tietää, mistä kukin tiedosto riippuu: objekti
`lista.o` tehdään lähdetiedostosta `lista.c` ja otsakkeesta
`asetukset.h`, ohjelma objekteista ja niin edelleen. Missä
järjestyksessä vaiheet tehdään? Riippuvuudet ovat suunnattu graafi,
jossa kaari $u \to v$ tarkoittaa, että $u$ on tehtävä ennen $v$:tä.
*Topologinen järjestys* on solmujen järjestys, jossa jokainen kaari
osoittaa eteenpäin. Se on olemassa täsmälleen silloin, kun graafissa
ei ole suunnattua sykliä.

```{.c tiedosto="esimerkit/11-kaannos.c" osa="projekti"}
```

```{.dot otsikko="Esimerkin riippuvuusgraafi: kaari kulkee edellytyksestä tulokseen"}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.5;
  node [fontname="DejaVu Sans Mono", fontsize=9];
  "asetukset.h" -> "lista.o"; "asetukset.h" -> "main.o";
  "lista.c" -> "lista.o"; "main.c" -> "main.o";
  "lista.o" -> ohjelma; "main.o" -> ohjelma;
  "testit.c" -> "testit.o"; "lista.o" -> testaa; "testit.o" -> testaa;
}
```

Kahnin algoritmi pitää kirjaa jokaisen solmun käsittelemättömien
edeltäjien määrästä (*tuloaste*). Solmut, joiden tuloaste on nolla,
voidaan tehdä heti, ja ne laitetaan jonoon. Kun solmu otetaan jonosta,
sen seuraajien tuloaste pienenee, ja nollaan pudonneet lisätään
jonoon:

```{.c tiedosto="esimerkit/11-kaannos.c" osa="kahn"}
```

```{.tuloste tiedosto="esimerkit/11-kaannos.odotettu"}
```

Ensimmäinen järjestys on yksi monista kelvollisista: lähdetiedostot
ensin, sitten objektit ja lopuksi ohjelma ja testit. Jonon sisältö on
myös rinnakkaistuksen perusta: kaikki jonossa yhtä aikaa olevat
vaiheet ovat toisistaan riippumattomia, ja `make -j` voi ajaa ne
rinnakkain.

Kun riippuvuuksiin lisätään virheellinen kaari ohjelmasta
otsakkeeseen, Kahn käsittelee vain ne neljä solmua, jotka eivät
riipu syklistä, ja jättää loput. Järjestyksen vajaus kertoo, että
sykli on olemassa; syvyyshaku kertoo, mikä se on. Topologisen
järjestyksen saa myös syvyyshausta: kun solmut kirjoitetaan siinä
järjestyksessä, jossa ne muuttuvat mustiksi, ja lista käännetään,
jokainen kaari osoittaa eteenpäin.

Satunnaistesti tuottaa 1000 suunnattua graafia, joista kaksi
kolmasosaa on syklisiä. Jokaisesta tarkistetaan kolme asiaa: Kahn ja
syvyyshaku ovat samaa mieltä syklin olemassaolosta, löydetyn syklin
jokainen kaari on graafissa, ja täydellisessä järjestyksessä jokainen
kaari osoittaa eteenpäin. Tarkistukset ovat riippumattomia
toteutuksesta, joten ne löytäisivät virheen kummasta tahansa
algoritmista.

## Komponentit

Syvyyshaun toinen pääsovellus on graafin jakaminen osiin.
Suuntaamattomassa graafissa *yhtenäinen komponentti* on joukko solmuja,
joiden välillä on polku. Komponentit löytyvät käynnistämällä haku
vuorotellen jokaisesta vielä löytämättömästä solmusta: jokainen
käynnistys löytää täsmälleen yhden komponentin.

Suunnatussa graafissa vastaava käsite on *vahvasti yhtenäinen
komponentti* (engl. strongly connected component): suurin joukko
solmuja, joissa jokaisesta pääsee jokaiseen. Edellisen osion
riippuvuussykli on tällainen komponentti. Kun jokainen komponentti
kutistetaan yhdeksi solmuksi, jäljelle jää syklitön graafi, jolla on
topologinen järjestys.

Kosarajun algoritmi löytää komponentit kahdella syvyyshaulla.
Ensimmäinen kirjaa solmut siinä järjestyksessä, jossa ne valmistuvat
(muuttuvat mustiksi). Toinen käy solmut läpi käänteisessä
valmistumisjärjestyksessä ja kulkee kaaria *vastaan*; jokainen
käynnistys merkitsee yhden komponentin. Perustelu: viimeksi valmistunut
solmu kuuluu komponenttiin, johon mikään muu komponentti ei johda
käännetyssä graafissa, joten haku ei voi vuotaa siitä ulos.

```{.c tiedosto="esimerkit/11-komponentit.c" osa="kosaraju"}
```

Esimerkin graafi on palvelujen kutsusuhteet. Komponentti, jossa on
useampi palvelu, on kutsusykli: sen palveluja ei voi käynnistää,
päivittää tai testata toisistaan riippumatta.

```{.c tiedosto="esimerkit/11-komponentit.c" osa="palvelut"}
```

```{.tuloste tiedosto="esimerkit/11-komponentit.odotettu"}
```

```{.dot tiedosto="kaaviot/komponentit.dot" otsikko="Kutsugraafin vahvasti yhtenäiset komponentit (esimerkin datasta ja tulosteesta). Komponenttien numerot ovat topologisessa järjestyksessä."}
```

Komponentit numeroituvat topologiseen järjestykseen: jokainen
komponenttien välinen kaari kulkee pienemmästä numerosta suurempaan.
Testi vertaa tulosta määritelmään 500 satunnaisella graafilla: kaksi
solmua ovat samassa komponentissa täsmälleen silloin, kun kumpikin on
saavutettavissa toisesta. Saavutettavuus lasketaan erikseen
transitiivisena sulkeumana. Esimerkki käyttää vierekkäisyysmatriisia,
jotta kaaren kääntäminen on pelkkä indeksien vaihto; listoilla aika on
$O(n + m)$, kun käännetty graafi rakennetaan erikseen. Tarjanin
algoritmi tekee saman yhdellä haulla.

## Käytännössä

- **Leveyshaku painottomille lyhimmille poluille.** Jos kaikki kaaret
  maksavat saman verran, Dijkstra on turha; jono riittää.
- **Merkitse solmu käsitellyksi, kun se lisätään jonoon.** Muuten sama
  solmu voi päätyä jonoon monta kertaa, ja jonon koko kasvaa
  kaarten määrän mukaiseksi.
- **Kolme väriä syklin etsintään.** Kaari harmaaseen solmuun on sykli;
  kaari mustaan ei ole.
- **Kerro sykli, älä vain sen olemassaoloa.** Edeltäjätaulukko antaa
  syklin solmut, ja käyttäjä voi korjata riippuvuuden.
- **Sykli on komponentti.** Vahvasti yhtenäiset komponentit kertovat
  kaikki riippuvuussyklit kerralla, ja kutistettu graafi on aina
  järjestettävissä.
- **Kahn rinnakkaistaa.** Jonossa olevat solmut ovat riippumattomia, ja
  niiden määrä kertoo, montako työtä voi ajaa yhtä aikaa.

## Itsearviointi

- Osaat kirjoittaa leveyshaun, joka palauttaa lyhimmän reitin
  edeltäjätaulukosta, ja perustella, miksi löydetty etäisyys on
  lopullinen.
- Osaat tunnistaa syklin suunnatussa graafissa kolmen värin
  syvyyshaulla ja tulostaa syklin solmut.
- Osaat muodostaa topologisen järjestyksen Kahnin algoritmilla ja
  syvyyshaun valmistumisjärjestyksestä.
- Osaat etsiä suunnatun graafin vahvasti yhtenäiset komponentit
  kahdella syvyyshaulla ja selittää, mitä ne kertovat sykleistä.
- Osaat valita leveyshaun, syvyyshaun ja painotetun haun välillä
  tehtävän mukaan.
