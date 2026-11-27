# SSA-muoto

Luvun 11 arvonumerointi toimi vain yhden peruslohkon sisällä, ja
syy oli välikielen muoto. Sama rekisteri voi saada arvon monessa
paikassa: silmukkamuuttuja `i` kirjoitetaan ennen silmukkaa ja
jokaisella kierroksella. Kun optimointi näkee käskyn
`%5 = rem i, %4`, se ei tiedä, *mikä* kirjoitus `i`:hin on voimassa,
ilman luvun 10 kaltaista analyysiä koko graafin yli. **SSA-muoto**
(*static single assignment*) poistaa tämän ongelman: jokainen rekisteri kirjoitetaan ohjelmatekstissä tasan kerran.
Silloin rekisterin nimi kertoo sen määrittelyn, ja monet optimoinnit
muuttuvat yksinkertaisiksi.

SSA kehitettiin IBM:llä 1980-luvulla (Cytron, Ferrante, Rosen, Wegman
ja Zadeck, 1991), ja nykyään lähes kaikki optimoivat kääntäjät
käyttävät sitä: LLVM:n välikieli on aina SSA-muodossa, GCC:n GIMPLE
on SSA-muodossa optimointien ajan, ja samoin HotSpot, V8 ja Go.

## Phi-funktiot

Suoraviivaisessa koodissa SSA on helppo: jokainen kirjoitus saa uuden
version, `i.0`, `i.1`, ja käytöt viittaavat viimeisimpään. Ongelma on
yhtymäkohdissa. Silmukan alussa `i` on joko alkuarvo (ensimmäisellä
kierroksella) tai edellisen kierroksen arvo. Tätä varten SSA:ssa on
**phi-funktio**, esimerkiksi `i.1 = phi [i.0, L0], [i.2, L4]`.
Phi valitsee arvon sen mukaan, mistä edeltäjästä lohkoon tultiin.
Se ei ole oikea käsky vaan merkintä, joka poistetaan ennen
koodingenerointia. Luvun 9 esimerkkifunktio `summa` (välikieli ja
ohjausvuograafi ovat siellä) on SSA-muodossa tällainen:

```{.tuloste tiedosto="esimerkit/naytteet/ssa-summa.txt"}
```

SSA-muodossa näkyy suoraan, että silmukan ehto `le i.1, n.0` käyttää
phin tulosta ja että `s` kulkee lohkon L4 phin kautta, koska lohkosta
L3 ja lohkosta L2 tullaan L4:ään eri arvoilla. Väliaikaiset rekisterit
`%3`–`%9` kirjoitettiin jo valmiiksi kerran, joten ne säilyttävät
nimensä.

Muunnos tehdään kahdessa vaiheessa: ensin päätetään, *mihin* phit
tarvitaan, ja sitten nimetään rekisterit uudelleen. Molemmat perustuvat
dominanssiin.

## Dominanssi

Lohko A **dominoi** lohkoa B, jos jokainen polku alkulohkosta B:hen
kulkee A:n kautta. Alkulohko dominoi kaikkia lohkoja, ja jokainen lohko
dominoi itseään. B:n **välitön dominoija** (*immediate dominator*,
idom) on sen lähin aito dominoija, ja välittömät dominoijat muodostavat
**dominanssipuun**.

Dominoijat lasketaan Cooperin, Harveyn ja Kennedyn iteratiivisella
algoritmilla. Lohkot käydään käänteisessä jälkijärjestyksessä, ja
kunkin lohkon idom on sen edeltäjien idomien "lähin yhteinen esi-isä"
dominanssipuussa. Kierroksia toistetaan, kunnes mikään ei muutu:

```{.cpp tiedosto="esimerkit/kide/ssa.cpp" osa="dominoijat"}
```

Algoritmi on yksinkertainen ja käytännössä nopea; teoreettisesti
parempi Lengauerin ja Tarjanin algoritmi (1979) on monimutkaisempi ja
voittaa vasta hyvin suurissa graafeissa.

## Dominanssiraja

Jos lohkossa B kirjoitetaan `x`, kirjoitus on voimassa kaikissa
lohkoissa, joita B dominoi. Siellä, missä B:n dominanssi *päättyy*,
B:n arvo kohtaa muita polkuja, ja tarvitaan phi. Nämä lohkot ovat B:n
**dominanssiraja** DF(B): lohkot, joiden jotakin edeltäjää B dominoi
mutta joita B ei itse aidosti dominoi.

```{.cpp tiedosto="esimerkit/kide/ssa.cpp" osa="raja"}
```

Esimerkkifunktion dominanssipuu ja rajat (`--vaihe=dominanssi`):

```{.tuloste tiedosto="esimerkit/naytteet/dominanssi-summa.txt"}
```

```{.dot tiedosto="kaaviot/dominanssi-summa.dot" otsikko="Dominaattoripuu: kunkin lohkon vanhempi on sen välitön dominaattori" leveys="30%"}
```

