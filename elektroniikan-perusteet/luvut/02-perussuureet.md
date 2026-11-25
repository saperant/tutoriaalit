# Jännite, virta, resistanssi ja teho

Neljä suuretta kuvaa lähes kaiken tasavirtapiirien käyttäytymisestä.
Ne kannattaa ymmärtää fyysisinä asioina eikä vain kaavojen
kirjaimina.

## Suureet ja yksiköt

**Jännite** $U$ (voltti, V) on potentiaaliero kahden pisteen välillä:
kuinka paljon energiaa yksi coulombi varausta saa tai luovuttaa
siirtyessään pisteestä toiseen. Jännite mitataan aina *kahden* pisteen
välillä. Kun puhutaan "solmun jännitteestä", toinen piste on
sovittu vertailupiste, maa.

**Virta** $I$ (ampeeri, A) on varauksen kulku: kuinka monta coulombia
kulkee johtimen poikkileikkauksen läpi sekunnissa. Virta kulkee aina
suljetussa silmukassa. Se, mikä lähtee lähteen plusnavasta, palaa
miinusnapaan.

**Resistanssi** $R$ (ohmi, Ω) on komponentin vastus virralle. Ohmin laki
kertoo, että resistiivisessä komponentissa jännite ja virta ovat
suoraan verrannollisia:

$$
U = R I .
$$

**Teho** $P$ (watti, W) on energian muuttumisnopeus. Komponentissa
kuluva teho on jännite kertaa virta, ja vastuksessa se voidaan
kirjoittaa Ohmin lain avulla kolmella tavalla:

$$
P = U I = I^2 R = \frac{U^2}{R} .
$$

Vastuksessa teho muuttuu lämmöksi. Tämä on syy useimpiin
komponenttien vikoihin: vastus, transistori tai jännitesäädin kestää
vain rajallisen lämpötilan. Luvussa 7 lasketaan häviötehosta
komponentin lämpötila.

| Suure | Tunnus | Yksikkö | Tyypillinen alue elektroniikassa |
|-------|--------|---------|----------------------------------|
| jännite | $U$ | V | 0,1...24 V (logiikka 1,8...5 V) |
| virta | $I$ | A | 1 µA...2 A |
| resistanssi | $R$ | Ω | 1 Ω...10 MΩ |
| teho | $P$ | W | 1 mW...10 W |

## Esimerkki: etuvastuksen teho

Etuvastus rajoittaa virtaa, kun 5 V:n syötöstä syötetään kuormaa,
jonka yli jää 2 V. Vastuksen yli jää loput 3 V, ja virta ja teho
saadaan suoraan:

```{.python tiedosto="esimerkit/02-teho.py" osa="kasin"}
```

SPICE laskee saman. Kuorma on mallinnettu toisena jännitelähteenä,
ja `@r1[i]` ja `@r1[p]` ovat vastuksen sisäisiä suureita: virta ja
teho. Laitteiden sisäiset suureet kirjoitetaan ngspicessä muotoon
`@nimi[suure]`.

```{.spice tiedosto="esimerkit/02-teho.cir"}
```

Vastus valitaan niin, että sen tehonkesto on reilusti häviötä
suurempi. Tavallinen nyrkkisääntö on kaksinkertainen marginaali,
koska vastuksen tehonkesto ilmoitetaan yleensä 70 °C:n ympäristössä,
ja kuuma vastus vanhenee ja muuttaa arvoaan:

```{.python tiedosto="esimerkit/02-teho.py" osa="kesto"}
```

```{.tuloste tiedosto="esimerkit/02-teho.odotettu"}
```

Tavallinen pintaliitosvastus (koko 0603) kestää noin 0,1 W ja 0805
noin 0,125 W, joten 191 mW:n häviö tarvitsee suuremman kotelon tai
kaksi vastusta rinnan.

## Komponenttien arvot: E-sarjat

Vastuksia ei valmisteta kaikilla arvoilla. Standardi IEC 60063
määrittelee *E-sarjat*, joissa arvot jakautuvat tasaisesti
logaritmiselle asteikolle: E12-sarjassa on 12 arvoa dekadia kohti,
E24:ssä 24 ja niin edelleen. Peräkkäisten arvojen suhde on
E12-sarjassa noin $10^{1/12} = 1{,}21$, joten 10 %:n toleranssin
vastukset peittävät koko asteikon ilman aukkoja.

![E12-sarjan arvot logaritmisella asteikolla. Varjostus on ±10 %:n
toleranssikaista: vierekkäiset kaistat koskettavat toisiaan, joten
jokainen resistanssi osuu jonkin nimellisarvon
kaistalle.](kuvat/esarja.png){width=88%}

