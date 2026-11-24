# Testipenkin rakenne

Johdannon ohjattu testi sekoitti kolme asiaa samaan koodiin: mitä
tehdään (kirjoita neljä arvoa), miten se tehdään liitännässä (aseta
`push` ja `din` laskevalla reunalla) ja mitä odotetaan (`maara == 4`).
Kun testejä on kymmeniä, sama liitäntäkoodi ja samat odotukset
kopioituvat jokaiseen. Kerroksellinen testipenkki erottaa ne omiksi
osikseen, joista kukin tekee yhden asian.

## Osat

```{.dot otsikko="Kerroksellisen testipenkin osat. Vain ajuri ja monitori tuntevat signaalit."}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.45;
  testi [shape=plaintext, style=""];
  dut [label="DUT", shape=box3d, style=""];
  testi -> generaattori;
  generaattori -> ajuri [label="transaktiot"];
  ajuri -> dut [label="signaalit"];
  dut -> monitori [label="signaalit"];
  monitori -> tulostaulu [label="havainnot"];
  monitori -> referenssimalli [label="havainnot"];
  referenssimalli -> tulostaulu [label="ennuste"];
  {rank=same; ajuri; monitori}
}
```

| Osa | Tehtävä | Tietää liitännästä |
|-----|---------|--------------------|
| transaktio | yksi toimenpide abstraktina tietueena | ei mitään |
| generaattori | tuottaa transaktioita (ohjatusti tai satunnaisesti) | ei mitään |
| ajuri (driver) | muuntaa transaktion signaaleiksi oikeaan aikaan | kaiken |
| monitori | muuntaa signaalit takaisin havainnoiksi | kaiken |
| referenssimalli | laskee, mitä DUT:n pitäisi tehdä | ei mitään |
| tulostaulu (scoreboard) | vertaa havaintoja mallin ennusteisiin | ei mitään |
| testi | valitsee generaattorin asetukset ja ajaa | ei mitään |

Taulukon oikea sarake on rakenteen ydin. Vain ajuri ja monitori
tuntevat signaalit ja ajoituksen. Jos liitäntä muuttuu, esimerkiksi
`push` muuttuu kättelyksi `valid`/`ready`, vain ne muutetaan. Malli,
tulostaulu ja testit puhuvat transaktioista.

Monitori on erillään ajurista, vaikka se näkee samat signaalit, koska
se havaitsee, mitä liitännässä *todella* tapahtui, ei sitä, mitä
ajuri yritti tehdä. Samaa monitoria voi käyttää, kun lohko on osa
suurempaa järjestelmää ja liitäntää ajaa toinen lohko eikä testipenkin
ajuri. Silloin ajuri poistetaan ja monitori ja tulostaulu jäävät.

## Transaktio

FIFOn transaktio on yhden kellojakson toimenpide: kirjoitetaanko,
luetaanko ja mikä data kirjoitetaan.

```{.systemverilog tiedosto="esimerkit/03-penkki/testipenkki.sv" osa="transaktio"}
```

Abstraktiotaso valitaan niin, että testit ovat helppoja kirjoittaa.
Väylällä transaktio olisi yleensä kokonainen siirto (osoite, data,
vastaus), joka kestää useita jaksoja; ajuri hoitaa kättelyt.

## Generaattori

Tässä generaattori arpoo toimenpiteitä painotetusti. Painotus on
valittu niin, että jono täyttyy ja tyhjenee usein. Satunnaistusta
käsitellään tarkemmin luvussa 4.

```{.systemverilog tiedosto="esimerkit/03-penkki/testipenkki.sv" osa="generaattori"}
```

## Ajuri

Ajuri ottaa jonosta seuraavan toimenpiteen ja asettaa signaalit kellon
laskevalla reunalla. Laskeva reuna on testipenkeissä yleinen tapa
välttää kilpatilanne: jos testipenkki muuttaisi tuloja samalla
nousevalla reunalla, jolla DUT lukee ne, tulos riippuisi siitä,
kumpi prosessi simulaattori ajaa ensin.

```{.systemverilog tiedosto="esimerkit/03-penkki/testipenkki.sv" osa="ajuri"}
```

Ajuri on kirjoitettu `initial forever` -silmukaksi eikä
`always`-lohkoksi. Verilator varoittaa (BLKSEQ), jos `always`-lohkossa
on estäviä sijoituksia, koska synteesikelpoisessa koodissa se on
virhe. Testipenkkikoodissa estävä sijoitus on oikein, ja `initial
forever` kertoo lukijalle ja työkalulle, että kyse on testipenkin
prosessista.

## Monitori, malli ja tulostaulu

Referenssimalli on tässä yksinkertaisin mahdollinen: SystemVerilogin
jono (`logic [7:0] malli[$]`), joka tekee saman kuin FIFO ilman
osoittimia, muistia ja ajoitusta. Malli päättää itse, hyväksytäänkö
kirjoitus, eikä luota DUT:n `taysi`-lippuun. Muuten `BUGI_TAYSI`
huijaisi myös mallia.

Monitori ja tulostaulu ovat tässä samassa prosessissa. Nousevalla
reunalla luetut arvot ovat ne, jotka DUT näkee reunalla, koska
rekisterien uudet arvot päivittyvät vasta reunan jälkeen. Tila
verrataan ensin malliin ja malli päivitetään vasta sen jälkeen:

