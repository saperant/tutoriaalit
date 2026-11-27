# Keskeytykset

Luvun 11 ohjelma kyselee laitteitaan: se lukee sarjaportin tilabittiä
silmukassa ja ajastimen laskuria silloin, kun itse haluaa. Oikea
laiteohjelmisto ei toimi näin. Laite ilmoittaa tapahtumasta
*keskeytyksellä*, prosessori siirtyy käsittelijään ja palaa sitten
siihen, mistä lähti, ja joutoajan prosessori nukkuu. Taidot
*Tietokonearkkitehtuuri* ja *Mikrokontrollerit ja
bare-metal-ohjelmointi* käsittelevät mekanismin laitteiston ja
ohjelmoijan kannalta. Tässä luvussa se lisätään prototyyppiin, ja
samalla luvun 9 varoitus muuttuu mitattavaksi: keskeytys on juuri se
kohta, jossa ajallisesti irrotettu prosessori ja muu malli ovat eri
ajassa.

Lisättävää on kolmessa paikassa: laite tarvitsee keskeytyslinjan,
prosessorimalli tavan ottaa keskeytys ja palata siitä, ja ohjelma
käsittelijän.

## Keskeytys on johdin, ei transaktio

Väylätransaktion aloittaa prosessori, ja sillä on osoite. Keskeytys
kulkee toiseen suuntaan, laitteelta prosessorille, eikä siinä ole
osoitetta eikä dataa: se on yksi bitti, joka on päällä niin kauan kuin
laite odottaa palvelua. TLM-2.0:n perusprotokolla ei siksi kata
keskeytyksiä, ja vakiintunut tapa on mallintaa linja samalla
`sc_signal<bool>`-kanavalla kuin luvun 2 johtimet. Laitteessa on
`sc_out<bool>`-portti, prosessorissa `sc_in<bool>`, ja linja kulkee
väylän ohi.

```{.dot otsikko="Prototyyppi keskeytyslinjoineen. Yhtenäiset nuolet ovat TLM-yhteyksiä, katkoviivat signaaleja." leveys="78%"}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.7;
  cpu [label="KeskeytysProsessori\nRV32I + CSR:t"];
  vayla [label="Vayla", style="rounded,filled,bold"];
  ram [label="RAM 64 kt"];
  uart [label="Paateuart"];
  ajastin [label="Tikkiajastin"];
  paate [label="Paate\n(testipenkki)"];
  cpu -> vayla;
  vayla -> ram; vayla -> uart; vayla -> ajastin;
  ajastin -> cpu [label="ajastin_irq", style=dashed, constraint=false];
  uart -> cpu [label="uart_irq", style=dashed, constraint=false];
  paate -> uart [label="vastaanota()", style=dotted];
}
```

Ajastin laajentaa luvun 8 mallia. Rekisteriin `JAKSO` kirjoitettu arvo
käynnistää jaksolliset tikit, jokainen tikki nostaa linjan, ja ohjelma
laskee sen kirjoittamalla rekisteriin `TILA`:

```{.cpp tiedosto="esimerkit/15-keskeytykset/laitteet.hpp" osa="tikkiajastin"}
```

Mallissa on kaksi kohtaa, jotka ratkaisevat, toimiiko se irrotetun
prosessorin kanssa. Ensimmäinen on se, että kirjoitus tulee aloittajan
ajassa. Kun prosessori kirjoittaa rekisteriin, se voi olla
simulaatioaikaa edellä. Laite ei siksi muuta linjaa
`kirjoita`-funktiossa vaan ajastaa tapahtuman, joka laukeaa, kun
simulaatioaika saavuttaa kirjoitushetken:

```{.cpp tiedosto="esimerkit/15-keskeytykset/laitteet.hpp" osa="kirjoitus"}
```

Tämä on sama sääntö kuin luvun 9 aikatietoisella ajastimella: ajasta
riippuva kohde käyttää annotoitua aikaa. Toinen kohta on, että linjaa
ajaa yksi prosessi. `sc_signal` sallii oletuksena yhden kirjoittavan
prosessin, joten tikki ja kuittaus käsitellään samassa metodissa:

```{.cpp tiedosto="esimerkit/15-keskeytykset/laitteet.hpp" osa="linja"}
```

Metodi herää oikealla simulaatiohetkellä, joten linjan reunat ovat
tarkkoja kvantista riippumatta. Epätarkkuus syntyy vasta lukijan
päässä.

Linja on *tasoherkkä*: se pysyy ylhäällä kuittaukseen asti. Jos
seuraava tikki tulee ennen kuittausta, linjassa ei näy uutta reunaa, ja
malli laskee tikin menetetyksi. Sarjaportti `Paateuart` on tehty samalla
kaavalla: saapuva merkki nostaa linjan ja datarekisterin luku laskee
sen. Merkit syöttää testipenkin moduuli `Paate`, joka edustaa linjan
toista päätä.

