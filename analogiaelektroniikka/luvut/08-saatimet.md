# Jännitteensäätimet

Kaikki edellisten lukujen piirit olettivat, että käyttöjännite on
tasainen ja häiriötön. Tämä luku rakentaa sen. Taidossa *Elektroniikan
perusteet ja SPICE* lineaarisäädin oli musta laatikko, jolla on
pudotusjännite ja häviöteho. Nyt laatikko avataan: sisällä on luvun 5
takaisinkytketty vahvistin, jonka kuorma on aina kondensaattori, ja
luvun 7 kohina ja häiriöt näkyvät sen lähdössä. Luvun lopussa
esitellään hakkuri, joka tekee saman tehtävän lämmittämättä, ja
perusteet valita näiden väliltä.

## Säädin on takaisinkytketty vahvistin

Lineaarisäätimessä on neljä osaa. *Referenssi* antaa tarkan
jännitteen, tässä 1,25 V. *Jännitteenjako* R1 ja R2 tuo lähdöstä osan
$\beta = R_2/(R_1 + R_2)$ takaisin. *Virhevahvistin* vertaa tätä
referenssiin ja ohjaa *päästötransistoria*, joka on sarjassa syötön ja
lähdön välissä. Kun silmukkavahvistus on suuri, takaisinkytketty
jännite on sama kuin referenssi, ja lähtö on

$$
U_{ulos} = \frac{U_{ref}}{\beta} = U_{ref}\left(1 + \frac{R_1}{R_2}\right).
$$

Säädin on siis ei-invertoiva vahvistin, jonka tulona on referenssi ja
jonka lähtöaste on tehotransistori. Referenssi tehdään integroidussa
piirissä yleensä *bandgap*-kytkennällä. Transistorin kanta-emitterijännite
laskee lämpötilan noustessa noin 2 mV/K. Kahden eri virrantiheydellä
toimivan transistorin kanta-emitterijännitteiden erotus taas kasvaa
suoraan lämpötilan mukana. Kun nämä summataan sopivassa suhteessa,
lämpötilariippuvuudet kumoavat toisensa, ja tulos on noin 1,2 V, mistä
1,25 V:n referenssit ovat peräisin. Tässä luvussa referenssi on
ihanteellinen jännitelähde.

Päästötransistorin voi kytkeä kahdella tavalla, ja valinta määrää
säätimen luonteen:

![Sama 3,3 V:n säädin kahdella päästötransistorilla. Vasemmalla
P-kanavainen transistori, jonka lähde on syötössä (LDO). Mukana ovat
myös lähtökondensaattori sarjaresistansseineen ja kuorma, joita
käytetään luvun myöhemmissä netlisteissä. Oikealla N-kanavainen
transistori seuraajana.](kuvat/saadin-kaavio.png){width=100%}

Seuraajassa transistorin lähde on säätimen lähdössä, joten hilan on
oltava lähtöä korkeammalla. P-kanavaisessa kytkennässä hilaa vedetään
alas syötöstä, ja transistori voi johtaa täysin, vaikka syöttö olisi
vain hieman lähtöä korkeampi. Koska P-kanavainen transistori kääntää
vaiheen, takaisinkytkentä tuodaan siinä virhevahvistimen plus-tuloon.

```{.spice tiedosto="esimerkit/08-saadin.cir"}
```

Virhevahvistin on oma aliohjelmansa kirjastossa `saatimet.lib`. Luvun 3
makromalli ei sovi tähän: se rajoittaa vasta lähtönsä, jolloin sen
sisäinen solmu ajautuu kyllästyksessä kauas ja palaa hitaasti. Säätimen
vahvistin on kyllästyksessä aina, kun syöttö ei riitä, joten tässä
rajoitus on tehty itse lähtösolmuun:

```{.spice tiedosto="esimerkit/saatimet.lib"}
```

Vahvistin on *transkonduktanssivahvistin*: se syöttää tulojen eroon
verrannollisen virran lähtöönsä, jonka resistanssi $R_A$ antaa
tasavahvistuksen $A = G_M R_A = 1000$. Lähtö on kytketty suoraan
päästötransistorin hilaan. Toimintapisteen voi laskea käsin: vahvistin
tarvitsee tulojensa välille eron $U_g/A$ tuottaakseen hilajännitteen
$U_g$, ja tämä ero näkyy lähdössä kerrottuna $1/\beta$:lla.

