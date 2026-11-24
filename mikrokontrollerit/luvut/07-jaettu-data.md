# Keskeytysten ja pääohjelman yhteinen data

Bare-metal-ohjelmassa ei ole säikeitä, mutta rinnakkaisuutta on silti:
keskeytys voi alkaa minkä tahansa kahden käskyn välissä, ja jos
käsittelijä ja pääohjelma käyttävät samaa dataa, syntyy samat
kilpailutilanteet kuin monisäikeisessä ohjelmassa. Ero on siinä, että
tilanne on epäsymmetrinen. Käsittelijä ajetaan aina loppuun asti
ilman pääohjelman väliintuloa, mutta pääohjelma voi keskeytyä
milloin tahansa. Siksi suojaus tarvitaan yleensä vain pääohjelman
puolelle.

Virheet ovat harvinaisia ja ajoituksesta riippuvia: keskeytyksen on
osuttava täsmälleen muutaman käskyn mittaiseen ikkunaan. Laite voi
toimia viikkoja testipenkissä ja kaatua kentällä. Tämän luvun
esimerkit laukaisevat keskeytyksen ohjelmallisesti pahimpaan
kohtaan, jotta jokainen virhe näkyy joka ajossa.

## Kadonnut päivitys

Lause `jaettu++` näyttää yhdeltä operaatiolta, mutta Cortex-M kääntää
sen kolmeksi käskyksi: luku rekisteriin, lisäys ja kirjoitus
muistiin. `volatile` takaa vain, että luku ja kirjoitus tapahtuvat,
ei sitä, että mitään ei tapahdu niiden välissä.

```{.c tiedosto="esimerkit/07-kilpailu/main.c" osa="menetetty"}
```

Käsittelijä lisää muuttujaan sata, mutta pääohjelma kirjoittaa
päälle arvon, jonka se luki ennen keskeytystä. Sama ongelma koskee
kaikkia luku–muutos–kirjoitus-operaatioita: lippujen asettamista
`|=`-operaatiolla, laskureita, rakenteiden useita kenttiä ja
oheislaiterekistereitä.

## Kriittinen osio

Yksinkertaisin suoja on estää keskeytykset operaation ajaksi. Oikea
tapa tallentaa PRIMASKin vanhan arvon ja palauttaa sen, jolloin
funktiota voi kutsua myös valmiiksi suojatusta kohdasta.

```{.c tiedosto="esimerkit/yhteinen/mps2.h" osa="sisaiset"}
```

```{.c tiedosto="esimerkit/07-kilpailu/main.c" osa="kriittinen"}
```

Keskeytys, joka tulee kriittisen osion aikana, ei katoa: se jää
odottamaan ja ajetaan heti, kun PRIMASK palautetaan. Kriittisen osion
pituus lisätään kuitenkin jokaisen keskeytyksen pahimpaan viiveeseen,
joten osion on oltava muutaman käskyn mittainen eikä se saa sisältää
odottamista.

Vaarallinen virhe on apufunktio, joka kieltää ja sallii keskeytykset
ehdoitta. Kun sitä kutsutaan kriittisen osion sisältä, se sallii
keskeytykset kesken kutsujan osion:

```{.c tiedosto="esimerkit/07-kilpailu/main.c" osa="sokea"}
```

## LDREX ja STREX

Cortex-M3 ja uudemmat tarjoavat lukottoman vaihtoehdon. LDREX lukee
arvon ja merkitsee osoitteen varatuksi; STREX kirjoittaa vain, jos
varaus on yhä voimassa, ja palauttaa nollan onnistuessaan. Poikkeuksen
alku ja loppu purkavat varauksen, joten jos keskeytys osuu väliin,
STREX epäonnistuu ja operaatio yritetään uudelleen. Keskeytyksiä ei
tarvitse kieltää, eikä viive kasva.

```{.c tiedosto="esimerkit/07-kilpailu/main.c" osa="ldrex"}
```

Käsin kirjoitettua assemblyä ei tarvita: C11:n `<stdatomic.h>` ja
GCC:n `__atomic`-funktiot kääntyvät Cortex-M3:lla juuri tähän
silmukkaan. Cortex-M0+:lla LDREX ja STREX puuttuvat, ja atomiset
operaatiot vaativat kriittisen osion.

## Repeävä luku

Cortex-M3 lukee muistia 32 bitin osissa. 64-bittinen muuttuja, kuten
mikrosekuntilaskuri, luetaan kahdella käskyllä, ja jos keskeytys
kasvattaa laskuria niiden välissä, ala- ja yläosa ovat eri hetkiltä:

```{.c tiedosto="esimerkit/07-kilpailu/main.c" osa="repeama"}
```

Suojaamaton luku saa alaosan ennen ylivuotoa ja yläosan sen jälkeen,
eli arvo hyppää yli neljä miljardia tikkiä eteenpäin. Toistava luku
lukee yläosan ennen ja jälkeen ja yrittää uudelleen, jos se muuttui.
Tapa toimii, koska alaosan pyörähdys on ainoa tilanne, jossa yläosa
muuttuu. Kriittinen osio olisi yhtä hyvä ratkaisu.

