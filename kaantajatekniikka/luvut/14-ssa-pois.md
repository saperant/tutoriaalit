# SSA-muodosta pois

Phi-funktio ei ole käsky, jonka suoritin voisi suorittaa, joten ennen
koodingenerointia phit on korvattava kopioilla. Heti SSA-muunnoksen
jälkeen se olisi helppoa: phin argumentit ovat saman muuttujan
versioita, jotka eivät ole koskaan yhtä aikaa elossa, joten
versionumerot voisi vain pudottaa. Optimointien jälkeen näin ei ole.
Arvonumerointi on korvannut rekistereitä edustajillaan, ja phin
argumenttina voi olla toisen muuttujan arvo, joka elää phin kohteen
rinnalla. Tässä luvussa phit puretaan oikein, turhat kopiot
sulautetaan pois ja mitataan, mitä luvun 13 optimoinnit tuottivat.

## Phit kopioiksi

Phi `x.1 = phi [a, L0], [b, L4]` saa arvon `a`, kun lohkoon tullaan
L0:sta, ja arvon `b`, kun tullaan L4:stä. Sama vaikutus saadaan
kopioilla edeltäjien lopussa: `x.1 = a` lohkoon L0 ja `x.1 = b`
lohkoon L4, kumpikin ennen lohkon päättävää hyppyä.

```{.cpp tiedosto="esimerkit/kide/ssapois.cpp" osa="pura"}
```

Suoraviivaisessa toteutuksessa on kaksi virhettä, jotka Briggs,
Cooper, Harvey ja Simpson kuvasivat vuonna 1998. Kumpikin tuottaa
ohjelman, joka kääntyy ja laskee väärin, ja kummallekin on testi, joka
myös ajetaan.

## Kadonnut kopio

Ensimmäinen virhe koskee kopion *paikkaa*. Testissä silmukan ehto on
rungon lopussa, ja laskurin edellistä arvoa `i.1` luetaan vielä
silmukan jälkeen:

```{.tuloste tiedosto="esimerkit/passit/kadonnut-kopio.ir"}
```

Oikea tuloste on 4. Paluukaaren kopio `i.1 = i.2` kuuluu lohkon L1
loppuun, mutta L1:stä lähtee kaksi kaarta, ja lohkon loppuun
kirjoitettu kopio suoritetaan molemmilla:

```{.tuloste tiedosto="esimerkit/passit/kadonnut-kopio-naiivi.odotettu" rivit="6-14"}
```

Silmukasta poistuttaessa `i.1` on jo ylikirjoitettu, ja ohjelma
tulostaa 5. Tämä on **kadonneen kopion ongelma** (*lost copy
problem*). Syy on **kriittinen kaari**: kaari lohkosta, jolla on
useita seuraajia, lohkoon, jolla on useita edeltäjiä. Sellaisella
kaarella ei ole paikkaa, jossa kopio suoritettaisiin vain tätä kaarta
kuljettaessa. Paikka tehdään jakamalla kaari uudella lohkolla:

```{.cpp tiedosto="esimerkit/kide/ssapois.cpp" osa="kaaret"}
```

```{.tuloste tiedosto="esimerkit/passit/kadonnut-kopio.odotettu" rivit="6-"}
```

Kopio on nyt lohkossa L3, jonka kautta kulkee vain paluukaari, ja
ohjelma tulostaa 4. Kiden välikielessä kriittisiä kaaria syntyy
tavallisesta koodista: `if`-lause ilman `else`-haaraa tuottaa kaaren
ehdosta suoraan lauseen jälkeiseen lohkoon.

## Vaihto

Toinen virhe koskee kopioiden *järjestystä*. Saman lohkon phit
lukevat kaikki argumenttinsa samalla hetkellä, kun lohkoon tullaan.
Testin silmukka vaihtaa kahden rekisterin arvot keskenään:

```{.tuloste tiedosto="esimerkit/passit/vaihto.ir"}
```

