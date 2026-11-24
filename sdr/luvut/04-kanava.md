# NCO, sekoitus ja kanavan valinta

Laitteen näytevirta sisältää koko viritetyn kaistan. Vastaanotin
tarvitsee siitä yhden kanavan: FM-asema on 200 kHz leveä, anturiradion
kanava muutaman kymmenen kHz:n levyinen. Kanavan valinnassa on kolme
vaihetta. Ensin kanava siirretään nollataajuudelle, sitten muut
taajuudet suodatetaan pois, ja lopuksi näytetaajuus pudotetaan kanavan
kaistan mukaiseksi. Valinta on vastaanottimen raskain osa, koska se
tehdään täydellä näytetaajuudella.

## Siirto kompleksisella oskillaattorilla

Kantataajuisessa signaalissa taajuussiirto on kertolasku:
$y[n] = x[n]\,e^{-i2\pi f_0 n/f_s}$ siirtää taajuudella $f_0$ olevan
signaalin nollaan. Toisin kuin reaalinen sekoitus, kompleksinen
kertolasku ei tuota peilikuvaa. Luvun 1 tallenteen vahva asema
siirretään näin 200 kHz:stä nollaan.

Oskillaattorin näytteiden laskeminen funktioilla `cos` ja `sin`
jokaiselle näytteelle on hidasta, ja pitkässä virrassa vaiheen
laskeminen kaavalla $2\pi f_0 n / f_s$ menettää tarkkuutta, kun $n$
kasvaa. Laitteistossa ja nopeassa ohjelmistossa käytetään siksi
**NCO:ta** (*numerically controlled oscillator*).

## NCO

NCO:n vaiheakkumulaattori on kokonaisluku, jonka täysi arvoalue vastaa
yhtä kierrosta. 32 bitin akkumulaattoriin lisätään jokaisella
näytteellä askel $\text{round}(f_0/f_s \cdot 2^{32})$, ja ylivuoto
hoitaa vaiheen jakojäännöksen $2\pi$:n suhteen. Akkumulaattorin
ylimmät bitit osoittavat taulukkoon, jossa on valmiiksi laskettu
kompleksinen eksponentti.

```{.python tiedosto="esimerkit/04-nco.py" osa="nco"}
```

Akkumulaattorin pituus määrää taajuusresoluution:

```{.python tiedosto="esimerkit/04-nco.py" osa="resoluutio"}
```

Taulukon koko määrää puhtauden. Vaiheen katkaiseminen taulukon
osoitteeksi on jaksollinen virhe, joka näkyy **harhalähtöinä**
(*spurs*). Nyrkkisääntö on noin 6 dB taulukon osoitebittiä kohti:

```{.python tiedosto="esimerkit/04-nco.py" osa="sfdr"}
```

```{.tuloste tiedosto="esimerkit/04-nco.odotettu"}
```

4096 alkion taulukko (64 kt kompleksisina `double`-lukuina) antaa yli
70 dB:n harhalähdöttömyyden, mikä riittää 8-bittiselle laitteelle
reilusti. Jos tarvitaan enemmän, vaiheeseen voi lisätä ditheröinnin,
joka muuttaa harhalähdöt tasaiseksi kohinaksi, tai taulukon arvojen
välillä voi interpoloida. Laitteistossa käytetään usein CORDIC-
algoritmia, joka laskee kierron pelkillä yhteen- ja
siirtolaskuilla. Sama NCO toteutetaan C++:lla luvussa 8.

## Monivaiheinen desimointi

Siirron jälkeen kanava suodatetaan alipäästösuotimella ja näytetaajuus
pudotetaan. Desimoinnissa lasketaan vain jokainen $D$:s lähtönäyte,
joten suotimen kustannus näytettä kohti on (kertoimet)/$D$. Suotimen
pituus riippuu siirtymäkaistan suhteellisesta leveydestä:
$N \approx A/(22\,\Delta f/f_s)$, kun vaimennus $A$ on desibeleinä.
Kapea siirtymä korkealla näytetaajuudella vaatii pitkän suotimen.

Esimerkissä 12,5 kHz:n kapea kanava (esimerkiksi puhe-FM) valitaan
2,4 MS/s:n virrasta 48 kS/s:iin, eli $D = 50$. Yksivaiheinen suodin
tarvitsee siirtymän 12,5 kHz → 24 kHz täydellä näytetaajuudella.
Kaksivaiheisessa ratkaisussa ensimmäinen vaihe desimoi kymmenellä.
Sen estokaistan tarvitsee alkaa vasta 216 kHz:stä, koska vain
taajuudet 240 kHz ± 24 kHz laskostuvat lopulliselle kaistalle.

```{.python tiedosto="esimerkit/04-desimointi.py" osa="suunnittelu"}
```