```{.python tiedosto="esimerkit/08-saadin.py" osa="osat"}
```

```{.python tiedosto="esimerkit/08-saadin.py" osa="toimintapiste"}
```

```{.tuloste tiedosto="esimerkit/08-saadin.odotettu" rivit="1-13"}
```

Tuloksissa on kolme säätimen tunnuslukua.

- **Tarkkuus.** LDO:n lähtö on 7,8 mV liian korkea ja seuraajan 13 mV
  liian matala. Syy on äärellinen vahvistus: hilajännitteen 2,96 V
  tuottamiseen tarvitaan tuloihin 3 mV:n ero. Oikeassa säätimessä tätä
  suurempi virhe tulee referenssin toleranssista, tyypillisesti 1 ... 2 %.
- **Kuormaregulaatio** (*load regulation*) kertoo, paljonko lähtö
  muuttuu, kun kuormavirta kasvaa 1 mA:sta 100 mA:iin. Transistori
  tarvitsee suuremmalle virralle suuremman hilan ja lähteen välisen
  jännitteen, ja lähtö laskee sen verran, että vahvistin tuottaa
  muutoksen: LDO:ssa 1,05 mV.
- **Linjaregulaatio** (*line regulation*) kertoo lähdön muutoksen
  syötön muuttuessa. LDO:ssa transistorin lähde on syötössä, joten hilan
  on seurattava syöttöä voltti voltista, ja lähtö muuttuu $1/(A\beta)$
  eli 2,6 mV/V. Seuraajassa syöttö on transistorin nielussa, ja sen
  vaikutus on yli tuhat kertaa pienempi.

## Pudotusjännite ja häviö

Kun syöttö laskee, vahvistin ajaa hilan ääriasentoonsa pitääkseen
lähdön ylhäällä. *Pudotusjännite* on pienin syötön ja lähdön ero, jolla
säädin vielä säätää.

```{.python tiedosto="esimerkit/08-saadin.py" osa="pudotus"}
```

![Vasemmalla lähtö syöttöjännitteen funktiona 100 mA:n kuormalla.
Katkoviiva on 1 % nimellisarvon alapuolella. Oikealla LDO:n
kuormaregulaatio: lähdön muutos kuormavirran kasvaessa.](kuvat/saadin-pudotus.png){width=92%}

Seuraaja lakkaa säätämästä, kun syöttö on alle 5,0 V: hila ei nouse
syötön yli, ja lähtö jää siitä kynnysjännitteen ja ylijännitteen verran
eli 1,74 V alemmas. Tästä syystä perinteinen säädin tarvitsee noin
kahden voltin varan. LDO:ssa hila on pudotustilanteessa maassa ja
transistori johtaa täysin, joten jäljelle jää vain sen
johtamisresistanssi: 59 mV 100 mA:n virralla. Pudotusjännite on siksi
verrannollinen kuormavirtaan, ja datalehti ilmoittaa sen tietyllä
virralla.

Pieni pudotusjännite on tärkeä hyötysuhteen takia. Kuormavirta kulkee
säätimen läpi, joten syöttöjännitteellä $U_{in}$ häviö on
$(U_{in} - U_{ulos})\,I$ ja hyötysuhde enintään $U_{ulos}/U_{in}$:

```{.tuloste tiedosto="esimerkit/08-saadin.odotettu" rivit="14-16"}
```

LDO voi toimia 3,6 V:n syötöstä 92 %:n hyötysuhteella, mihin seuraaja ei
pysty millään syötöllä. Häviöteho muuttuu lämmöksi, ja liitoksen
lämpötila lasketaan lämpöresistanssista kuten taidossa *Elektroniikan
perusteet ja SPICE*: 170 mW lämmittää pientä SOT-23-koteloa
(250 K/W) noin 43 astetta. Sama säädin 12 V:n syötöstä hukkaisi
0,87 W, mikä on kotelolle liikaa. Silloin tarvitaan hakkuri.

Säädin kuluttaa virtaa myös ilman kuormaa. Tässä jakovastusten kautta
kulkee 125 µA, ja oikeassa piirissä lisäksi vahvistimen ja referenssin
virta. Tämä *lepovirta* ratkaisee paristokäyttöisen laitteen
käyttöajan, kun laite nukkuu suurimman osan ajasta.

## Stabiilisuus ja lähtökondensaattori

