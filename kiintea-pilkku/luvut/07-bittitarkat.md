# Bittitarkat mallit

Laitteistosuunnittelun tavallinen vuo etenee kolmessa vaiheessa.
Algoritmi kehitetään liukuluvuilla (Python, MATLAB), sitten siitä tehdään
*bittitarkka* malli (*bit-true*, *bit-accurate*), joka laskee täsmälleen
samoilla leveyksillä, pyöristyksillä ja saturaatioilla kuin laitteisto,
ja lopuksi RTL toteutetaan mallin mukaan. Bittitarkka malli on
RTL-testipenkin referenssi: sen ja RTL:n tulosten on oltava samat bitti
bitiltä, ei ”lähes samat”.

## FIR-suodatin kahdella kielellä

Esimerkkinä on 15-kertoiminen alipäästö. Kertoimet ovat Q1.15-muodossa,
kertymä 64-bittinen (laitteistossa riittäisi 36 bittiä), ja tulos
pyöristetään lähimpään parilliseen ja saturoidaan Q1.15:een. Testisyöte
tuotetaan lineaarisella kongruenssigeneraattorilla, jonka molemmat
kielet osaavat laskea täsmälleen samoin:

```{.c tiedosto="esimerkit/07-fir.c" osa="syote"}
```

```{.c tiedosto="esimerkit/07-fir.c" osa="suodatin"}
```

C-toteutus on lähellä laitteistoa: tyypit ovat kiinteän levyisiä, ja
jokainen kavennus on näkyvä. Python-mallissa kokonaisluvut ovat
rajattomia, joten mallin kirjoittaja päättää itse jokaisen kavennuksen.
Pythonin `>>` on aina aritmeettinen, ja `&` toimii negatiivisilla
luvuilla kuin äärettömän leveällä kahden komplementin luvulla, mikä
tekee pyöristyksestä suoraviivaista:

```{.python tiedosto="esimerkit/07-fir-malli.py" osa="syote"}
```

```{.python tiedosto="esimerkit/07-fir-malli.py" osa="malli"}
```

Molemmat laskevat 200 näytettä, tulostavat ensimmäiset ja tiivisteen
kaikista ulostuloista sekä suurimman eron double-tarkkuudella
laskettuun samaan suodattimeen:

```{.c tiedosto="esimerkit/07-fir.c" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/07-fir.odotettu"}
```

Python-mallin tuloste on bitilleen sama: testit vertaavat molempia
samaan odotettuun tulosteeseen. Ero double-laskentaan
on enintään 0,5 LSB, eli ainoa virhe on lopun pyöristys. Kertymässä ei
ole virhettä, koska kertymä on riittävän leveä eikä välissä pyöristetä.

Tiiviste on käytännöllinen tapa verrata pitkiä tulosjonoja: RTL-simulaatio
laskee saman tiivisteen, ja ensimmäinen poikkeava näyte etsitään vasta,
kun tiivisteet eroavat. Tässä käytetty FNV-1a on yksinkertainen ja
riittää testaukseen; se ei ole kryptografinen tiiviste.

## Sama kavennus laitteistokuvauskielellä

Malli on olemassa laitteistoa varten, joten on syytä nähdä kerran, miltä
sama kavennus näyttää SystemVerilogilla. Kertymä on 36-bittinen
etumerkillinen vektori: 32-bittinen tulo ja neljä vartijabittiä, jotka
15 tapin summa säännön mukaan tarvitsee. (Kertoimien $\ell_1$-normi on
1,16, joten yksikin riittäisi.) Jokainen mallin operaatio vastaa
johdotusta tai pientä logiikkaa:

```{.systemverilog tiedosto="esimerkit/07-fir-rtl.sv" osa="kavenna"}
```

Aritmeettinen siirto `>>>` ja bittileikkaus `kertyma[14:0]` ovat pelkkää
johdotusta. Logiikkaa syntyy vain vertailusta puolikkaaseen, yhden
lisäyksestä ja saturaation multiplekseristä. Avainsana `signed` on
välttämätön: ilman sitä `>>>` täyttäisi nollilla ja vertailut olisivat
etumerkittömiä, eikä kääntäjä varoita. Testipenkki ajaa saman
generaattorin tuottamat 200 näytettä ja laskee saman tiivisteen:

```{.systemverilog tiedosto="esimerkit/07-fir-rtl.sv" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/07-fir-rtl.odotettu"}
```

Tiiviste `4c6887fe` on sama kuin C- ja Python-mallissa, eli kolme
toteutusta kolmella kielellä tuottavat bitilleen saman tuloksen.
Rekisterit, liukuhihnat ja kättelyt tämän laskennan ympärillä ovat
taidon *DSP-algoritmien laitteistototeutus* aihe.