Kolmen vaihdon jälkeen oikea tuloste on 2 ja 1. Jos kopiot
kirjoitetaan phien järjestyksessä, ensimmäinen hävittää arvon, jonka
toinen tarvitsee:

```{.tuloste tiedosto="esimerkit/passit/vaihto-naiivi.odotettu" rivit="14-20"}
```

Ohjelma tulostaa 2 ja 2. Tämä on **vaihdon ongelma** (*swap problem*).
Phien kopiot ovat **rinnakkaisia kopioita** (*parallel copy*):
kaikki lähteet luetaan ennen kuin yhteenkään kohteeseen kirjoitetaan.
Peräkkäisiksi ne saadaan järjestämällä. Kopion voi tehdä, kun mikään
jäljellä oleva kopio ei enää lue sen kohdetta. Jos sellaista ei ole,
jäljellä on kehä, ja se katkaistaan ottamalla yksi arvo talteen
apurekisteriin:

```{.cpp tiedosto="esimerkit/kide/ssapois.cpp" osa="rinnakkaiset"}
```

```{.tuloste tiedosto="esimerkit/passit/vaihto.odotettu" rivit="14-21"}
```

Laskurin kopio tehdään ensin, koska mikään ei lue sen kohdetta, ja
vaihto kulkee apurekisterin `%k11` kautta. Lähdekoodissa tällainen
phipari syntyy tavallisesta vaihdosta `var t = a; a = b; b = t;`
silmukassa, kun kopioiden eteneminen on poistanut apumuuttujan.

Virheelliset variantit ovat mukana testisarjassa passeina
`pura` ilman kaarten jakoa ja `pura-naiivi`, ja niiden väärät
tulosteet 5 sekä 2 ja 2 ovat kultaisia tiedostoja. Näin testisarja
osoittaa, että kumpikin testiohjelma todella erottaa oikean
toteutuksen väärästä.

## Kopioiden sulauttaminen

Purkaminen tuottaa kopion jokaista phin argumenttia kohden. Luvun 13
esimerkkifunktiossa `laske` niitä on kolmesta phistä kuusi
(`--vaihe=ssapassit -O2`):

```{.tuloste tiedosto="esimerkit/naytteet/ssapassit-laske.txt" alkaen="; phit purettu" asti="ret summa.1"}
```

Useimmat kopioista ovat tarpeettomia. Esimerkiksi `i.1` ja `i.2` ovat
saman laskurin peräkkäiset arvot: kun `i.2` on laskettu, `i.1`:tä ei
enää tarvita. Ne voivat jakaa rekisterin, ja kopio `i.1 = i.2` katoaa.
**Sulauttaminen** (*coalescing*) yhdistää kopion kohteen ja lähteen
yhdeksi rekisteriksi aina, kun se on turvallista.

Turvallisuuden ratkaisee **häirintä** (*interference*): kaksi
rekisteriä häiritsee toisiaan, jos toiseen kirjoitetaan, kun toisen
arvoa vielä tarvitaan. Häirinnät saadaan luvun 10 elävyydestä
kulkemalla jokainen lohko lopusta alkuun. Kopio on poikkeus: `x = y`
ei tee `x`:stä ja `y`:stä häiritseviä, koska niillä on kopion jälkeen
sama arvo.

```{.cpp tiedosto="esimerkit/kide/ssapois.cpp" osa="sulauta"}
```

Kun kaksi rekisteriä sulautetaan, yhdistetty rekisteri perii
molempien häirinnät, joten myöhemmät sulautukset näkevät ajantasaisen
tilanteen. Testissä toinen kopio saa sulautua ja toinen ei:

```{.tuloste tiedosto="esimerkit/passit/sulautus.ir"}
```

```{.tuloste tiedosto="esimerkit/passit/sulautus.odotettu"}
```

Menetelmä on Chaitinin graafinvärittäjästä (luku 16), jossa sama
häirintätieto on interferenssigraafi. Kide sulauttaa aina, kun
häirintää ei ole. Tuotantokääntäjät ovat varovaisempia, koska
yhdistetty rekisteri elää pidempään ja voi olla vaikeampi sijoittaa.

