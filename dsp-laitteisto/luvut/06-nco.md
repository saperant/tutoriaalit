# Numeerisesti ohjattu oskillaattori

Numeerisesti ohjattu oskillaattori (NCO, *numerically controlled
oscillator*) tuottaa siniaaltoa, jonka taajuus asetetaan luvulla.
Ohjelmistoradio sekoittaa sillä signaalin kantataajuudelle,
modulaattori tuottaa sillä kantoaallon ja mittalaite herätteen.
Rakenne on yksinkertainen: summain, joka laskee vaihetta, ja taulukko,
joka muuttaa vaiheen amplitudiksi. Kiinnostavaa on se, mitä
taulukon koko ja vaiheen katkaisu tekevät spektrille.

## Vaiheakkumulaattori

Vaihe on $P$-bittinen etumerkitön luku, jossa täysi kierros on $2^P$.
Joka näytteellä vaiheeseen lisätään *taajuussana* $M$, ja summa saa
kiertää yli:

$$\varphi[n+1] = (\varphi[n] + M) \bmod 2^P, \qquad
f = \frac{M}{2^P} f_s.$$

Esimerkissä $P = 24$, joten 100 MHz:n näytetaajuudella taajuuden
resoluutio on $100\ \mathrm{MHz} / 2^{24} \approx 6\ \mathrm{Hz}$.
Taajuuden muutos on vaihejatkuva: uusi taajuussana alkaa vaikuttaa
seuraavasta näytteestä, eikä vaihe hyppää. Tämä on NCO:n tärkein etu
analogiseen oskillaattoriin ja PLL:ään nähden.

## Vaiheesta amplitudiksi

Vaiheesta käytetään vain ylimmät bitit. Kaksi ylintä bittiä kertovat
neljänneksen, ja seuraavat $A$ bittiä osoittavat neljännesjakson
taulukkoon. Sinin symmetria säästää kolme neljännestä taulukosta:

| Neljännes | Osoite | Etumerkki |
|-----------|--------|-----------|
| 0 | $i$ | + |
| 1 | $2^A - 1 - i$ (bitit käännetty) | + |
| 2 | $i$ | − |
| 3 | $2^A - 1 - i$ | − |

Taulukon arvot lasketaan puolen askeleen siirrolla, $\sin(\frac{\pi}{2}
\cdot \frac{i + 1/2}{2^A})$. Silloin neljännes on täsmälleen
symmetrinen keskipisteensä suhteen, ja peilaus on pelkkä osoitteen
bittien kääntö. Ilman siirtoa taulukossa pitäisi olla sekä nolla että
huippu, ja peilauksessa tarvittaisiin vähennyslasku.

```{.python tiedosto="esimerkit/malli/kertoimet.py" osa="nco"}
```

Bittitarkka malli:

```{.python tiedosto="esimerkit/malli/cordic.py" osa="nco"}
```

RTL lukee taulukon tiedostosta, jonka `malli/generoi.py` tuottaa.
Synteesi tunnistaa `$readmemh`-alustetun muistin ja rekisteröidyn
lukemisen lohko-RAMiksi: 256 riviä × 11 bittiä mahtuu yhteen
iCE40:n 4 kilobitin SB_RAM40_4K-lohkoon.

```{.systemverilog tiedosto="esimerkit/rtl/nco.sv" osa="taulukko"}
```

Liukuhihnassa on neljä vaihetta: vaiheen katkaisu, osoitteen peilaus,
lohko-RAMin luku ja etumerkki. Lohko-RAMin luku on aina
rekisteröity, joten sen ympärille kannattaa rakentaa vaihe.
Vastapaine pysäyttää koko liukuhihnan ja myös vaiheakkumulaattorin,
joten jokainen vastaanotettu näyte on seuraava näyte, eikä yhtään
jää väliin:

```{.systemverilog tiedosto="esimerkit/rtl/nco.sv" osa="liukuhihna"}
```

## Vaiheen katkaisu ja kannuspiikit