```{.systemverilog tiedosto="esimerkit/03-penkki/testipenkki.sv" osa="tulostaulu"}
```

Vertailu `!==` on nelitilainen: se pitää arvoa `x` erisuurena kuin
mikään määrätty arvo. Tavallinen `!=` palauttaisi `x`:n, jolloin ehto
olisi epätosi ja virhe jäisi huomaamatta.

Tulostaulu tulostaa vain kolme ensimmäistä virhettä. Ensimmäinen
virhe on yleensä lähimpänä syytä; sen jälkeen DUT ja malli ovat eri
tiloissa, ja loput virheet ovat seurauksia.

## Testi

Testi lukee siemenen argumentista, täyttää jonon 2000 toimenpiteellä,
vapauttaa nollauksen ja odottaa, että ajuri on käyttänyt jonon:

```{.systemverilog tiedosto="esimerkit/03-penkki/testipenkki.sv" osa="testi"}
```

Ehjällä FIFOlla tulostaulu ei löydä virheitä:

```{.tuloste tiedosto="esimerkit/odotetut/penkki.odotettu"}
```

Sama testipenkki löytää kaikki kolme FIFOn vikaa. Ohjatulta testiltä
huomaamatta jäänyt `BUGI_SAMANAIKAINEN` paljastuu jo simulaatioajan
hetkellä 75:

```{.tuloste tiedosto="esimerkit/odotetut/penkki-samanaikainen.odotettu"}
```

Luku tyhjästä jonosta tuottaa alivuodon, jonka jälkeen määrä on 7:

```{.tuloste tiedosto="esimerkit/odotetut/penkki-tyhja.odotettu"}
```

Liian aikainen `taysi` näkyy suoraan lippujen vertailussa:

```{.tuloste tiedosto="esimerkit/odotetut/penkki-taysi.odotettu"}
```

## Referenssimallin taso

Referenssimalli voi olla eri tarkkuustasoilla:

| Taso | Ennustaa | Esimerkki |
|------|----------|-----------|
| transaktiotaso | tuloksen ja järjestyksen, ei ajoitusta | FIFOn jono, salauslohkon salateksti |
| jaksotarkka | tuloksen jokaisella jaksolla | tämän luvun malli, arbiterin myöntö (luku 9) |
| bittitarkka algoritmimalli | numeerisen tuloksen bitilleen | DSP-suodattimen kiinteän pilkun malli |

Transaktiotason malli on helpoin kirjoittaa ja kestää toteutuksen
muutokset, kuten liukuhihnan lisäämisen. Jaksotarkka malli löytää
myös ajoitusvirheet, mutta se on käytännössä toinen toteutus ja
muuttuu jokaisen RTL-muutoksen mukana. FIFOn malli on jaksotarkka
lippujen ja määrän osalta, mutta datan osalta transaktiotasoinen.

Kun malli on kirjoitettu toisella kielellä (C, C++ tai Python), se
liitetään testipenkkiin SystemVerilogin DPI-rajapinnalla tai
cocotb:llä (luku 7). Algoritmilohkoissa sama malli on usein
järjestelmäsuunnittelijan alkuperäinen malli, jolloin RTL:ää verrataan
suoraan siihen.

## Käytännössä

- **Vain ajuri ja monitori tuntevat signaalit.** Muut osat puhuvat
  transaktioista, joten liitännän muutos koskee kahta osaa.
- **Malli päättää itse.** Referenssimalli ei saa lukea DUT:n
  sisäistä tilaa tai lippuja ennustaakseen sen käytöstä; silloin vika
  siirtyy malliin.
- **Ärsyke laskevalla reunalla tai pienellä viiveellä, näytteistys
  nousevalla.** Kilpatilanne testipenkin ja DUT:n välillä on yleisin
  syy testiin, joka toimii yhdellä simulaattorilla ja ei toisella.
  SystemVerilogin `clocking`-lohko tekee saman ajoituksen
  standardilla tavalla, ja myös Verilator 5 tukee sitä.
- **Ensimmäinen virhe on tärkein.** Tulosta muutama ensimmäinen ja
  laske loput; tuhat virheriviä piilottaa syyn.
- **Testi päättyy virhekoodiin.** `$error` tai `$fatal` saa
  simulaattorin palauttamaan nollasta poikkeavan arvon, jonka
  regressio tunnistaa. Pelkkä tulostettu "FAIL" vaatii jäsennyksen.
- **Nelitilainen vertailu tarkistuksissa.** `!==` ja `===` havaitsevat
  `x`:n; `!=` ja `==` piilottavat sen.

## Itsearviointi

- Osaat jakaa testipenkin osiin (transaktio, generaattori, ajuri,
  monitori, referenssimalli, tulostaulu, testi) ja kertoa, mitä kukin
  tietää liitännästä.
- Osaat ajoittaa ärsykkeen ja näytteistyksen niin, ettei testipenkin
  ja DUT:n välille synny kilpatilannetta.
- Osaat kirjoittaa referenssimallin, joka ei riipu DUT:n sisäisestä
  tilasta.
- Osaat valita referenssimallin tarkkuustason ja kertoa sen hinnan.
- Osaat selittää, miksi `!==` on oikea vertailu tulostaulussa.