Luku 5 päättyi toteamukseen, että säätimen datalehti määrää
lähtökondensaattorin arvon ja sarjaresistanssin. Nyt nähdään, miksi.
LDO:n silmukassa on kaksi matalaa napaa. Ensimmäinen syntyy
virhevahvistimen lähdössä, jossa suuri resistanssi $R_A$ kohtaa
päästötransistorin hilakapasitanssin. Toinen syntyy lähdössä:
P-kanavaisen transistorin nielu on suuri-impedanssinen, ja sitä
kuormittaa lähtökondensaattori. Kaksi napaa kääntää vaihetta 180
astetta, joten vaihevaraa ei ole. Silmukan pelastaa kondensaattorin
sarjaresistanssi (*ESR*, equivalent series resistance): se tuo nollan
taajuudelle $1/(2\pi\,ESR\,C)$, ja nolla palauttaa vaihetta.

Seuraajassa ongelmaa ei ole samassa muodossa. Sen lähtö on
pieni-impedanssinen, joten lähtönapa on korkealla, ja säädin
vakautetaan sisäisellä kondensaattorilla. Pienen pudotusjännitteen
hinta on siis vaikeampi stabiilisuus.

Silmukkavahvistus mitataan kuten luvussa 5, mutta katkaisu on
yksinkertaisempi. Virhevahvistimen tulo ei ota virtaa, joten
testilähteen voi kytkeä sarjaan takaisinkytkentään, ja
silmukkavahvistus on sen eri puolten jännitteiden suhde:

```{.spice tiedosto="esimerkit/08-vakaus.cir"}
```

Kapasitanssi `Cgs` on transistorin hilan ja lähteen välissä ja `Cea`
vahvistimen lähdöstä maahan. Silmukan kannalta ne ovat rinnakkain.
Malli on kolmen tekijän tulo: virhevahvistin, transistorin
transkonduktanssi ja lähtösolmun impedanssi.

```{.python tiedosto="esimerkit/08-vakaus.py" osa="malli"}
```

```{.tuloste tiedosto="esimerkit/08-vakaus.odotettu" rivit="1-14"}
```

![Vasemmalla silmukkavahvistus ja vaihe kolmella sarjaresistanssilla.
Oikealla mallin vaihevara sarjaresistanssin funktiona kolmella
kuormalla; vihreällä alueella vara on yli 45°.](kuvat/saadin-vaihevara.png){width=96%}

Keraamisen kondensaattorin 10 mΩ:n sarjaresistanssilla vaihevara on
nolla tai negatiivinen: säädin värähtelee. 0,5 ... 1 Ω:n resistanssilla
vara on hyvä, ja liian suurella se heikkenee taas, koska nolla siirtää
ylitystaajuuden vahvistimen toisen navan yläpuolelle. Sopiva alue
riippuu kuormasta: pienellä kuormalla lähtönapa on matalammalla.
Datalehden käyrä sallitusta sarjaresistanssista kuormavirran funktiona
on tämä sama kuva valmistajan mittaamana.

Aikatasossa sama näkyy kuorman muuttuessa äkisti:

```{.tuloste tiedosto="esimerkit/08-vakaus.odotettu" rivit="15-19"}
```

![Lähtö, kun kuorma kasvaa 10 mA:sta 100 mA:iin. Pienellä
sarjaresistanssilla värähtely kasvaa, kunnes transistorin
epälineaarisuus rajoittaa sen.](kuvat/saadin-askel.png){width=92%}

Sarjaresistanssilla on hintansa. Ennen kuin silmukka ehtii reagoida,
virran muutos kulkee kondensaattorin kautta ja tuottaa
sarjaresistanssissa jännitteen $ESR \cdot \Delta I$: 0,5 Ω:lla 45 mV.
Vakaus ja nopea vaste vetävät eri suuntiin. Uudemmat säätimet on
kompensoitu sisäisesti niin, että ne ovat vakaita keraamisella
kondensaattorilla, ja datalehti sanoo sen erikseen. Vanhemmat vaativat
tantaalikondensaattorin tai sarjavastuksen. Keraamista kondensaattoria
valitessa on lisäksi muistettava, että sen kapasitanssi pienenee
tasajännitteen vaikutuksesta, pienissä koteloissa jopa alle puoleen
nimellisarvosta.

## Syötön häiriöt ja kohina