```{.c tiedosto="esimerkit/07-kilpailu/main.c" osa="main"}
```

```{.c tiedosto="esimerkit/07-kilpailu/main.c" osa="main64"}
```

```{.tuloste tiedosto="esimerkit/testit/07-kilpailu.odotettu"}
```

## Rengaspuskuri

Yleisin jaetun datan rakenne on jono keskeytyksestä pääohjelmaan.
Käsittelijä *tuottaa* (vastaanotettu tavu, mittaus, tapahtuma) ja
pääohjelma *kuluttaa*. Kun tuottajia ja kuluttajia on kumpaakin
täsmälleen yksi, rengaspuskuri ei tarvitse lukkoja: tuottaja muuttaa
vain kirjoitusindeksiä ja kuluttaja vain lukuindeksiä.

```{.c tiedosto="esimerkit/yhteinen/rengas.h" osa="rengas"}
```

Rakenteessa on kolme yksityiskohtaa, jotka tekevät siitä oikean:

1. **Indeksit kasvavat vapaasti** eivätkä käänny ympäri puskurin
   koossa. Täyttöaste on aina `kirjoitus - luku`, eikä täyden ja tyhjän
   erottamiseen tarvita ylimääräistä paikkaa. Koon on oltava kahden
   potenssi, jotta 2^32^ on jaollinen koolla ja `%` on pelkkä maski.
2. **Data kirjoitetaan ennen indeksiä.** Jos kääntäjä vaihtaisi
   järjestyksen, kuluttaja voisi nähdä uuden indeksin ja lukea vanhan
   tavun. `atomic_signal_fence` on C11:n kääntäjäeste juuri tähän
   tilanteeseen: saman suorittimen keskeytys tai signaali. Moniytimisessä
   piirissä tai DMA:n kanssa tarvitaan lisäksi laitteiston este `dmb`.
3. **Ylivuoto lasketaan.** Jos kuluttaja ei ehdi, uusi tavu hylätään ja
   laskuri kertoo sen. Hiljaa kadonnut data on pahempi kuin laskettu.

UART:n vastaanottokeskeytys siirtää tavut renkaaseen. Käsittelijä
kuittaa keskeytyksen ennen kuin tyhjentää vastaanottimen. Järjestys on
tärkeä: jos kuittaus tehtäisiin silmukan jälkeen, silmukan viimeisen
tarkistuksen ja kuittauksen väliin osunut tavu jäisi vastaanottimeen
ilman keskeytystä, eikä uusia tavuja enää tulisi. Esimerkki jäi
kehitysvaiheessa jumiin juuri näin, kun testikone oli kuormitettu.

```{.c tiedosto="esimerkit/08-rengas/main.c" osa="isr"}
```

Pääohjelma odottaa tavua nukkuen. Tarkistus ja WFI tehdään
keskeytykset kiellettyinä, mikä selitetään tarkemmin luvussa 8.

```{.c tiedosto="esimerkit/08-rengas/main.c" osa="hae"}
```

```{.c tiedosto="esimerkit/08-rengas/main.c" osa="main"}
```

```{.c tiedosto="esimerkit/08-rengas/main.c" osa="komento"}
```

Syöte tulee tiedostosta `08-rengas/syote.txt`, jonka QEMU syöttää
UART0:n vastaanottimeen. Käsin ajettaessa (`make aja E=08-rengas`)
komennot kirjoitetaan päätteeseen.

```{.tuloste tiedosto="esimerkit/testit/08-rengas.odotettu"}
```

## Käytännössä

- **Luettele jokainen muuttuja, jota keskeytys ja pääohjelma
  jakavat**, ja päätä kullekin suojaustapa. Yksittäinen 32-bittinen
  lippu, jota vain luetaan tai kirjoitetaan, ei tarvitse muuta kuin
  `volatile`n.
- **Tallenna ja palauta PRIMASK** äläkä salli keskeytyksiä ehdoitta.
  CMSIS:n `__get_PRIMASK` ja `__set_PRIMASK` tai C11:n atomiset
  operaatiot.
- **Pidä kriittiset osiot lyhyinä**: kopioi data osion sisällä ja
  käsittele se osion jälkeen.
- **Käytä yhden tuottajan ja kuluttajan rengaspuskuria** keskeytyksestä
  pääohjelmaan, ja laske ylivuodot.
- **Testaa kilpailutilanteet laukaisemalla keskeytys pahimpaan
  kohtaan.** Satunnaista ajoitusta odottava testi ei löydä niitä.

## Itsearviointi

- Osaat selittää, miksi `volatile` ei riitä luku–muutos–kirjoitus-
  operaation suojaksi, ja näyttää kadonneen päivityksen.
- Osaat kirjoittaa kriittisen osion, joka toimii myös sisäkkäin.
- Osaat kuvata LDREX- ja STREX-käskyjen toiminnan ja sen, miksi
  keskeytys saa STREX:n epäonnistumaan.
- Osaat lukea 64-bittisen, keskeytyksen päivittämän laskurin oikein.
- Osaat toteuttaa yhden tuottajan ja yhden kuluttajan rengaspuskurin
  ja perustella, miksi se ei tarvitse lukkoa.