Lähin standardiarvo valitaan logaritmisesti, koska suhteellinen ero
on se, millä on merkitystä:

```{.python tiedosto="esimerkit/02-esarja.py" osa="sarjat"}
```

## Toleranssit ja huonoin tapaus

Vastuksen todellinen arvo poikkeaa nimellisestä enintään toleranssin
verran: 5 %:n 10 kΩ:n vastus on jotain 9,5 kΩ:n ja 10,5 kΩ:n
väliltä. Piirin tulos vaihtelee samalla tavalla, ja suunnittelijan on
tiedettävä, kuinka paljon. Yksinkertaisin menetelmä on *huonoimman
tapauksen analyysi*: kokeillaan kaikki ääripäiden yhdistelmät.

```{.python tiedosto="esimerkit/02-esarja.py" osa="huonoin"}
```

```{.tuloste tiedosto="esimerkit/02-esarja.odotettu"}
```

Jakajan lähtö voi siis olla ±7 % nimellisestä, vaikka kumpikin vastus
on vain ±5 %. Huonoin tapaus on varma mutta pessimistinen: on
epätodennäköistä, että kaikki osat ovat samaan aikaan ääripäässä.
Luvussa 8 sama jakaja analysoidaan Monte Carlo -menetelmällä, joka
kertoo tuloksen todennäköisen jakauman.

## Mittaaminen kuormittaa piiriä

Yleismittari mittaa jännitettä ottamalla piiristä hieman virtaa.
Tavallisen digitaalisen mittarin sisäresistanssi on noin 10 MΩ, mikä
on merkityksetön useimmissa piireissä mutta ei suuri-impedanssisissa.
Kun 1 MΩ:n vastusten jakajaa mitataan, mittari on rinnan alemman
vastuksen kanssa ja muuttaa sitä, mitä se mittaa:

```{.spice tiedosto="esimerkit/02-mittari.cir"}
```

```{.python tiedosto="esimerkit/02-mittari.py" osa="kasin"}
```

```{.tuloste tiedosto="esimerkit/02-mittari.odotettu"}
```

Rinnankytkennän kokonaisresistanssi on aina pienempi kuin pienempi
vastuksista:

$$
R_\text{rinnan} = \frac{R_2 R_m}{R_2 + R_m} .
$$

Sama ilmiö koskee oskilloskoopin mittapäätä, mikrokontrollerin
AD-muunninta ja jokaista piiriä, joka lukee toisen piirin lähtöä.
Siksi lähtöimpedanssin ja tuloimpedanssin suhde on yksi
elektroniikan peruskysymyksistä: mittaus on luotettava, kun mittarin
tuloimpedanssi on vähintään satakertainen mitattavan piirin
lähtöimpedanssiin nähden.

## Käytännössä

- Laske teho jokaiselle vastukselle, joka kantaa yli muutaman
  milliampeerin virtaa, ja valitse tehonkesto kaksinkertaisella
  marginaalilla. Kuuma komponentti on ensimmäinen vikaehdokas.
- Valitse arvot E-sarjasta jo suunnitteluvaiheessa. E24-sarja ja
  1 %:n toleranssi ovat nykyään yhtä halpoja kuin E12 ja 5 %, ja ne
  ovat hyvä oletus.
- Kun tuloksen tarkkuus on tärkeä (esimerkiksi AD-muuntimen
  vertailujännite), tee toleranssianalyysi. Jakajan tarkkuus riippuu
  vastusten toleranssista ja lämpötilakertoimesta, ei vain
  nimellisarvoista.
- Muista mittauksen kuormitus. Jos mittaus muuttaa tulosta, piirin
  lähtöimpedanssi on liian suuri mittalaitteelle, ja ratkaisu on
  puskuri (operaatiovahvistin, jatkotaito *Analogiaelektroniikka*).
- SPICE ei erota isoja ja pieniä kirjaimia: `1M` on yksi milliohmi
  (tai millivoltti), megaohmi on `1Meg`.

## Itsearviointi

- Osaat laskea vastuksen virran, jännitteen ja tehon Ohmin lailla ja
  tehon kaavoilla.
- Osaat valita E-sarjan arvon ja vastuksen tehonkeston perustellusti.
- Osaat arvioida toleranssien vaikutuksen huonoimman tapauksen
  analyysillä.
- Osaat selittää, miksi mittari kuormittaa piiriä, ja arvioida
  mittausvirheen sisäresistanssin perusteella.
- Osaat kirjoittaa yksinkertaisen netlistin ja lukea vastuksen virran ja
  tehon ngspicestä.
