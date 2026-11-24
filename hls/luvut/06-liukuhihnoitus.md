# Liukuhihnoitus

Liukuhihnattomassa silmukassa kierros alkaa vasta, kun edellinen on
valmis, joten suurin osa laitteistosta on suurimman osan ajasta
käyttämättä: pistetulon kertoja laskee yhden jakson kahdesta.
*Liukuhihnoitettu* silmukka (*pipelined loop*) aloittaa uuden
kierroksen ennen kuin edellinen on valmis. Kierrosten väli on
*aloitusväli* II (*initiation interval*), ja tavoite on yleensä II = 1:
uusi kierros joka jaksolla.

## Latenssi ja läpäisy

Kun kierroksen pituus on *L* jaksoa ja kierroksia *N*, liukuhihnoitettu
silmukka vie

*latenssi = (N − 1) · II + L* jaksoa.

Kun *N* on suuri, latenssi on noin *N · II*, eikä kierroksen pituudella
ole juuri merkitystä. Siksi liukuhihnaa voi pidentää vapaasti, jos se
auttaa saavuttamaan pienemmän II:n tai lyhyemmän kellojakson.
*Läpäisy* (*throughput*) on kierroksia jaksossa, 1 / II. minihls pyöristää
kierroksen pituuden ylöspäin II:n monikertaan, koska sen liukuhihnan
vaiheet ovat kukin II jakson pituisia: sen latenssi on
*(N + S − 1) · II*, missä $S = \lceil L / \mathit{II} \rceil$ on vaiheiden määrä.

Pistetulon liukuhihnoittamiseen riittää yksi pragma silmukan rungon
alkuun:

```{.cpp tiedosto="esimerkit/06-liukuhihna/mac_putki.cpp" osa="pragma"}
```

```{.tuloste tiedosto="esimerkit/06-liukuhihna/odotettu"}
```

Ajoitus on sama kuin liukuhihnattomana, mutta kierrokset limittyvät:

| Jakso | 0 | 1 | 2 | 3 | 4 | ... | 8 |
|------------------------|-----|-----|-----|-----|-----|-----|-----|
| vaihe 0: lue a[i], b[i] | i=0 | i=1 | i=2 | i=3 | i=4 | ... | |
| vaihe 1: s += tulo | | i=0 | i=1 | i=2 | i=3 | ... | i=7 |

Sama ero näkyy simuloidusta RTL:stä. Alla olevista kuvista ensimmäinen
on johdannon liukuhihnaton pistetulo ja toinen sama liukuhihnoitettuna,
molemmat samalla syötteellä. Muistin luku `a_ce0` on liukuhihnattomassa
versiossa ylhäällä joka toisella jaksolla, liukuhihnoitetussa joka
jaksolla, ja `ap_done` nousee seitsemän jaksoa aiemmin.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/mac-ap-ctrl.json" otsikko="Pistetulo ilman liukuhihnaa (II = 2) simulaatiosta"}
```

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/mac-putki.json" otsikko="Pistetulo liukuhihnoitettuna (II = 1) simulaatiosta"}
```

Kahdeksan kierrosta vievät 9 jaksoa 16:n sijaan. Koko funktion latenssi
laski 19 jaksosta 12 jaksoon, ja ero kasvaa kierrosmäärän mukana:
1 000 kierroksella 2 003 jaksosta 1 004 jaksoon. Liukuhihnan täyttyminen
alussa ja tyhjeneminen lopussa (*prologue* ja *epilogue*) vievät yhteensä
*L − 1* jaksoa.

## Modulo-ajoitus

Liukuhihnassa samalla jaksolla on käynnissä useita kierroksia eri
vaiheissa. Kaksi operaatiota, jotka on ajoitettu jaksoille *t₁* ja *t₂*,
käyttävät laitteistoa samaan aikaan, jos *t₁ mod II = t₂ mod II*. Siksi
liukuhihnan ajoitus varaa resurssit *modulo-varaustaulukosta*
(*modulo reservation table*), jossa on II paikkaa. minihls:n
listaajoitus tekee juuri tämän: resurssin paikka on `jakso % ii`.

Aloitusvälillä on kaksi alarajaa:

- **ResMII**, resurssien raja: jos kierros käyttää resurssia *n* kertaa
  ja yksiköitä on *k*, on $\mathit{II} \geq \lceil n / k \rceil$. Muistiportti on tavallisin
  rajoittaja (luku 7).
- **RecMII**, takaisinkytkennän raja: jos arvo kulkee kierroksesta
  seuraavaan riippuvuusketjua pitkin, jonka viive on *d* jaksoa ja
  etäisyys *e* kierrosta, on $\mathit{II} \geq \lceil d / e \rceil$.

minihls laskee ResMII:n etukäteen ja kokeilee sitten aloitusvälejä
siitä ylöspäin. Jokaisella II:n arvolla ajoitetaan ja tarkistetaan
*kantamat riippuvuudet* (*loop-carried dependences*). Jos ehto ei
toteudu, riippuvuuden kohdetta yritetään ensin siirtää myöhemmäksi
samalla II:llä, ja vasta sitten II:tä kasvatetaan:

```{.python tiedosto="esimerkit/minihls/ajoitus.py" osa="modulo"}
```

Tämä on yksinkertaistettu versio Raun *iteratiivisesta
modulo-ajoituksesta* (*iterative modulo scheduling*, 1994), jota
käytetään sekä HLS-työkaluissa että VLIW-prosessorien kääntäjissä.
Oikea algoritmi poistaa ja sijoittaa operaatioita uudelleen, kunnes
kaikki ehdot täyttyvät tai yrityksiä on tehty liikaa.

## Takaisinkytkentä rajoittaa

Ensimmäisen kertaluvun IIR-suodin päivittää tilaansa jokaisella
näytteellä. Uusi tila riippuu edellisestä, joten kierros ei voi alkaa
ennen kuin edellisen kierroksen tila on laskettu:

```{.cpp tiedosto="esimerkit/06-takaisinkytkenta/iir.cpp" osa="ydin"}
```

Tilan kautta kulkevassa ketjussa ovat vähennyslasku, kertolasku ja
yhteenlasku: 2 + 6 + 2 = 10 ns. 8 ns:n kellolla ketju ei mahdu yhteen
jaksoon, joten se vie kaksi jaksoa ja II on vähintään 2:

```{.tuloste tiedosto="esimerkit/06-takaisinkytkenta/odotettu" osa="ajo1"}
```

Raportti kertoo syyn: muuttuja `tila`. Vitis HLS ilmoittaa saman
tilanteen varoituksella *"Unable to enforce a carried dependence
constraint"* ja kertoo, mikä operaatio ja muuttuja ovat ketjussa.

Ratkaisu on kirjoittaa laskenta niin, että takaisinkytkentään jää
vähemmän. Kokonaisluvuilla $t + \lfloor (x - t) K / 256 \rfloor$ on sama kuin
$\lfloor (t (256 - K) + x K) / 256 \rfloor$, koska *t* on kokonaisluku. Uudessa
muodossa syötteen kertolasku ei riipu tilasta, ja ketjuun jäävät vain
tilan kertolasku ja yhteenlasku, 8 ns:

```{.cpp tiedosto="esimerkit/06-takaisinkytkenta/iir_lyhyt.cpp" osa="rivi"}
```

```{.tuloste tiedosto="esimerkit/06-takaisinkytkenta/odotettu" osa="ajo2"}
```

Liukuhihna piteni neljään vaiheeseen, ja kertojia tarvitaan kaksi,
mutta II on 1 ja silmukka vie 19 jaksoa 34:n sijaan. Tila luetaan
jaksolla 2 ja kirjoitetaan saman jakson lopussa, joten seuraava kierros
saa sen omalla jaksollaan 2, yhtä jaksoa myöhemmin. Samat testivektorit
menivät läpi molemmilla, joten uudelleenkirjoitus säilytti tulokset
bitilleen. Liukuluvuilla sama muunnos muuttaisi pyöristyksiä, ja
tulokset poikkeaisivat hieman.

## Liukuhihnan ohjaus

