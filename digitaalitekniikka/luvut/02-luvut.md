# Luvut bitteinä

Digitaalinen piiri käsittelee vain bittejä. Luku on sopimus siitä,
miten bittijono tulkitaan. Hyvä sopimus tekee laitteistosta
yksinkertaisen: kahden komplementti on valittu, koska sillä sama
summain laskee sekä etumerkittömiä että etumerkillisiä lukuja.

Ohjelmoijan näkökulma (ylivuoto C:ssä, tarkistettu aritmetiikka,
bittioperaatiot) on taidossa *Miten tietokone laskee*. Tässä luvussa
katsotaan, mitä esitykset merkitsevät laitteistolle.

## Paikkajärjestelmät

$n$-bittisen binääriluvun $b_{n-1} \ldots b_1 b_0$ arvo on
$\sum_i b_i 2^i$. Heksadesimaaliluku on binääriluku neljän bitin
ryhminä: `0xB2` on `1011 0010`. Laitteistossa heksa on vain
kirjoitustapa, ei eri esitys.

```{.python tiedosto="esimerkit/02-luvut.py" osa="bitit"}
```

## Kahden komplementti

Kahden komplementissa eniten merkitsevän bitin (MSB) paino on
negatiivinen: $-2^{n-1}$. Neljällä bitillä arvot ovat −8…7.

```{.python tiedosto="esimerkit/02-luvut.py" osa="taulukko"}
```

Etumerkittömänä ja kahden komplementtina samat bitit tarkoittavat eri
lukuja, mutta niiden ero on aina $2^n$. Siksi yhteenlasku modulo $2^n$
antaa oikeat bitit molemmille tulkinnoille. Laitteisto ei tiedä, kumpaa
tulkintaa käytetään: summain on sama, vain liput tulkitaan eri tavalla
(luku 6).

Vastaluku saadaan kääntämällä bitit ja lisäämällä yksi:

```{.python tiedosto="esimerkit/02-luvut.py" osa="vastaluku"}
```

Laitteistossa tämä on halpaa. Kääntäminen on rivi invertterejä, ja
"+1" saadaan summaimen tulomuistibitistä ilmaiseksi. Siksi vähennyslasku
$a - b = a + \bar{b} + 1$ ei tarvitse omaa piiriä.

Etumerkin laajennus kopioi MSB:n uusiin bitteihin. Laitteistossa se on
pelkkää johdotusta: yksi johdin haarautuu usean bitin tuloksi.

```{.python tiedosto="esimerkit/02-luvut.py" osa="laajennus"}
```

```{.tuloste tiedosto="esimerkit/02-luvut.odotettu"}
```

Tulosteen kolmas rivi −(−8) näyttää kahden komplementin epäsymmetrian:
vähimmäisarvon vastaluku on se itse, koska +8 ei mahdu neljään bittiin.
Laitteisto tuottaa siitä ylivuotolipun (luku 6).

## Gray-koodi ja BCD

**Gray-koodissa** peräkkäiset arvot eroavat täsmälleen yhdessä
bitissä:

```{.python tiedosto="esimerkit/02-luvut.py" osa="gray"}
```

Tavallisessa binääriluvussa siirtymä 011 → 100 muuttaa kolmea bittiä.
Jos bittejä luetaan juuri muutoksen aikana, lukija voi nähdä minkä
tahansa välitilan, esimerkiksi 111 tai 000. Gray-koodissa välitilaa ei
ole: luettu arvo on joko vanha tai uusi. Siksi Gray-koodia käytetään
kiertoasentoanturien koodilevyissä ja asynkronisen FIFO-puskurin
osoittimissa, jotka luetaan toisen kellon tahdissa (taito
*RTL-suunnittelu SystemVerilogilla*, kellotusalueiden ylitys). Karnaugh-kartta (luku 4) käyttää samaa
järjestystä.

**BCD** (binary-coded decimal) koodaa jokaisen kymmenjärjestelmän
numeron omana neljän bitin ryhmänään. Se tuhlaa tilaa (16 bittiä
luvulle 1984, binäärinä riittää 11), mutta numeroiden näyttäminen ja
desimaalipyöristys ovat suoria. Sitä käytetään näyttöjen ohjauksessa,
reaaliaikakelloissa ja rahalaskennassa.

## Käytännössä

- **Leveys on osa tyyppiä.** Laitteistossa jokainen signaali on
  kiinteän levyinen. Kun suunnittelet laskentaa, laske lukualue ja
  valitse leveys sen mukaan. Ylimääräinen bitti maksaa pinta-alaa,
  puuttuva bitti tuottaa väärän vastauksen hiljaa.
- **Kahden komplementti oletuksena.** Etumerkillisille arvoille ei
  käytetä etumerkki–suuruus-esitystä, koska se vaatisi oman
  vähennyspiirinsä ja kaksi nollaa.
- **Gray-koodi aina, kun monibittistä laskuria luetaan asynkronisesti.**
  Tavallisen laskurin lukeminen toisen kellon tahdissa voi antaa
  arvon, jota laskuri ei koskaan ollut.
- **Heksa kirjoitusasuna.** Laitteistodokumentit, rekisterikartat ja
  simulaatiotulosteet käyttävät heksaa, koska neljä bittiä vastaa yhtä
  numeroa. Etumerkkiä ei näe heksasta: `0xF` on 15 tai −1 tulkinnan
  mukaan.

## Itsearviointi

- Osaat muuntaa luvun binääriksi, heksaksi ja kahden komplementiksi ja
  takaisin.
- Osaat selittää, miksi sama summain laskee etumerkittömiä ja
  etumerkillisiä lukuja ja miten vähennys tehdään summaimella.
- Osaat laajentaa etumerkillisen luvun leveämmäksi ja kertoa, mikä
  vähimmäisarvon vastaluvussa on erikoista.
- Osaat kertoa, miksi Gray-koodia käytetään luettaessa arvoa toisen
  kellon tahdissa.