## Tulos

Kuvassa on esimerkkifunktio putken alussa ja lopussa (`--vaihe=ir`
tasoilla `-O1` ja `-O2`).

```{.dot tiedosto="kaaviot/cfg-laske.dot" otsikko="Funktion laske ohjausvuograafi paikallisten passien jälkeen ja SSA-optimointien jälkeen (kääntäjän tulosteista)" leveys="100%"}
```

Versiot `summa.1`–`summa.4` ovat sulautuneet takaisin yhdeksi
rekisteriksi, samoin `i.1` ja `i.2`. Kuudesta kopiosta jäi sulautuksen
jälkeen yksi: vakio `$0` sulautui `i.1`:een, mutta `summa.1` ei voinut
sulautua samaan rekisteriin, koska `i.1` ja `summa.1` häiritsevät
toisiaan. Luvun 11 passit muuttivat jääneen kopion `summa.1 = i.1`
takaisin vakion sijoitukseksi ja poistivat tyhjät lohkot.

Silmukan kierros on lyhentynyt kuudestatoista välikielen käskystä
kymmeneen, ja yksi haara on poissa. Kaavio näyttää myös, mitä jäi
tekemättä: tulo `n * k`, vakio 100 ja niiden vertailu lasketaan joka
kierroksella, vaikka ne eivät muutu silmukassa. Niiden siirtäminen
silmukan eteen on luvun 11 taulukon *silmukasta riippumattoman koodin
siirto*.

## Mittaus

Optimoinnin hyöty mitataan suoritetuista käskyistä. Valinnalla
`--laske` kääntäjä lisää jokaisen peruslohkon alkuun laskurin, joka
kasvaa lohkon käskyjen määrällä, ja ajonaikainen kirjasto tulostaa
summan ohjelman lopussa:

```{.cpp tiedosto="esimerkit/kide/koodigen.cpp" osa="laskuri"}
```

Luku on täsmälleen sama joka ajolla, toisin kuin suoritusaika, joten
se kelpaa kultaiseksi tiedostoksi. Testisarja mittaa jokaisen
testiohjelman molemmilla tasoilla (funktio `mittaa` tiedostossa
`testaa.sh`); sarake *koodissa* on käskyjen määrä assemblyssä:

```{.tuloste tiedosto="esimerkit/naytteet/mittaus.txt"}
```

![Suoritettujen käskyjen muutos tasolta `-O1` tasolle `-O2`
testiohjelmittain (taulukon luvuista).](kuvat/mittaus.png){width=78%}

Tuloksessa on kolme havaintoa. Ensinnäkin hyöty on silmukoissa:
`laske` nopeutuu kolmanneksen, koska se kirjoitettiin näitä passeja
varten, ja `collatz` 17,5 %, koska sen silmukan kierroksesta poistui
kolme vakion latausta: vakio 1 ladataan kerran ennen silmukkaa ja
vakio 2 kerran kierroksella.

Toiseksi koodin *koko* kasvaa useimmissa ohjelmissa, vaikka
suoritettuja käskyjä on vähemmän. Jaettu vakio tai lauseke elää
pidempään kuin lohkon sisäinen väliaikainen, joten funktio tarvitsee
useamman rekisterin, ja Kide tallentaa jokaisen käyttämänsä
`s`-rekisterin funktion alussa ja palauttaa sen lopussa (luku 15).

Kolmanneksi `kertoma` hidastuu 3 %. Funktiossa vakio 1 on nyt yhteinen
vertailulle `n <= 1` ja vähennykselle `n - 1`:

```{.gnuassembler tiedosto="esimerkit/naytteet/asm-kertoma-O2.txt" rivit="9-18"}
```