## CORDIC

FIR-suodattimessa virhe syntyy yhdessä kohdassa, lopun pyöristyksessä.
Toinen esimerkki näyttää mallin toisen käyttötavan: iteratiivisessa
algoritmissa bittejä katkeaa joka kierroksella, ja mallilla mitoitetaan
kierrosten määrä ja välitulosten vartijabitit ennen kuin laitteistoa on
olemassa.

CORDIC (*coordinate rotation digital computer*) laskee trigonometrisia
funktioita pelkillä yhteenlaskuilla, siirroilla ja pienellä
vakiotaulukolla. Vektoria kierretään vakiokulmin $\pm\arctan 2^{-i}$, ja
kierto kertoimella $2^{-i}$ on siirto. Jokainen iteraatio on yksi
liukuhihnavaihe tai yksi kellojakso, ja jokainen tuottaa noin yhden
bitin lisää tarkkuutta:

```{.c tiedosto="esimerkit/07-cordic.c" osa="cordic"}
```

```{.c tiedosto="esimerkit/07-cordic.c" osa="tarkkuus"}
```

```{.tuloste tiedosto="esimerkit/07-cordic.odotettu"}
```

Mallin avulla suunnittelija valitsee iteraatioiden määrän ja
sanaleveyden ennen kuin riviäkään RTL:ää on kirjoitettu: 16-bittiseen
ulostuloon tarvitaan noin 16 iteraatiota ja muutama vartijabitti
välituloksiin, koska jokaisen iteraation siirto katkaisee bittejä.
Vahvistus $K \approx 1{,}6468$ kompensoidaan alkuarvolla $1/K$, joten
kertolaskua ei tarvita lainkaan. CORDICin laitteistorakenteet
(iteratiivinen ja liukuhihnoitettu) ja kiertotila ovat taidossa
*DSP-algoritmien laitteistototeutus*.

## Bittitarkan mallin rakenne

Hyvä bittitarkka malli on kirjoitettu laitteiston rakenteen mukaan:
jokaiselle rekisterille ja väylälle on muuttuja, jonka leveys ja muoto
ovat samat kuin RTL:ssä, ja jokainen kavennus tehdään nimetyllä
funktiolla (`pyorista_parilliseen`, `saturoi16`). Mallia ajetaan samoilla
testivektoreilla kuin RTL:ää, ja testipenkki vertaa jokaisen näytteen.
Kun bittitarkan mallin tulos on vertailtu double-referenssiin ja todettu
riittäväksi, RTL:n ei tarvitse olla ”oikein” missään abstraktissa
mielessä, vaan sen tarvitsee vain vastata mallia.

## Käytännössä

- **Kolme tasoa: double, bittitarkka, RTL.** Double-malli kertoo, mitä
  algoritmin pitäisi tehdä. Bittitarkka malli kertoo, mitä laitteisto
  tekee, ja sen poikkeama double-mallista on mitoitettu. RTL:n on
  vastattava bittitarkkaa mallia täsmälleen.
- **Vertaa bitit, älä toleransseja.** RTL:n ja bittitarkan mallin
  vertailussa toleranssi piilottaa virheitä. Toleranssi kuuluu vain
  bittitarkan ja double-mallin väliin.
- **Nimeä kavennukset.** Jokainen pyöristys ja saturaatio on oma
  funktionsa, jonka nimi kertoo tavan. Rivinsisäiset siirrot ovat
  vaikeita tarkistaa.
- **Tuota testivektorit deterministisesti.** Oma pseudosatunnainen
  generaattori tai tiedosto, ei kielen kirjaston satunnaislukuja, joiden
  algoritmi voi vaihtua versiosta toiseen.
- **Python mallikieleksi, C nopeuteen.** Python on helppo kirjoittaa
  oikein rajattomien kokonaislukujen ansiosta; C:llä tai C++:lla saman
  mallin voi ajaa miljoonilla näytteillä ja upottaa SystemC-malliin.

## Itsearviointi

- Osaat kirjoittaa saman kiinteän pilkun algoritmin C:llä ja Pythonilla
  niin, että tulokset ovat bitilleen samat.
- Osaat verrata bittitarkkaa mallia double-referenssiin ja selittää
  eron lähteet.
- Osaat toteuttaa CORDICin siirroilla ja yhteenlaskuilla ja valita
  iteraatioiden määrän tarkkuusvaatimuksesta.
- Osaat kertoa, miten bittitarkkaa mallia käytetään RTL:n testauksessa.
- Osaat lukea kavennuksen SystemVerilog-toteutuksen ja kertoa, mikä osa
  siitä on johdotusta ja mikä logiikkaa.
