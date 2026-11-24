# Kvantisointivirhe ja SQNR

Pyöristysvirhe on deterministinen, mutta kun signaali on monimutkainen,
virhe käyttäytyy kuin satunnainen kohina. Tämä *additiivisen kohinan
malli* on kiinteän pilkun suunnittelun tärkein työkalu: sillä lasketaan
etukäteen, kuinka paljon kohinaa kukin pyöristys tuottaa ja kuinka monta
bittiä tarvitaan.

## Kohinamalli

Pyöristys lähimpään tuottaa virheen, joka on tasajakautunut välillä
$[-q/2, q/2]$, kun $q$ on LSB:n paino. Tasajakauman varianssi on

$$\sigma_e^2 = \frac{q^2}{12}.$$

Täyden skaalan siniaallon teho on $A^2/2$, ja Q1.(b−1)-muodossa
$A \approx 1$ ja $q = 2^{1-b}$. Signaalin ja kvantisointikohinan suhde
(*signal-to-quantization-noise ratio*) on silloin

$$\text{SQNR} = 10 \log_{10} \frac{1/2}{2^{2-2b}/12} \approx 6{,}02\,b + 1{,}76 \text{ dB}.$$

Jokainen bitti lisää noin 6 dB. Sääntö tarkistetaan mittaamalla:

```{.python tiedosto="esimerkit/06-sqnr.py" osa="kvantisointi"}
```

```{.python tiedosto="esimerkit/06-sqnr.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/06-sqnr.odotettu"}
```

Kymmenestä bitistä ylöspäin mitattu ja laskettu ovat sadasosien päässä
toisistaan. Hyvin pienillä bittimäärillä malli pettää: virhe ei ole enää
tasajakautunut eikä riippumaton signaalista, vaan se on signaalin
jaksollinen funktio. Neljällä bitillä kvantisoitu sini ei kuulosta
kohinaiselta vaan säröytyneeltä, koska virhe keskittyy harmonisille
taajuuksille. Siksi pienillä bittimäärillä käytetään *ditheriä*: ennen
kvantisointia lisätään pieni satunnainen signaali, joka tekee virheestä
riippumattoman ja muuttaa särön kohinaksi.

## Tarkkuus on absoluuttinen

Kaava pätee vain täyden skaalan signaalille. Kiinteän pilkun LSB on
sama kaikille arvoille, joten hiljainen signaali saa saman kohinan
mutta vähemmän tehoa:

```{.python tiedosto="esimerkit/06-sqnr.py" osa="hiljainen"}
```

40 dB hiljaisempi signaali menettää 40 dB SQNR:stä, eli 16 bitistä jää
käyttöön alle 10. Tämä on kiinteän pilkun suurin heikkous liukulukuun
verrattuna, ja se tekee *skaalauksesta* suunnittelun keskeisen tehtävän:
signaali pidetään mahdollisimman lähellä täyttä skaalaa koko datapolun
läpi.

## Kertoimien kvantisointi

Suodattimen kertoimet kvantisoidaan kerran suunnitteluvaiheessa, eikä
niiden virhe ole kohinaa vaan pysyvä muutos taajuusvasteeseen.
Herkimmin muuttuu estokaistan vaimennus, koska se syntyy monen pienen
kertoimen tarkasta kumoutumisesta:

```{.python tiedosto="esimerkit/06-kertoimet.py" osa="suunnittelu"}
```

```{.python tiedosto="esimerkit/06-kertoimet.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/06-kertoimet.odotettu"}
```

Ikkunoidun suodattimen −52 dB:n vaimennus säilyy 12 kerroinbitillä.
Sen alapuolella vaimennus heikkenee noin 6 dB bittiä kohti, koska
kertoimien virheet muodostavat oman ”kohinasuodattimensa”, jonka vaste
summautuu ideaaliseen. Peukalosääntö: kerroinbittejä tarvitaan vähintään
$\text{vaimennus}/6$ ja muutama varalle.

IIR-suodattimet ovat paljon herkempiä. Kertoimien pieni virhe siirtää
napoja, ja yksikköympyrän lähellä oleva napa voi siirtyä sen
ulkopuolelle, jolloin suodatin muuttuu epästabiiliksi. Siksi
korkea-asteiset IIR-suodattimet toteutetaan toisen asteen lohkojen
(*biquad*) ketjuna eikä yhtenä korkean asteen polynomina.

## Käytännössä

- **Laske bitit SQNR-vaatimuksesta.** Tarvittava bittimäärä on noin
  $(\text{SQNR} - 1{,}76)/6{,}02$, kun signaali on täyttä skaalaa. Lisää
  bitit, jotka menetetään signaalin keskimääräisen tason ja täyden
  skaalan erona (*headroom*).
- **Pidä signaalit lähellä täyttä skaalaa.** Vahvistukset ja
  skaalaukset sijoitetaan niin, ettei signaali hiljene matkalla
  tarpeettomasti. Jokainen 6 dB:n hukka maksaa bitin.
- **Kvantisoi kertoimet ja mittaa vaste.** Kertoimien bittimäärä
  valitaan tarkistamalla kvantisoitujen kertoimien taajuusvaste, ei
  pelkällä kaavalla.
- **Käytä ditheriä matalilla bittimäärillä.** Kun SQNR on alle noin
  40 dB, virhe on säröä eikä kohinaa.

## Itsearviointi

- Osaat johtaa kvantisointikohinan varianssin $q^2/12$ ja SQNR:n
  kaavan $6{,}02\,b + 1{,}76$ dB.
- Osaat mitata SQNR:n ja selittää, miksi malli pettää pienillä
  bittimäärillä.
- Osaat selittää, miksi kiinteän pilkun tarkkuus on absoluuttinen ja
  mitä se tarkoittaa skaalauksen kannalta.
- Osaat arvioida, montako bittiä FIR-suodattimen kertoimet tarvitsevat
  vaaditulle estokaistan vaimennukselle.