Säätimen toinen tehtävä on eristää kuorma syötön häiriöistä. Sitä
mittaa *PSRR* (power supply rejection ratio): syötön vaihtojännitteen
suhde lähdössä näkyvään osaan desibeleinä. Lisäksi säädin tuottaa omaa
kohinaa, josta suurin osa on peräisin referenssistä. Netlistissä
referenssin kohinaa mallintaa vastus, jonka terminen kohina
(luku 7) on tavallisen bandgap-referenssin suuruusluokkaa:

```{.spice tiedosto="esimerkit/08-hairiot.cir"}
```

```{.python tiedosto="esimerkit/08-hairiot.py" osa="psrr"}
```

```{.tuloste tiedosto="esimerkit/08-hairiot.odotettu" rivit="1-4"}
```

Matalilla taajuuksilla vaimennus on $A\beta$ eli 51,6 dB, sama luku
kuin linjaregulaatio. Virhevahvistimen navan yläpuolella
silmukkavahvistus laskee, ja vaimennus sen mukana. 200 kHz:n taajuudella
jäljellä on 21,5 dB: syötön häiriöstä pääsee läpi kahdestoistaosa.
Lineaarisäädin ei siis yksin poista hakkurin kytkentätaajuista rippeliä.
Sen eteen tarvitaan LC-suodin tai ferriitti, tai valitaan säädin, jonka
vaimennus on ilmoitettu juuri sillä taajuudella.

![Vasemmalla syötön häiriöiden vaimennus taajuuden funktiona.
Oikealla lähdön kohinatiheys ilman referenssin suodatusta ja 100 nF:n
suodatuskondensaattorilla.](kuvat/saadin-hairiot.png){width=92%}

Kohinalle silmukka tekee päinvastoin kuin häiriöille. Referenssin,
jakovastusten ja vahvistimen tulon kohina on silmukan sisällä, ja lähtö
seuraa sitä uskollisesti vahvistettuna kertoimella $1/\beta$:

```{.python tiedosto="esimerkit/08-hairiot.py" osa="kohina"}
```

```{.tuloste tiedosto="esimerkit/08-hairiot.odotettu" rivit="5-10"}
```

Ilman suodatusta lähdön kohina on 121 µV kaistalla 10 Hz ... 100 kHz,
mikä on tavallisen säätimen datalehtiarvojen luokkaa. Kun referenssi
suodatetaan kondensaattorilla ennen vahvistinta, kohina putoaa
kymmenesosaan. Vähäkohinaisissa säätimissä tätä varten on oma nasta
(NR tai BYP). Suodatuksen jälkeen jäljelle jää jakovastusten ja
vahvistimen kohina. 16-bittiselle muuntimelle, jonka pienin askel 2,5 V:n
referenssillä on 38 µV, ero on ratkaiseva; logiikkapiirille sillä ei
ole merkitystä.

## Hakkurin periaate: buck-muunnin

Lineaarisäädin pudottaa ylimääräisen jännitteen lämmöksi. *Hakkuri*
(*switching regulator*) ei pudota sitä lainkaan: se kytkee syötön
kuormaan lyhyiksi hetkiksi ja tasoittaa pulssit kelalla ja
kondensaattorilla. Alentava hakkuri eli *buck-muunnin* on rakenteista
yksinkertaisin.

![Buck-muuntimen tehoaste. Kun kytkin johtaa, kelan virta kasvaa
syötöstä; kun se avautuu, virta jatkaa kulkuaan diodin kautta.](kuvat/buck-kaavio.png){width=58%}

Kela vastustaa virran muutosta. Kytkimen johtaessa sen yli on jännite
$U_{in} - U_{ulos}$ ja virta kasvaa; kytkimen avauduttua jännite on
$-U_{ulos}$ ja virta pienenee. Tasapainossa kasvu ja lasku ovat yhtä
suuret, mistä seuraa, että lähtö on *pulssisuhteen* $D$ osuus syötöstä:
$U_{ulos} = D\,U_{in}$. Netlistissä pulssisuhde on kiinteä 0,275, ja
parametreilla valitaan kuorma ja osien häviöt:

```{.spice tiedosto="esimerkit/08-buck.cir"}
```

```{.python tiedosto="esimerkit/08-buck.py" osa="jatkuva"}
```

```{.tuloste tiedosto="esimerkit/08-buck.odotettu" rivit="1-5"}
```