Loppu funktiosta on sama kuin luvussa 1, paitsi että kaksi
`li`-käskyä on poissa. Vertailun tulos tarvitsee kuitenkin oman
rekisterinsä `s3`, koska `s2` on varattu vakiolle. Jokainen
rekursiokutsu maksaa siitä yhden tallennuksen ja yhden latauksen ja
säästää yhden `li`:n.
Välikielen tasolla muunnos oli puhdas parannus, ja hinta syntyi vasta
takaosassa. Tuotantokääntäjä välttää tämän kahdella tavalla: pieni
vakio kirjoitetaan suoraan käskyyn (`addi`, luku 15), ja rekisterien
varaaja voi laskea vakion uudelleen käyttökohdassa sen sijaan, että
pitäisi sitä rekisterissä (*rematerialization*).

## Työnjako paikallisten passien kanssa

SSA-passit eivät korvaa luvun 11 passeja vaan toimivat niiden välissä:

| Vaihe | Passit | Tehtävä |
|-------|--------|---------|
| ennen SSA-muotoa | luvun 11 passit | pienentää funktion ja siistii ohjausvuon; phejä syntyy vähemmän |
| SSA-muodossa | luvun 13 passit | vakiot, yhteiset lausekkeet ja kuollut koodi koko funktion yli |
| SSA-muodon jälkeen | luvun 11 passit | tyhjät lohkot, hyppyketjut ja loput kopiot |

Arvonumerointi ja kuolleen koodin poisto ovat siis kääntäjässä
kahdesti. SSA-versiot tekevät kaiken, minkä paikalliset, joten
kokonaan SSA-muotoon rakennettu kääntäjä ei tarvitsisi paikallisia;
Kidessä ne ovat tason `-O1` sisältö ja `-O2`:n vertailukohta.
Ohjausvuon siistiminen on sen sijaan vain paikallisena, koska
tavallisessa välikielessä lohkon tai kaaren poistaminen ei vaadi
phien korjaamista.

Taso `-O1` kytkee SSA-passit pois, ja siitä on kaksi hyötyä. Mittaus
vertaa tasoja keskenään, ja testisarja ajaa jokaisen ohjelman
kaikilla tasoilla ja vaatii saman tulosteen (luku 17). Jos `-O2`
tuottaa eri tuloksen kuin `-O1`, vika on SSA-putkessa, ja
`--vaihe=ssapassit` näyttää, minkä vaiheen jälkeen koodi muuttui
vääräksi.

## Käytännössä

- **Jaa kriittiset kaaret ennen phien purkua.** Kopio, joka on
  väärällä polulla, ylikirjoittaa arvon, jota toinen polku vielä
  lukee.
- **Käsittele phien kopiot rinnakkaisina.** Järjestä ne ja katkaise
  kehät apurekisterillä; phien kirjoitusjärjestys ei ole
  suoritusjärjestys.
- **Sulauta kopiot purkamisen jälkeen.** Ilman sulautusta jokainen phi
  maksaa kopion jokaisella kaarella, ja SSA-muodossa tehty
  optimointi voi hävitä takaisin.
- **Mittaa suoritetut käskyt, älä koodin kokoa.** Optimointi voi
  kasvattaa koodia ja silti vähentää työtä, ja päinvastoin.
- **Arvioi optimointi takaosan läpi.** Välikielen käskymäärä ei kerro
  rekisterien hintaa; muunnos, joka pidentää elinvälejä, voi hidastaa
  ohjelmaa.
- **Pidä optimoinnit valinnan takana.** Taso, jolla passi ei ole
  käytössä, on sekä vertailukohta mittaukselle että oraakkeli
  testeille.

## Itsearviointi

- Osaat purkaa phi-funktiot kopioiksi ja selittää, miksi se on
  optimointien jälkeen vaikeampaa kuin heti SSA-muunnoksen jälkeen.
- Osaat tunnistaa kriittisen kaaren ja näyttää esimerkillä, miten
  kopio katoaa, jos kaarta ei jaeta.
- Osaat järjestää rinnakkaiset kopiot peräkkäisiksi ja katkaista
  kehän apurekisterillä.
- Osaat määritellä häirinnän ja päättää, saako kopion kohteen ja
  lähteen sulauttaa.
- Osaat selittää, miksi välikielessä hyödyllinen muunnos voi lisätä
  suoritettuja käskyjä, ja mitata sen.