Liukuhihnan jokaisella vaiheella on voimassaolobitti. Bittivektori
`l2_v` siirtyy askeleen jokaisen kierroksen lopussa, ja vaiheeseen 0
tulee ykkönen niin kauan kuin kierroksia on aloittamatta. Aktiivisuus
vaatii, että jakson vaihe on voimassa, joten täyttymis- ja
tyhjenemisvaiheessa vain osa liukuhihnasta toimii:

```{.verilog tiedosto="esimerkit/06-takaisinkytkenta/iir_lyhyt.v" osa="vaiheet"}
```

```{.verilog tiedosto="esimerkit/06-takaisinkytkenta/iir_lyhyt.v" osa="ohjaus"}
```

## Vaiherekisterit

Kun arvoa tarvitaan myöhemmässä vaiheessa, sen on kuljettava
liukuhihnassa oman kierroksensa mukana, koska samaan aikaan seuraavat
kierrokset tuottavat jo omia arvojaan. Silmukkamuuttuja `t3` tarvitaan
jaksolla 3 tuloksen osoitteeksi, joten se kulkee kolmen
*vaiherekisterin* läpi:

```{.verilog tiedosto="esimerkit/06-takaisinkytkenta/iir_lyhyt.v" osa="muuttujat"}
```

```{.verilog tiedosto="esimerkit/06-takaisinkytkenta/iir_lyhyt.v" osa="datapolku"}
```

```{.verilog tiedosto="esimerkit/06-takaisinkytkenta/iir_lyhyt.v" osa="kytkennat"}
```

```{.verilog tiedosto="esimerkit/06-takaisinkytkenta/iir_lyhyt.v" osa="paivitykset"}
```

Arvo kirjoitetaan ensimmäiseen vaiherekisteriin sillä jaksolla, jolla
se valmistuu (`l2_j0`), ja siirretään eteenpäin kierroksen lopussa.
Kun II = 1, jokainen jakso on kierroksen loppu. Tilarekisteri `m_tila`
on ainoa, jota ei vaiheisteta: se on koko silmukan yhteinen, ja
kantama riippuvuus takaa, että seuraava kierros lukee sen vasta
kirjoituksen jälkeen.

## Pysäyttäminen

Jos liukuhihnan syöte ei ole valmis, koko liukuhihnan on odotettava.
minihls pysäyttää koko piirin yhdellä sallintasignaalilla (luku 9).
Vitis HLS:ssä tavat ovat *stall* (oletus, koko liukuhihna pysähtyy),
*flushable* (tyhjät vaiheet voivat edetä) ja *free-running* (vaiheet
etenevät aina, ja voimassaolo kulkee datan mukana); ne valitaan
pragmalla `pipeline style=stp|flp|frp`.

## Käytännössä

- **Liukuhihnoita sisin silmukka ensin** ja tavoittele II = 1. Lue
  raportista saavutettu II ja syy, jos se on suurempi.
- **ResMII vai RecMII?** Jos syy on resurssi, lisää yksiköitä tai
  muistiportteja (luku 7). Jos syy on takaisinkytkentä, lyhennä
  ketjua: siirrä laskentaa pois takaisinkytkennästä tai käytä useampaa
  rinnakkaista akkua.
- **Pitkä liukuhihna on halpa.** Lisävaiheet maksavat rekistereitä ja
  muutaman jakson latenssia mutta eivät läpäisyä.
- **Kellojakso ja II ovat kytköksissä.** Lyhyempi kellojakso pidentää
  takaisinkytkentää jaksoina ja voi kasvattaa II:tä; aikayksikköinä
  läpäisy voi silti parantua.

## Itsearviointi

- Osaat laskea liukuhihnoitetun silmukan latenssin kierrosmäärästä,
  aloitusvälistä ja kierroksen pituudesta.
- Osaat selittää modulo-varaustaulukon ja laskea ResMII:n resurssien
  käytöstä.
- Osaat tunnistaa koodista silmukan kantaman riippuvuuden ja arvioida
  sen asettaman RecMII:n.
- Osaat lyhentää takaisinkytkentää kirjoittamalla laskennan uudelleen
  ja todentaa, että tulokset säilyvät.
- Osaat selittää voimassaolobittien ja vaiherekisterien tehtävän
  tuotetussa RTL:ssä.