L3 (jossa `s` kasvaa) ei dominoi L4:ää, koska L4:ään pääsee myös
suoraan L2:sta; siksi DF(L3) = {L4}, ja L4 tarvitsee phin muuttujalle
`s`. Silmukan runkolohkojen rajalla on silmukan otsake L1, johon
paluukaari tuo arvot.

## Phien sijoittaminen

Jokaiselle rekisterille kerätään lohkot, joissa se kirjoitetaan, ja
phi lisätään niiden dominanssirajalle. Phi on itsekin kirjoitus, joten
sen lohkon raja käsitellään vuorostaan (iteroitu dominanssiraja):

```{.cpp tiedosto="esimerkit/kide/ssa.cpp" osa="phit"}
```

Minimaalinen SSA lisäisi phin jokaiseen rajan lohkoon. Tämä toteutus
tekee **karsitun SSA:n** (*pruned SSA*): phi lisätään vain, jos
rekisteri on elävä lohkon alussa, eli sen arvoa vielä luetaan.
Elävyys lasketaan luvun 10 analyysillä. Ilman karsintaa esimerkiksi
silmukan rungossa esitellylle väliaikaiselle muuttujalle syntyisi
silmukan otsakkeeseen turha phi.

## Uudelleennimeäminen

Lopuksi rekisterit nimetään uudelleen kulkemalla dominanssipuu
syvyyshakuna. Kullekin alkuperäiselle rekisterille pidetään pinoa sen
versioista; pinon päällimmäinen on se määrittely, joka dominoi nykyistä
kohtaa. Lohkon käsittelyn lopuksi täytetään seuraajien phien
argumentit tämän lohkon kautta tulevilla versioilla, ja lapsien jälkeen
pinoista poistetaan tässä lohkossa lisätyt versiot:

```{.cpp tiedosto="esimerkit/kide/ssa.cpp" osa="nimea"}
```

## Mitä SSA-muodolla tehdään

SSA-muodossa rekisterin nimi yksilöi sen määrittelyn, joten moni
koko funktion analyysi muuttuu taulukkohauksi:

- **Vakioiden eteneminen.** Jos `x.1` on vakio, jokainen `x.1`:n käyttö
  on sama vakio. Tieto tallennetaan kerran nimeä kohden eikä erikseen
  jokaiseen lohkoon.
- **Globaali arvonumerointi.** Luvun 11 arvonumerointi unohti taulunsa
  lohkon lopussa, koska rekisteri saattoi muuttua toisessa lohkossa.
  SSA-muodossa se ei voi muuttua, joten dominoivassa lohkossa laskettu
  lauseke on voimassa kaikissa sen dominoimissa lohkoissa.
- **Kuolleen koodin poisto.** Määrittely, jolla ei ole käyttöjä, on
  kuollut. Käytöt löytyvät määrittely–käyttö-ketjusta ilman
  elävyysanalyysiä.

Kide tekee nämä kolme optimointia valinnalla `-O2`, ja luku 13 käy ne
läpi. Suoritin ei tunne phi-funktioita, joten optimoinnin jälkeen
SSA-muodosta on palattava tavalliseen välikieleen; se on luvun 14 aihe.
Oletustasolla `-O1` SSA-muotoa ei käytetä käännöksessä, ja
`--vaihe=ssa` vain näyttää sen.

## Käytännössä

- **Optimoivan kääntäjän välikieli kannattaa pitää SSA-muodossa.**
  Määrittely–käyttö-ketjut ovat silloin suoria viitteitä, ja vakioiden
  eteneminen, kuolleen koodin poisto ja arvonumerointi koko funktion
  yli ovat yksinkertaisia.
- **Käytä karsittua tai puolikarsittua SSA:ta.** Minimaalinen SSA
  tuottaa paljon kuolleita phejä, joita myöhemmät vaiheet joutuvat
  siivoamaan.
- **Dominanssi on hyödyllinen muuallakin.** Silmukat tunnistetaan
  paluukaarista, joiden kohde dominoi lähdettä; silmukasta riippumaton
  koodi siirretään lohkoon, joka dominoi silmukkaa.
- **Rakenna SSA valmiista osista.** Dominoijat, dominanssiraja ja
  elävyys ovat erillisiä, testattavia analyysejä; SSA-muunnos on
  niiden yhdistelmä.

## Itsearviointi

- Osaat selittää SSA-muodon ja phi-funktion ja muuntaa pienen
  funktion käsin SSA-muotoon.
- Osaat määritellä dominanssin, välittömän dominoijan ja
  dominanssirajan ja laskea ne pienestä ohjausvuograafista.
- Osaat selittää, miksi phit sijoitetaan iteroidulle
  dominanssirajalle ja mitä karsittu SSA karsii.
- Osaat selittää, miksi vakioiden eteneminen, arvonumerointi ja
  kuolleen koodin poisto yksinkertaistuvat SSA-muodossa.