Vaiheesta pudotetaan $P - A - 2$ alinta bittiä. Pudotettu osa on
vaihevirhe, joka on jaksollinen: se kasvaa sahalaitana ja palaa
nollaan aina, kun katkaistu osa kiertää yli. Jaksollinen virhe ei ole
kohinaa vaan erillisiä spektripiikkejä, *kannuspiikkejä* (*spurs*).
Niiden taso suhteessa kantoaaltoon on noin $6{,}02$ dB vaihebittiä
kohden. Mittaus mallilla, kun amplitudi on 16-bittinen ja vain
vaihebittien määrä muuttuu:

```{.python tiedosto="esimerkit/analyysit/nco_piikit.py" osa="sfdr"}
```

```{.tuloste tiedosto="esimerkit/odotetut/nco_piikit.odotettu"}
```

SFDR (*spurious-free dynamic range*) kasvaa noin 6 dB bittiä kohden,
kuten sääntö ennustaa. Toinen taulukko pitää vaihebitit 12:ssa ja
muuttaa amplitudin bittejä. Amplitudin kvantisointi rajoittaa
SFDR:ää kymmeneen bittiin asti; sen jälkeen raja on vaiheessa.
Kahden virheen ei kannata olla eri tasoilla: amplitudibitit, jotka
ylittävät vaihebittien tarkkuuden, ovat hukkaan heitettyjä.

Kannuspiikit riippuvat taajuussanasta. Jos sanan alimmat bitit ovat
nollia, katkaistu osa on aina nolla eikä vaihevirhettä synny. RTL-testi
mittaa molemmat tapaukset NCO:n omasta ulostulosta:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-nco.odotettu"}
```

Taajuudella $f_s/64$ ainoat piikit tulevat amplitudin
kvantisoinnista, ja SFDR on 81 dB. Taajuudella 0,04 $f_s$
taajuussanan alimmat bitit eivät ole nollia, ja SFDR putoaa 59
dB:iin, mikä vastaa analyysin tulosta kymmenellä vaihebitillä.

## Keinoja kannuspiikkejä vastaan

- **Isompi taulukko.** Jokainen osoitebitti tuplaa muistin ja tuo 6
  dB. Kalliiksi käy nopeasti.
- **Vaiheen dither.** Vaiheeseen lisätään ennen katkaisua pieni
  satunnaisluku (esimerkiksi LFSR:stä). Virhe ei ole enää jaksollinen,
  ja piikkien energia leviää kohinaksi. SFDR paranee jopa 12 dB:llä,
  mutta kohinataso nousee.
- **Interpolointi.** Taulukon arvojen väliin interpoloidaan
  lineaarisesti tai Taylorin sarjan ensimmäisellä termillä, jota
  varten tarvitaan kertoja ja kosinitaulukko.
- **CORDIC.** Luvun 5 rotaatiotila laskee sinin vaiheesta ilman
  taulukkoa. Tarkkuus kasvaa bitin kierrosta kohden, mutta latenssi ja
  logiikka ovat suuremmat kuin taulukolla.

## Käytännössä

- Valitse akkumulaattorin leveys taajuusresoluutiosta ja
  taulukon koko SFDR-vaatimuksesta (6 dB vaihebittiä kohden).
- Käytä neljännesjakson taulukkoa puolen askeleen siirrolla. Peilaus
  on silloin pelkkä bittien kääntö.
- Mitoita amplitudibitit samalle tasolle kuin vaihebitit; liian tarkka
  amplitudi ei paranna spektriä.
- Rakenna liukuhihna lohko-RAMin rekisteröidyn luvun ympärille ja
  pysäytä akkumulaattori vastapaineessa.
- Testaa sekä taajuussanalla, jonka alimmat bitit ovat nollia, että
  sanalla, jonka eivät ole: vain jälkimmäinen paljastaa katkaisun
  vaikutuksen.

## Itsearviointi

- Osaat laskea NCO:n taajuuden ja taajuusresoluution
  akkumulaattorin leveydestä ja taajuussanasta.
- Osaat toteuttaa neljännesjakson taulukon peilauksineen ja
  selittää puolen askeleen siirron hyödyn.
- Osaat selittää, mistä vaiheen katkaisun kannuspiikit tulevat ja
  miten niiden taso riippuu vaihebiteistä.
- Osaat valita keinon kannuspiikkien vähentämiseen ja kertoa sen
  hinnan.