```{.python tiedosto="esimerkit/04-desimointi.py" osa="kustannus"}
```

Kumpikin ratkaisu vaimentaa 40 kHz:n häiritsijän, joka laskostuisi
48 kS/s:lla taajuudelle −8 kHz:

```{.python tiedosto="esimerkit/04-desimointi.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/04-desimointi.odotettu"}
```

Kaksivaiheinen ketju on 2,5 kertaa kevyempi, ja säästö kasvaa
desimointikertoimen mukana. Nyrkkisääntö on, että ensimmäiset vaiheet
desimoivat paljon kevyillä suotimilla ja viimeinen vaihe tekee
jyrkän siirtymän pienellä näytetaajuudella. Ensimmäisinä vaiheina
käytetään usein puolikaistasuotimia ($D = 2$, joka toinen kerroin
nolla) tai kertolaskuttomia CIC-suotimia (*Digitaalinen
signaalinkäsittely*, luku 9).

## Polyfaasisuodinpankki

Kun samasta kaistasta halutaan monta kanavaa, esimerkiksi kaikki
kahdeksan 100 kHz:n kanavaa 800 kS/s:n kaistalta, suora tapa toistaa
sekoituksen, suodatuksen ja desimoinnin jokaiselle kanavalle:

```{.python tiedosto="esimerkit/04-kanavapankki.py" osa="suora"}
```

**Polyfaasisuodinpankki** (*channelizer*) tekee saman työn kerralla.
Prototyyppisuodin jaetaan $M$ osasuotimeksi $h_r[p] = h[pM + r]$, ja
tulo $M$ osajonoksi $x_r[m] = x[mM - r]$. Osasuotimet toimivat
valmiiksi pienellä näytetaajuudella, ja sekoitukset korvautuvat
yhdellä $M$-pisteisellä IFFT:llä:
$y_k[m] = \sum_r v_r[m]\,e^{i2\pi kr/M}$.

```{.python tiedosto="esimerkit/04-kanavapankki.py" osa="polyfaasi"}
```

Tulos on täsmälleen sama kuin suoralla tavalla, mutta laskenta on
murto-osa. Tulostuksessa tulosignaalin kolme ääntä löytyvät
kanavista 1, 3 ja 6 (+100, +300 ja −200 kHz) oikeilla tasoillaan
0, −20 ja −40 dB.

```{.python tiedosto="esimerkit/04-kanavapankki.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/04-kanavapankki.odotettu"}
```

Polyfaasipankit ovat matkapuhelinverkkojen tukiasemien,
satelliittivastaanottimien ja radioastronomian perustyökalu. Tässä
kanavien reunat menevät päällekkäin, koska desimointi on kriittinen
($D = M$). Käytännön pankeissa desimoidaan usein $M/2$:lla, jolloin
kanavien väliin ei jää katvealueita.

## Käytännössä

- **Siirrä ensin, suodata sitten.** Kun kanava on nollassa, sama
  symmetrinen alipäästösuodin kelpaa kaikille kanaville. Kompleksiset
  kaistanpäästösuotimet ovat harvoin tarpeen.
- **Käytä NCO:ta pitkissä virroissa.** Kokonaislukuakkumulaattori ei
  kadota tarkkuutta, ja taulukko on nopeampi kuin trigonometriset
  funktiot.
- **Desimoi vaiheittain.** Kustannuksen voi arvioida
  (kertoimet)/(kertynyt desimointi) -summana jo suunnitteluvaiheessa.
  Laske kustannus myös kompleksisena: kompleksinen näyte kertaa
  reaalinen kerroin on kaksi kertolaskua.
- **Mitoita suotimet laskostuvan kaistan mukaan.** Ensimmäisen
  vaiheen estokaista määräytyy siitä, mikä laskostuu lopulliselle
  kaistalle, ei lopullisen kanavan reunasta.
- **Monta kanavaa: polyfaasipankki.** Jo muutamalla kanavalla
  pankki on kevyempi kuin erilliset ketjut, ja se skaalautuu satoihin
  kanaviin.

## Itsearviointi

- Osaat siirtää kanavan nollataajuudelle kompleksisella
  oskillaattorilla ja selittää, miksi peilikuvaa ei synny.
- Osaat toteuttaa NCO:n vaiheakkumulaattorilla ja taulukolla ja
  laskea sen taajuusresoluution ja harhalähdöttömyyden.
- Osaat suunnitella monivaiheisen desimointiketjun ja laskea sen
  kustannuksen kertolaskuina näytettä kohti.
- Osaat selittää, miten polyfaasisuodinpankki korvaa $M$ erillistä
  kanavaa yhdellä suotimella ja IFFT:llä.