Kelan virta on kolmioaalto kuormavirran ympärillä, ja kondensaattori
tasoittaa sen niin, että lähdössä on 1,6 mV:n rippeli. Oikeassa
piirissä rippeliä kasvattaa kondensaattorin sarjaresistanssi, jonka
kautta kelavirran vaihteleva osa kulkee.

![Kytkentäsolmun jännite, kelan virta ja lähdön rippeli neljän jakson
ajalta. Vasemmalla kelan virta ei käy nollassa. Oikealla kevyt kuorma:
virta katkeaa, ja kytkentäsolmu asettuu loppujaksoksi
lähtöjännitteeseen.](kuvat/buck-aallot.png){width=92%}

Sääntö $U_{ulos} = D\,U_{in}$ pätee vain *jatkuvassa johtumisessa*,
jossa kelan virta ei käy nollassa. Kun kuormavirta on alle puolet
kelavirran rippelistä, tässä alle 60 mA, virta katkeaa joka jaksolla.
*Katkeavassa johtumisessa* kela ottaa syötöstä jokaisella jaksolla
energia-annoksen, joka ei pienene kuorman keventyessä, ja lähtöjännite
nousee, kunnes kuorma kuluttaa annoksen:

```{.python tiedosto="esimerkit/08-buck.py" osa="katkeava"}
```

```{.tuloste tiedosto="esimerkit/08-buck.odotettu" rivit="6-8"}
```

Samalla pulssisuhteella lähtö on kevyellä kuormalla 6,4 V eikä 3,3 V.
Hakkuri tarvitsee siis takaisinkytkennän, joka säätää pulssisuhdetta.

```{.dot otsikko="Jännitemoodin säätö periaatteena. Virhevahvistimen lähtöä verrataan sahalaitaan, ja vertailijan lähtö on kytkimen ohjaus: mitä matalampi lähtöjännite, sitä leveämpi pulssi."}
digraph {
  rankdir=LR;
  ref [shape=plaintext, style="", label="referenssi"];
  ea [label="virhe-\nvahvistin"];
  pwm [label="vertailija\nja sahalaita"];
  aste [label="kytkin,\nkela ja\nkondensaattori"];
  ulos [shape=plaintext, style="", label="lähtö"];
  jako [label="jännitteen-\njako"];
  ref -> ea -> pwm -> aste -> ulos;
  aste -> jako [constraint=false];
  jako -> ea;
}
```

Rakenne on sama kuin lineaarisäätimessä, mutta päästötransistorin
paikalla on vertailija (luku 5) ja tehoaste. Stabiilisuus on
vaikeampi: kela ja kondensaattori muodostavat kaksoisnavan, tässä
2,3 kHz:n taajuudelle, ja katkeavassa johtumisessa tehoasteen vahvistus
muuttuu. Silmukan kompensointi on säätötekniikkaa, ja valmiin
hakkuripiirin datalehti antaa sille mitoitusohjeen.

Hakkurin etu näkyy, kun osiin lisätään häviöt: kytkimelle 0,1 Ω:n
johtamisresistanssi ja diodiksi Schottky-diodi.

```{.python tiedosto="esimerkit/08-buck.py" osa="haviot"}
```

```{.tuloste tiedosto="esimerkit/08-buck.odotettu" rivit="9-12"}
```

Hyötysuhde on 92 %, kun lineaarisäädin samassa tehtävässä jäisi
27,5 %:iin ja lämpenisi 8,7 watin teholla. Suurin häviö on diodin
myötäjännite, ja siksi useimmissa hakkuripiireissä diodin paikalla on
toinen transistori (*synkroninen tasasuuntaus*). Simulaation kytkin
vaihtaa tilaa häviöttä; todellisessa transistorissa jokainen kytkentä
kuluttaa energiaa, joten häviöt kasvavat kytkentätaajuuden mukana.

Samoista osista saa myös nostavan muuntimen (*boost*), kun kela on
syötön ja kytkimen välissä: kelan virta katkaistaan, ja kelan jännite
summautuu syöttöön.

## Lineaarinen vai hakkuri

| Ominaisuus | Lineaarisäädin | Hakkuri |
|------------|----------------|---------|
| hyötysuhde | enintään $U_{ulos}/U_{in}$ | 85 ... 95 % jännitteistä riippumatta |
| lähdön häiriöt | vain kohina, kymmeniä mikrovoltteja | kytkentätaajuinen rippeli ja sen harmoniset |
| ulkoiset osat | kaksi kondensaattoria | kela, kondensaattorit, usein diodi |
| piirilevy | ei kriittinen | virtasilmukat ratkaisevat häiriöt |
| jännitteen nosto | ei mahdollinen | mahdollinen |

