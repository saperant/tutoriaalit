# Lyhytaikainen spektri

DFT kertoo, mitä taajuuksia koko mittauksessa on, mutta ei sitä, milloin
ne esiintyvät. Puheessa, musiikissa, koneen kiihdytyksessä ja
tutkapulssissa juuri ajallinen muutos on kiinnostavaa. **Lyhytaikainen
Fourier-muunnos** (STFT) liu'uttaa ikkunaa signaalin yli ja laskee
DFT:n jokaisesta ikkunan kohdasta. Tuloksena on kaksiulotteinen taulukko,
jonka toinen akseli on aika ja toinen taajuus. Sen itseisarvo kuvana on
**spektrogrammi**.

## STFT SciPyllä

SciPyn luokka `ShortTimeFFT` kokoaa STFT:n parametrit yhteen:
ikkunafunktio, hyppy (*hop*) eli montako näytettä ikkuna siirtyy
kerralla, näytetaajuus ja skaalaus. Metodit `t` ja `f` antavat
akselien arvot, joten indeksejä ei tarvitse muuntaa käsin. Esimerkissä
taajuus nousee kahdessa sekunnissa tasaisesti 200 hertsistä 2 000
hertsiin, ja STFT:stä luetaan hetkellinen taajuus.

```{.python tiedosto="esimerkit/10-stft.py" osa="stft"}
```

256 näytteen ikkuna 8 kHz:n näytetaajuudella antaa 31,25 Hz:n
taajuusvälit, ja huiput osuvat lähimpään väliin. Hetkellinen taajuus
muuttuu ikkunan aikana noin 29 Hz, joten tarkempaa arviota tästä
ikkunasta ei saa.

![Taajuuspyyhkäisyn spektrogrammi. Hetkellä 1 s alkaa 3 kHz:n
sävel.](kuvat/spektrogrammi.png){width=100%}

## Aika–taajuus-kompromissi

Taidossa *Kompleksiluvut ja Fourier-analyysi* todettiin, että kapea
pulssi on taajuudessa leveä ja päinvastoin. STFT:ssä sama
epätarkkuusperiaate on suunnitteluvalinta. Lyhyt ikkuna paikantaa
tapahtumat ajassa tarkasti, mutta sen taajuusresoluutio on huono. Pitkä
ikkuna erottaa taajuudet, mutta sotkee nopeat muutokset. Mitataan
molemmat: napsahduksen leveys ajassa ja jatkuvan sävelen leveys
taajuudessa kolmella ikkunan pituudella.

```{.python tiedosto="esimerkit/10-stft.py" osa="kompromissi"}
```

```{.tuloste tiedosto="esimerkit/10-stft.odotettu"}
```

Leveyksien tulo pysyy suunnilleen vakiona: kun toinen kapenee, toinen
levenee. Ikkunan pituus valitaan sen mukaan, mitä halutaan nähdä.
Puheanalyysissä käytetään tyypillisesti 20–30 ms:n ikkunoita, jotka
seuraavat äänteiden vaihtumista. Moottorin harmonisten seurantaan
käytetään pitkiä ikkunoita, jotta lähekkäiset kertaluvut erottuvat.

## Hyppy ja käänteismuunnos

Hyppy määrää, kuinka tiheästi aika-akselia näytteistetään. Se ei
paranna aikaresoluutiota, joka määräytyy ikkunan pituudesta, mutta se
tekee spektrogrammista tasaisemman. Tavallinen valinta on neljäsosa tai
puolikas ikkunan pituudesta. Kun ikkuna ja hyppy täyttävät
*COLA*-ehdon (ikkunoiden summa on vakio), STFT on kääntyvä: signaalin
voi muokata taajuustasossa ja koota takaisin. `ShortTimeFFT.istft`
tekee käänteismuunnoksen. Tällä periaatteella toimivat esimerkiksi
kohinanvaimennus ja äänen aikavenytys, joiden suunnittelu kuuluu taitoon
*Digitaalinen signaalinkäsittely*.

## Käytännössä

- **Valitse ikkunan pituus ilmiön aikaskaalan mukaan.** Lyhyt ikkuna
  transienteille, pitkä kapeille taajuuksille. Kokeile useampaa
  pituutta, ennen kuin teet johtopäätöksiä.
- **Käytä `ShortTimeFFT`-luokan akseleita** (`t`, `f`, `extent`), äläkä
  laske kehysten aikoja käsin; ikkunan keskikohdan ja reunan sekoittaminen
  on tavallinen virhe.
- **Näytä spektrogrammi desibeleinä** ja rajaa dynamiikka (esim.
  60 dB), muuten heikot komponentit katoavat.
- **Muista ikkunan reunat.** Signaalin alussa ja lopussa ikkuna on
  osin signaalin ulkopuolella, ja niissä kehyksissä on reunailmiöitä.

## Itsearviointi

- Osaat laskea STFT:n `ShortTimeFFT`-luokalla ja lukea siitä
  hetkellisen taajuuden.
- Osaat selittää ikkunan pituuden vaikutuksen aika- ja
  taajuusresoluutioon ja valita pituuden tehtävän mukaan.
- Osaat kertoa hypyn merkityksen ja sen, milloin STFT on kääntyvä.