## Prosessorin poikkeusmekanismi

RISC-V:n etuoikeusmäärittely kuvaa keskeytykset *ohjaus- ja
tilarekistereillä* (CSR, *control and status register*). Malliin
otetaan niistä pienin osa, jolla keskeytyksen voi ottaa ja siitä voi
palata:

```{.cpp tiedosto="esimerkit/15-keskeytykset/csr.hpp" osa="csr"}
```

| Mukana | Jätetty pois |
|-----------------------------|--------------------------------------------|
| konetila (M) | käyttäjä- ja valvojatila, etuoikeustason vaihto |
| `mstatus`: `MIE` ja `MPIE` | `MPP` ja muut kentät |
| `mie` ja `mip`: ajastin ja ulkoinen | ohjelmistokeskeytys, paikalliset keskeytykset |
| `mtvec` suorassa tilassa | vektoroitu tila |
| `mepc`, `mcause` | `mtval`, `mscratch` |
| keskeytykset | synkroniset poikkeukset: virheellinen käsky tai väylävirhe pysäyttää simuloinnin kuten ennen |
| `csrrw`, `csrrs`, `csrrc`, `mret`, `wfi` | CSR-käskyjen välittömät muodot |

Oikeassa RISC-V-järjestelmässä ajastinkeskeytys tulee
ydinkohtaisesta ajastimesta (`mtime`, `mtimecmp`) ja ulkoiset
keskeytykset kootaan keskeytysohjaimessa (PLIC) yhdeksi linjaksi. Tässä
ajastimella on omat rekisterinsä ja sarjaportti on kytketty suoraan
ulkoiseen linjaan, joten ohjainta ei tarvita.

Luvun 11 malli jätti kaksi laajennuskohtaa: SYSTEM-käskyt käsittelee
virtuaalinen `jarjestelma`, ja pääsilmukka `aja` on virtuaalinen.
Uusi prosessori perii vanhan ja lisää linjat ja rekisterit:

```{.cpp tiedosto="esimerkit/15-keskeytykset/keskeytysprosessori.hpp" osa="liitanta"}
```

Keskeytys otetaan käskyjen välissä. Prosessori tallentaa keskeytetyn
käskyn osoitteen, kirjaa syyn, kieltää keskeytykset ja hyppää
käsittelijään. Kaikki muu, kuten rekisterien tallennus, on ohjelman
tehtävä:

```{.cpp tiedosto="esimerkit/15-keskeytykset/keskeytysprosessori.hpp" osa="otto"}
```

CSR-käskyt lukevat rekisterin vanhan arvon ja kirjoittavat uuden
(`csrrw`), asettavat bittejä (`csrrs`) tai nollaavat niitä (`csrrc`).
`mret` palauttaa keskeytystilan ja hyppää takaisin, ja `wfi` (*wait
for interrupt*) pysäyttää prosessorin:

```{.cpp tiedosto="esimerkit/15-keskeytykset/keskeytysprosessori.hpp" osa="jarjestelma"}
```

Pääsilmukka on sama kuin luvussa 11 kahta riviä lukuun ottamatta:
`ota_keskeytys` kutsutaan ennen jokaista käskynhakua, ja lopuksi
kutsutaan `sc_stop`, koska ajastimen prosessi tuottaisi tapahtumia
loputtomiin eikä `sc_start` muuten palaisi.

## Ohjelma

Kokoaja saa uudet käskyt aliluokassa. SYSTEM-käskyt ovat I-tyyppiä,
joten ne koodataan luvun 11 funktiolla:

```{.cpp tiedosto="esimerkit/15-keskeytykset/rv32csr.hpp" osa="kokoaja"}
```

Pääohjelma asettaa pinon ja käsittelijän osoitteen, käynnistää
ajastimen 1733 kellojakson eli 17,33 µs:n jaksolla, sallii molemmat
keskeytyslähteet ja lopuksi keskeytykset. Sen jälkeen se odottaa,
kunnes muistipaikassa `tikit` on kymmenen:

```{.cpp tiedosto="esimerkit/15-keskeytykset/main.cpp" osa="ohjelma"}
```

Käsittelijä lukee syyn rekisteristä `mcause`. Ajastimen tikki
kuitataan ja lasketaan; sarjaportin merkki luetaan ja lähetetään
takaisin. Rekisterit `t0` ja `t1` tallennetaan pinoon, koska
pääohjelma käyttää samoja rekistereitä eikä tiedä, missä kohdassa se
keskeytyy:

```{.cpp tiedosto="esimerkit/15-keskeytykset/main.cpp" osa="kasittelija"}
```

Järjestelmän kokoamisessa uutta ovat vain signaalit ja niiden
kytkennät:

```{.cpp tiedosto="esimerkit/15-keskeytykset/main.cpp" osa="linjat"}
```

Ensimmäinen ajo käyttää mikrosekunnin kvanttia, ja pääohjelma nukkuu
`wfi`-käskyssä. Malli kirjaa linjojen reunat ja prosessorin
keskeytykset aikajärjestykseen. Sarjaportin kaiuttama rivi tulostuu jo
simuloinnin aikana, loki sen jälkeen:

```{.tuloste tiedosto="esimerkit/15-keskeytykset/odotettu" rivit="1-11"}
```

Ensimmäinen tikki tulee hetkellä 17 570 ns: ohjelma kirjoitti
jaksorekisterin omassa ajassaan 240 ns, ja jakso lasketaan siitä.
Prosessori ottaa keskeytyksen 10 ns myöhemmin, kun kesken ollut `wfi`
on suoritettu loppuun. Käsittelijä kuittaa ajastimen 395 ns:n
kuluttua, linja laskee, ja `mret` palauttaa pääohjelmaan.

Kolmas tikki osuu kohtaan, jossa sarjaportin käsittelijä on kesken:

```{.tuloste tiedosto="esimerkit/15-keskeytykset/odotettu" rivit="16-23"}
```

![Sama loki aikajanana. Vasemmalla koko ajo: linjat ovat ylhäällä vain
hetken, ja prosessori on käsittelijässä vain niiden kohdalla. Oikealla
suurennos kolmannesta tikistä: ajastimen linja nousee, kun sarjaportin
käsittelijä on kesken ja keskeytykset on kielletty, joten tikki
otetaan vasta `mret`-käskyn jälkeen.](kuvat/keskeytykset.png){width=100%}

Ajastimen linja nousee hetkellä 52 230 ns, mutta `mstatus.MIE` on
nolla, koska prosessori on käsittelijässä. Tikki odottaa linjalla 420 ns
ja otetaan heti paluun jälkeen. Mitään ei katoa, koska linja on
tasoherkkä: laite pitää pyynnön voimassa, kunnes se kuitataan.

```{.tuloste tiedosto="esimerkit/15-keskeytykset/odotettu" alkaen="ohjelma laski" asti="ohjelma laski"}
```

Koko ajo vei 329 käskyä, ja prosessori nukkui 92 % ajasta.

## Kvantti ja keskeytysviive

Luvussa 9 irrotettu aloittaja näki toisen aloittajan viestit myöhässä.
Keskeytyslinjalle käy samoin. Prosessori lukee linjan arvon
simulaatioajassa, mutta suorittaa käskyjä omassa ajassaan, joka voi
olla kvantin verran edellä. Linjan nousu, joka tapahtuu
simulaatioajassa "tulevaisuudessa", näkyy prosessorille vasta
seuraavan synkronoinnin jälkeen.

Sama ohjelma ajetaan neljällä kvantilla ja kahdella odotustavalla:
`kysely` pyörii silmukassa ja lukee muistipaikkaa `tikit`, `wfi` nukkuu
tikkien välissä.

```{.tuloste tiedosto="esimerkit/15-keskeytykset/odotettu" alkaen="== kvantin" asti="50000  wfi"}
```

![Vasemmalla keskeytysviiveen vaihteluväli kymmenelle tikille.
Kyselevän ohjelman viive on mitä tahansa nollan ja kvantin väliltä,
nukkuvan aina yksi käsky. Oikealla suoritettujen käskyjen
määrä.](kuvat/keskeytysviive.png){width=100%}

- **Nollakvantilla** prosessori synkronoi jokaisen käskyn jälkeen
  (4365 synkronointia), ja viive on enintään käskyn mittainen.
- **Kyselevän ohjelman viive kasvaa kvantin mukana.** Mikrosekunnin
  kvantilla se on 105–815 ns ja kymmenen mikrosekunnin kvantilla jo
  8,5 µs. Viive ei ole ohjelman eikä laitteen ominaisuus vaan mallin:
  sama ohjelma oikealla piirillä vastaisi muutamassa kellojaksossa.
- **Kun kvantti ylittää tikkien jakson, tikkejä katoaa.** 50 µs:n
  kvantilla prosessori näkee linjan vain 50 µs:n välein. Sillä välin
  ajastin on tikittänyt kahdesti tai kolmesti, mutta linja on ollut
  koko ajan ylhäällä. Ajastin menetti 16 tikkiä, ja ohjelma tarvitsi
  kymmenen tikin laskemiseen 452 µs eikä 174 µs: ohjelmiston kello
  jätättää.
- **`wfi` poistaa viiveen kokonaan.** Nukkuva prosessori synkronoi ja
  jää odottamaan linjan tapahtumaa, joten se herää täsmälleen nousun
  hetkellä kvantista riippumatta:

```{.cpp tiedosto="esimerkit/15-keskeytykset/keskeytysprosessori.hpp" osa="synkronointi"}
```

`wfi` on myös nopeuskeino. Kyselevä ohjelma suorittaa 4355 käskyä,
nukkuva 275, eli kuudestoistaosan. Simulaattori ei tee nukkuvan
prosessorin puolesta mitään: aika hyppää suoraan seuraavaan
tapahtumaan. Oikeassa virtuaaliprototyypissä käyttöjärjestelmän
joutosilmukka on `wfi`, ja suurin osa simuloidusta ajasta kuluu siinä.

## Linjan taso ja paluu käsittelijästä

`mret`-käskyn toteutuksessa on synkronointi, jota oikeassa
prosessorissa ei ole. Syy on sama aikaero toisin päin. Käsittelijä
kuittaa laitteen kirjoituksella, ja laite ajastaa linjan laskun
kirjoitushetkeen. Jos prosessori on edellä, se hetki on
simulaatioajassa vielä tulossa. Kun `mret` sallii keskeytykset
uudelleen ja prosessori lukee linjan, se näkee yhä ykkösen ja ottaa
saman keskeytyksen toiseen kertaan.

Koe ajaa kyselevän ohjelman ilman tätä synkronointia:

```{.tuloste tiedosto="esimerkit/15-keskeytykset/odotettu" alkaen="== koe"}
```

Jokainen tikki käsitellään kahdesti. Ohjelma laskee kymmenen tikkiä,
vaikka ajastin antoi viisi, ja lopettaa puolessa ajassa. Malli toimisi
nollakvantilla ja hajoaisi kaikilla muilla, mikä on luvun 9 mukaan
merkki virheestä: tulos ei saa riippua kvantista.

Sääntö on yleinen: irrotettu aloittaja synkronoi ennen kuin se lukee
signaalia, jonka arvoon sen oma aiempi transaktio vaikuttaa. Laitteen
ei auta kirjoittaa linjaa suoraan `b_transport`issa, koska signaalin
uusi arvo tulee näkyviin vasta seuraavassa delta-syklissä, eikä
keskeytymättä jatkava prosessori päästä simulaattoria sinne.

## Käytännössä

- **Keskeytyslinja on signaali, ja laite ajoittaa sen reunat.** Linjan
  nousu ja lasku tapahtuvat oikealla simulaatiohetkellä, vaikka
  kirjoitus tuli irrotetulta aloittajalta. Tarkista laitemallista
  kolme asiaa: reunan ajoitus, kuittauksen vaikutus ja se, mitä
  tapahtuu, kun uusi tapahtuma tulee ennen kuittausta.
- **Kvantti mitoitetaan lyhimmän keskeytysjakson mukaan.** Jos
  ohjelmisto ei koskaan nuku, kvantin on oltava selvästi tikkien
  jaksoa pienempi. Nukkuva ohjelmisto sietää suuren kvantin, koska
  `wfi` synkronoi.
- **Ajoitusvirhettä etsitään pienellä kvantilla.** Keskeytysviive,
  jonka malli näyttää, on enintään kvantin tarkka. Kun kysymys on
  vasteajasta, se mitataan RTL:stä: taito *SoC-integraatio* tekee sen
  kellojakson tarkkuudella.
- **Valmis ISS tekee prosessorin osuuden puolestasi.** QEMU, Spike ja
  kaupalliset mallit toteuttavat etuoikeusmäärittelyn kokonaan ja
  tunnistavat `wfi`:n. Laitemallin kirjoittajan vastuulle jää linjan
  oikea käytös.
- **Keskeytys on myös testattava virhetilanne.** Mallissa keskeytyksen
  voi viivästää, kadottaa tai antaa kahdesti täsmälleen halutulla
  hetkellä, ja ajurin käytöksen voi toistaa. Oikealla laitteella sama
  vaatii onnea.

## Itsearviointi

- Osaat mallintaa keskeytyslinjan signaalina ja selittää, miksi se ei
  kulje väyläsoketin kautta.
- Osaat kirjoittaa laitemallin, joka nostaa ja laskee linjan oikealla
  simulaatiohetkellä, kun rekisterikirjoitus tulee ajallisesti
  irrotetulta aloittajalta.
- Osaat kertoa, mitä prosessori tekee ottaessaan keskeytyksen ja
  palatessaan siitä ja mitkä rekisterit siihen tarvitaan.
- Osaat ennustaa, miten kvantti vaikuttaa keskeytysviiveeseen ja
  milloin tikkejä alkaa kadota, ja perustella, miksi `wfi` korjaa
  molemmat.
- Osaat selittää, miksi irrotetun prosessorin on synkronoitava ennen
  kuin se lukee linjan, jonka se on juuri kuitannut.