Tavallinen ratkaisu on käyttää molempia. Hakkuri tekee suuren
jännite-eron hyvällä hyötysuhteella lähelle tarvittavaa jännitettä, ja
sen perässä LDO puhdistaa syötön analogiaosille pienellä
pudotusjännitteellä. Väliin tulee LC-suodin tai ferriitti, koska
säätimen vaimennus on heikoimmillaan juuri hakkurin taajuudella.

Hakkurin piirilevyllä tärkein asia on silmukka, jossa virta katkeaa
äkisti: tulokondensaattori, kytkin ja diodi. Sen pinta-alan on oltava
mahdollisimman pieni, koska silmukan induktanssi tuottaa luvun 7
ohituskondensaattoriesimerkin jännitepiikit jokaisella kytkennällä.

Datalehdestä kannattaa lukea ensin nämä rivit:

- *Lineaarisäädin:* pudotusjännite omalla kuormavirralla,
  lähtökondensaattorin arvo ja sallittu sarjaresistanssi, PSRR-käyrä
  häiritsevällä taajuudella, lähdön kohina ja sen kaista, lepovirta ja
  kotelon lämpöresistanssi.
- *Hakkuri:* kytkentätaajuus, suositeltu kela ja sen rippelivirta,
  toiminta kevyellä kuormalla ja piirilevyn mallisijoittelu.
- *Referenssi:* alkutarkkuus, lämpötilakerroin (ppm/K), kohina
  kaistalla 0,1 ... 10 Hz ja pitkän ajan ajautuminen. Säädin ei ole
  referenssi: sen tarkkuus on prosentin luokkaa.

## Käytännössä

- Valitse lähtökondensaattori datalehden mukaan, älä tottumuksesta.
  Tarkista sekä arvo että sarjaresistanssin alue ja laske keraamisen
  kondensaattorin kapasitanssi käyttöjännitteellä.
- Mitoita syöttö pudotusjännitteen mukaan pahimmassa tapauksessa:
  suurin kuorma, pienin syöttö ja korkein lämpötila.
- Laske häviöteho ja liitoksen lämpötila. Kun lineaarisäätimen häviö
  ylittää muutaman sata milliwattia, harkitse hakkuria.
- Älä luota säätimeen suodattimena hakkurin taajuudella. Katso
  PSRR-käyrästä vaimennus sillä taajuudella ja lisää suodin.
- Tarkista säätimen vakaus kuorma-askeleella sekä pienimmällä että
  suurimmalla kuormalla. Soiva lähtö kertoo pienestä vaihevarasta.
- Syötä herkät analogiaosat ja AD-muuntimen referenssi omasta
  vähäkohinaisesta säätimestä tai referenssipiiristä, ei logiikan
  käyttöjännitteestä.
- Sijoita hakkurin tulokondensaattori, kytkin ja diodi vierekkäin ja
  noudata valmistajan mallisijoittelua.

## Itsearviointi

- Osaat nimetä lineaarisäätimen osat ja johtaa lähtöjännitteen
  referenssistä ja jännitteenjaosta.
- Osaat selittää, miksi P-kanavaisella päästötransistorilla saadaan
  pieni pudotusjännite ja miksi seuraaja tarvitsee kahden voltin varan.
- Osaat laskea kuorma- ja linjaregulaation virhevahvistimen
  vahvistuksesta ja todentaa ne simuloimalla.
- Osaat mitata säätimen silmukkavahvistuksen ja selittää, miten
  lähtökondensaattorin sarjaresistanssi vaikuttaa vaihevaraan.
- Osaat lukea PSRR-käyrää ja selittää, miksi vaimennus heikkenee
  taajuuden kasvaessa.
- Osaat arvioida säätimen lähtökohinan referenssin kohinasta ja
  takaisinkytkentäkertoimesta.
- Osaat laskea buck-muuntimen lähtöjännitteen, kelavirran rippelin ja
  jatkuvan johtumisen rajan sekä selittää, miksi hakkuri tarvitsee
  takaisinkytkennän.
- Osaat valita lineaarisäätimen ja hakkurin väliltä hyötysuhteen,
  häiriöiden ja lämmön perusteella.
