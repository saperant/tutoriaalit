# Q-formaatit

Kiinteän pilkun muodon kuvaamiseen on monta merkintätapaa. Tässä
tutoriaalissa käytetään yleistä Q-merkintää: **Qm.n** on etumerkillinen
luku, jossa on $m$ kokonaisbittiä (etumerkkibitti mukaan lukien) ja $n$
murtobittiä, yhteensä $m + n$ bittiä. Etumerkitön muoto merkitään
**UQm.n**. Koodin $k$ arvo on $k \cdot 2^{-n}$.

Merkintä ei ole yhtenäinen. ARM:n ja TI:n dokumenteissa Q15 tarkoittaa
samaa kuin tässä Q1.15 (etumerkkibittiä ei lasketa), ja MATLABin
`fixdt(1, 16, 15)` kertoo etumerkin, kokonaisleveyden ja murtobitit.
Lue merkintä aina dokumentin omista määritelmistä ja kirjaa oma
käytäntö suunnitteluun.

## Arvoalue ja tarkkuus

Etumerkillisen Qm.n-luvun arvoalue on $[-2^{m-1}, 2^{m-1} - 2^{-n}]$ ja
tarkkuus eli LSB:n paino $2^{-n}$. Bittejä voi siirtää kokonaisosasta
murto-osaan: sama 16-bittinen sana on Q1.15, Q4.12 tai Q8.8 sen mukaan,
mitä suunnittelija tarvitsee.

```{.python tiedosto="esimerkit/02-formaatit.py" osa="formaatti"}
```

```{.python tiedosto="esimerkit/02-formaatit.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/02-formaatit.odotettu"}
```

Arvoalue ja tarkkuus ovat toistensa vastakohdat: jokainen kokonaisosaan
lisätty bitti kaksinkertaistaa alueen ja puolittaa tarkkuuden.
Etumerkillisen muodon alue on epäsymmetrinen, koska nollaa vastaa
positiivinen koodi: pienin arvo on täsmälleen $-2^{m-1}$, suurin yhden
LSB:n verran vajaa $2^{m-1}$. Q1.15:n −1 mahtuu, +1 ei.

Tyypillisiä käyttökohteita:

| Muoto | Käyttö |
|-------|--------|
| Q1.15, Q1.31 | normalisoidut signaalit, suodattimen kertoimet |
| Q2.30 | Q1.15-tulot ennen pyöristystä |
| Q8.8, Q16.16 | pelien ja grafiikan koordinaatit, lämpötilat |
| UQ0.16, UQ0.8 | todennäköisyydet, värikanavat, ikkunafunktiot |
| UQ12.4 | anturilukemat, joissa on muutama murtobitti |

## Muunnos liukuluvusta ja takaisin

Liukuluvusta Qm.n-koodiksi päästään kertomalla luvulla $2^n$, pyöristämällä
ja leikkaamalla alueelle. Takaisin liukuluvuksi jaetaan luvulla $2^n$.
Funktio `ldexp` kertoo kahden potenssilla tarkasti ja nopeasti, koska se
muuttaa vain eksponenttia:

```{.c tiedosto="esimerkit/02-muunnos.c" osa="muunnos"}
```

```{.c tiedosto="esimerkit/02-muunnos.c" osa="esimerkit"}
```

```{.tuloste tiedosto="esimerkit/02-muunnos.odotettu"}
```

Q4.12 esittää π:n neljän desimaalin tarkkuudella, Q8.8 kahden.
Q1.15:een π ei mahdu ollenkaan, ja ilman saturaatiota muunnos olisi
antanut täysin väärän arvon. Muunnos tehdään testipenkeissä ja
malleissa, ei laitteistossa; laitteistossa data on alusta asti
kiinteän pilkun koodeina.

## Muodon vaihto ja pilkun kohdistus

Kun murtobittien määrä muuttuu, koodia siirretään: $k$ murtobittiä lisää
on siirto $k$ bittiä vasemmalle (kertolasku luvulla $2^k$), $k$ bittiä
vähemmän on siirto oikealle (jakolasku ja pyöristys). Laitteistossa
siirto vakiomäärällä on pelkkää johdotusta, eikä se maksa mitään.

```{.c tiedosto="esimerkit/02-muunnos.c" osa="vaihto"}
```

Muodon vaihto ei muuta arvoa, mutta tulos voi vaatia lisää bittejä:
2,5 ei mahdu Q1.15:een. Kun kaksi eri muotoista lukua lasketaan yhteen,
pilkut on ensin kohdistettava samaan kohtaan, aivan kuin desimaaliluvut
allekkain laskettaessa. Kohdistus tehdään siirtämällä se luku, jolla on
vähemmän murtobittejä, ja leventämällä tulosta.

## Käytännössä

- **Kirjaa muoto jokaiselle signaalille.** Lohkokaavioon tai
  rajapintakuvaukseen merkitään jokaisen väylän Qm.n-muoto. Muoto ei
  näy RTL-koodissa eikä C-tyypeissä (`int16_t` voi olla Q1.15 tai Q8.8),
  joten se on dokumentoitava erikseen tai koodattava nimiin
  (`naytteet_q15`).
- **Valitse alue ensin, tarkkuus sitten.** Kokonaisbittien määrä
  seuraa signaalin suurimmasta mahdollisesta arvosta, ja jäljelle jäävät
  bitit ovat murtobittejä. Väärin arvioitu alue johtaa ylivuotoon, joka
  on paljon pahempi virhe kuin kvantisointikohina.
- **Normalisoi signaalit välille $[-1, 1)$.** Q1.n-muodoissa tulo
  pysyy samalla välillä (paitsi $(-1)^2$), joten kertolaskun jälkeinen
  skaalaus on aina sama siirto.
- **Siirto on ilmainen, kertolasku ei.** Skaalauskertoimet kannattaa
  valita kahden potenssin mukaan aina kun mahdollista, koska silloin ne
  ovat pelkkää johdotusta.

## Itsearviointi

- Osaat laskea Qm.n- ja UQm.n-muodon arvoalueen ja tarkkuuden.
- Osaat muuntaa liukuluvun kiinteän pilkun koodiksi pyöristäen ja
  saturoiden sekä takaisin.
- Osaat vaihtaa muotoa siirroilla ja kertoa, milloin tulos vaatii
  lisää kokonaisbittejä.
- Osaat kohdistaa kahden eri muotoisen luvun binääripilkut ennen
  yhteenlaskua.
