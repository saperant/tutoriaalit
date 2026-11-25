# Tiedostomuodot ja protokollat

Takaisinmallinnus ei rajoitu koodiin. Dokumentoimaton tiedostomuoto tai
verkkoprotokolla pitää usein selvittää yhteentoimivuuden tai
vianetsinnän vuoksi. Menetelmä on sama kuin koodissa: havainnoi,
muodosta hypoteesi, tarkista se. Hypoteesin tarkistus on tässä
poikkeuksellisen vahva: kun muodon osaa jäsentää ja kirjoittaa
uudelleen tavulleen samaksi, se on ymmärretty kokonaan.

## Rakenteen havainnointi

Kohteena on mittalaitteen tallennustiedosto. Ensimmäinen työkalu on
heksavedos: tavut ja niiden tulostuvat merkit rinnakkain.

```{.bash tiedosto="esimerkit/09-muoto/aja.sh" osa="heksa"}
```

```{.tuloste tiedosto="esimerkit/09-muoto/odotettu" osa="t1"}
```

Jo tästä erottuu rakennetta: tiedosto alkaa tunnisteella `KMTD`
(*magic number*), ja merkkijonot `olohuone`, `parveke` ja `kellari`
toistuvat. Tunnisteen jälkeen on pieniä lukuja, ja merkkijonoja edeltää
tavu, joka näyttää niiden pituudelta (`08` ennen kahdeksanmerkkistä
`olohuone`).

*Entropia* erottaa rakenteen satunnaiselta tai salatulta datalta.
Tekstin ja pienten lukujen entropia on matala, pakatun tai salatun
datan lähellä kahdeksaa bittiä tavua kohti:

```{.tuloste tiedosto="esimerkit/09-muoto/odotettu" osa="t2"}
```

Tiedoston loppuosa (siirtymästä `0x60` alkaen) on korkeamman entropian
aluetta: siellä on jotain salattua tai pakattua. Tämä on tärkeä
havainto heti alussa: osa tiedostoa ei aukea pelkällä rakenteen
päättelyllä.

## Kenttien tunnistaminen

Lukukentät tunnistaa arvoalueesta ja säännöllisyydestä.
Aikaleimat ovat suuria, uskottavalle aikavälille osuvia lukuja, jotka
kasvavat tasaisin välein; pituuskentät ovat pieniä lukuja, jotka
vastaavat tiedoston rakennetta. Skripti `tutki.py` etsii molempia.
Yksittäinen aikaleimalta näyttävä luku on usein sattumaa, joten skripti
etsii pisimmän ketjun, jossa aika kasvaa vähän ja siirtymä tasaisesti:

```{.python tiedosto="esimerkit/09-muoto/tutki.py" osa="luvut"}
```

```{.tuloste tiedosto="esimerkit/09-muoto/odotettu" osa="t4"}
```

Aikaleimat ovat 18 ja 17 tavun välein ja kasvavat 300 sekuntia
kerrallaan: viiden minuutin mittausväli. Tietueen koko vaihtelee, koska
nimen pituus vaihtelee. Pituuskenttä `192` osoittaa korkean entropian
lohkoon, ja tiedoston neljä viimeistä tavua ovat CRC-32-tarkiste koko
edeltävästä datasta, mikä selvisi kokeilemalla eri tarkistealgoritmeja.

## Jäsennin tarkistuksena

Kun rakenne on päätelty, siitä kirjoitetaan jäsennin. Jäsennin on
hypoteesin tarkistus: jos se jäsentää tiedoston, tulostaa järkevät
arvot ja osaa kirjoittaa tiedoston uudelleen tavulleen samaksi, muoto
on ymmärretty. Tämä on tiukin mahdollinen testi.

```{.bash tiedosto="esimerkit/09-muoto/aja.sh" osa="jasenna"}
```

```{.tuloste tiedosto="esimerkit/09-muoto/odotettu" osa="t5"}
```

```{.dot otsikko="Päätelty tiedostomuoto. Otsaketta seuraa vaihtelevan pituisia mittaustietueita, sitten pituuskentällä alkava kalibrointilohko ja lopuksi tarkiste. Luvut ovat little endian -muodossa."}
digraph {
  nodesep=0.25; ranksep=0.3;
  node [shape=plain, style=""];
  t [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" colspan="6"><i>tiedosto</i></td></tr>
    <tr><td bgcolor="#EEF1F6">"KMTD"<br/><font point-size="8">4 tavua</font></td><td bgcolor="#EEF1F6">versio<br/><font point-size="8">u16</font></td><td bgcolor="#EEF1F6">liput<br/><font point-size="8">u16</font></td><td bgcolor="#EEF1F6">määrä<br/><font point-size="8">u32</font></td><td port="m" width="110">mittaus × määrä<br/><font point-size="8">10 + nimen pituus</font></td><td>lohkon koko<br/><font point-size="8">u32</font></td><td>kalibrointilohko<br/><font point-size="8">salattu</font></td><td>CRC-32<br/><font point-size="8">u32</font></td></tr>
  </table>>];
  m [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" colspan="6"><i>mittaus</i></td></tr>
    <tr><td>aikaleima<br/><font point-size="8">u32</font></td><td>lämpötila × 100<br/><font point-size="8">i16</font></td><td>kosteus × 10<br/><font point-size="8">u16</font></td><td>anturi<br/><font point-size="8">u8</font></td><td>nimen pituus<br/><font point-size="8">u8</font></td><td>nimi<br/><font point-size="8">pituuden verran</font></td></tr>
  </table>>];
  t:m:s -> m:n;
}
```

Jäsennin lukee otsakkeen, mittaukset ja kalibrointilohkon, tarkistaa
CRC:n ja kirjoittaa tiedoston uudelleen: tulos on identtinen. Korkean
entropian lohko jää salatuksi, mutta sen rajat ja tarkiste tunnetaan,
joten tiedoston rakenne on silti täysin hallussa. Yhden bitin muutos
otsakkeessa jää kiinni CRC-tarkistuksesta. Jäsennin on samalla
yhteentoimiva toteutus: sillä voi lukea ja tuottaa saman muodon
tiedostoja.

Jäsennintä kirjoittaessa noudatetaan samaa varovaisuutta kuin minkä
tahansa epäluotettavan syötteen kanssa (*Verkko-ohjelmointi*,
protokollan jäsennys): pituudet tarkistetaan ennen käyttöä, eikä
tiedostoon luoteta. Takaisinmallinnettu muoto tulee usein juuri
lähteestä, johon ei voi luottaa.

## Protokollan päättely kaappauksesta

Verkkoprotokolla päätellään samoin, mutta aineistona on liikenteen
kaappaus. Kohteena on ohjaimen ja laitteen sarjaliikenne, joka on
tallennettu tietueiksi (suunta, pituus, kehys). Skripti `paattele.py`
etsii kehyksistä vakiokentät, pituuden, järjestysnumeron, pyynnön ja
vastauksen suhteen sekä tarkistesumman:

```{.bash tiedosto="esimerkit/10-protokolla/aja.sh" osa="paattele"}
```

```{.tuloste tiedosto="esimerkit/10-protokolla/odotettu" osa="t2"}
```

```{.dot otsikko="Päätelty kehys. Tarkiste on tyypin, järjestysnumeron, pituuden ja hyötykuorman tavujen summa modulo 256."}
digraph {
  node [shape=plain, style=""];
  k [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0"><font point-size="8">tavu 0</font></td><td border="0"><font point-size="8">1</font></td><td border="0"><font point-size="8">2</font></td><td border="0"><font point-size="8">3</font></td><td border="0"><font point-size="8">4 …</font></td><td border="0"><font point-size="8">viimeinen</font></td></tr>
    <tr><td bgcolor="#EEF1F6">tahdistus<br/><font point-size="8">0xa5</font></td><td>tyyppi<br/><font point-size="8">vastaus: | 0x80</font></td><td>järjestysnumero</td><td>pituus <i>n</i></td><td width="120">hyötykuorma<br/><font point-size="8"><i>n</i> tavua</font></td><td>tarkiste</td></tr>
  </table>>];
}
```

Päättely tunnistaa kehyksen rakenteen: tahdistustavu `0xa5`, tyyppi,
järjestysnumero, pituus, hyötykuorma ja tarkistesumma. Vastauksen tyyppi
on pyynnön tyyppi tai-operoituna `0x80`:llä, ja vastaus kaiuttaa
pyynnön järjestysnumeron. Nämä ovat protokollien tavallisia kuvioita,
ja niiden tunnistaminen on puoli työtä. Pyyntö–vastaus-pareista näkee
komennot: `0x03` kysyy nimen, `0x01` lukee tilan, `0x02` asettaa
arvon ja saa vastaukseksi vanhan arvon. Oikeassa työssä kaappaus
saadaan Wiresharkilla, loogisella analysaattorilla tai väylän
koukutuksella, ja monimutkaisempaan päättelyyn on työkaluja kuten
Wiresharkin omat erittelijät ja protokollatoteutuksen fuzzaus
(*Haavoittuvuuksien analyysi ja torjunta*).

## Käytännössä

- **Katso ensin heksavedos ja entropia.** Tunniste, toistuvat
  merkkijonot ja matalan entropian alueet kertovat, mikä on rakennetta
  ja mikä salattua tai pakattua.
- **Tunnista kentät alueesta ja säännöllisyydestä**: aikaleimat
  kasvavina lukuina, pituudet rakennetta vastaavina, tarkisteet
  tiedoston lopussa.
- **Kirjoita jäsennin ja kirjoita tiedosto uudelleen.** Tavulleen sama
  tulos on todiste siitä, että muoto on ymmärretty; ero osoittaa, mitä
  jäi selittämättä.
- **Käytä samaa menetelmää protokollaan.** Kaappaus korvaa tiedoston;
  pyyntö–vastaus-parit ja toistuvat kentät paljastavat rakenteen.
- **Käsittele takaisinmallinnettu syöte epäluotettavana.** Tarkista
  pituudet ja rajat; älä luota tiedoston omiin kokokenttiin.

## Itsearviointi

- Osaat tutkia tuntematonta tiedostoa heksavedoksella ja entropialla
  ja erottaa rakenteen salatusta datasta.
- Osaat tunnistaa aikaleima-, pituus- ja tarkistekentät arvoalueesta
  ja säännöllisyydestä.
- Osaat kirjoittaa jäsentimen ja perustella, miksi tiedoston
  uudelleenkirjoitus on vahva tarkistus.
- Osaat päätellä binääriprotokollan kehysrakenteen liikennekaappauksesta.
