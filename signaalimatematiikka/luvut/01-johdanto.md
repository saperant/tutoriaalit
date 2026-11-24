# Johdanto {.runko-johdanto}

Signaali on suure, joka muuttuu ajan mukana: mikrofonin jännite,
kiihtyvyysanturin lukema, radiovastaanottimen näytteet tai verkkojännite
pistorasiassa. Ohjelmoija kohtaa signaaleja yllättävän usein. Äänitiedosto
on lista näytteitä, anturidatassa on kohinaa, joka pitää suodattaa, ja
langaton yhteys kuljettaa bittejä sinimuotoisten aaltojen vaiheessa ja
amplitudissa. Kun signaaleja käsitellään, kaksi kysymystä toistuu: mitä
taajuuksia signaalissa on ja mitä jokin käsittely tekee kullekin
taajuudelle.

Näihin kysymyksiin vastaa **Fourier-analyysi**. Sen ydinajatus on, että
lähes mikä tahansa signaali voidaan esittää sinimuotoisten aaltojen
summana. Summan kertoimet kertovat, kuinka paljon kutakin taajuutta
signaalissa on ja missä vaiheessa se on. Kertoimet ovat luonnostaan
**kompleksilukuja**, koska kompleksiluku pitää yhdessä luvussa sekä
amplitudin että vaiheen. Siksi tutoriaali alkaa kompleksiluvuista ja
etenee Eulerin kaavan ja osoittimien kautta Fourier-sarjaan,
Fourier-muunnokseen, konvoluutioon ja lopuksi diskreettiin
Fourier-muunnokseen, jota tietokone oikeasti laskee.

Tutoriaali opettaa asiat kolmella tavalla yhtä aikaa:

- **Geometria.** Kompleksiluku on tason piste, ja kertolasku on kierto
  ja skaalaus. Sinimuotoinen signaali on pyörivä nuoli. Fourier-muunnos
  on kannanvaihto kohtisuoraan kantaan, aivan kuten taidossa
  *Lineaarialgebra*.
- **Laskut koodina.** Jokainen kaava toteutetaan Pythonilla ja NumPylla:
  sarjat silmukoina, integraalit summina ja muunnokset matriiseina.
- **Numeerinen tarkistus.** Jokainen analyyttinen tulos tarkistetaan
  laskemalla, ja ero verrataan toleranssiin. Kun kaava ja numeerinen
  tulos täsmäävät, kaavaan voi luottaa ja sitä voi käyttää.

## Kenelle ja mitä tarvitaan

Lukija osaa ohjelmoida Pythonilla ja tuntee lineaarialgebran perusteet:
pistetulon, kannan, ortogonaalisuuden ja matriisitulon (taito
*Lineaarialgebra*). Koulumatematiikasta tarvitaan trigonometriaa ja
derivaatan ja integraalin idea; integraalit lasketaan tutoriaalissa
summina, joten integroimistekniikoita ei tarvita.

| Luku | Kysymys |
|------|---------|
| Kompleksiluvut | Miten tason pisteillä lasketaan, ja miksi kertolasku kiertää? |
| Eulerin kaava | Miten eksponenttifunktio, sini ja kosini liittyvät toisiinsa? |
| Sinimuotoiset signaalit | Miten amplitudi ja vaihe esitetään yhdellä luvulla? |
| Summat, sarjat ja integraalit | Miksi eri taajuudet eivät sekoitu keskenään? |
| Fourier-sarja | Miten jaksollinen signaali hajotetaan harmonisiksi? |
| Fourier-muunnos | Mitä taajuuksia jaksottomassa signaalissa on? |
| Konvoluutio | Mitä suodatin tekee, ja miksi se on taajuustasossa kertolasku? |
| DFT kannanvaihtona | Mitä `numpy.fft` laskee, ja miksi se on nopea? |

## Ensimmäinen esimerkki: mitä taajuuksia signaalissa on?

Seuraava ohjelma rakentaa yhden sekunnin signaalin kahdesta aallosta,
50 hertsin sinistä ja 120 hertsin kosinista, ja kysyy NumPylta, mitä
taajuuksia signaalissa on. Funktio `numpy.fft.rfft` laskee signaalin
diskreetin Fourier-muunnoksen, ja jokaisen kompleksisen kertoimen
itseisarvosta saadaan vastaavan taajuuden amplitudi.

```{.python tiedosto="esimerkit/01-taajuudet.py" osa="taajuudet"}
```

```{.tuloste tiedosto="esimerkit/01-taajuudet.odotettu"}
```

Ohjelma löytää molemmat aallot ja niiden amplitudit, eikä muita
taajuuksia ole. Aikatasossa signaali näyttää sekavalta käyrältä, mutta
taajuustasossa se on kaksi lukua. Tutoriaalin lopussa tiedät, miksi
amplitudi saadaan kaavalla $2|X_k|/N$, mitä kompleksiluvun kulma
kertoo, miksi tulos on näin siisti juuri tällä signaalilla ja mitä
`rfft` laskee sisäisesti.

## Merkinnät

Imaginaariyksikkö on $i$, jolle $i^2 = -1$. Sähkötekniikassa käytetään
usein kirjainta $j$, koska $i$ on varattu virralle; Python käyttää
myös $j$:tä (`3 + 4j`). Kompleksiluvun $z$ liittoluku on $\bar z$,
itseisarvo $|z|$ ja vaihekulma $\arg z$.

Jatkuvan ajan signaali on $x(t)$ ja diskreetti näytejono $x[n]$.
Taajuus $f$ mitataan hertseinä (jaksoa sekunnissa) ja kulmataajuus
$\omega = 2\pi f$ radiaaneina sekunnissa. Fourier-muunnos merkitään
isolla kirjaimella: $X(f)$ on signaalin $x(t)$ muunnos ja $X[k]$
näytejonon $x[n]$ diskreetti muunnos. Tutoriaali käyttää Fourier-
muunnoksen muotoa, jossa taajuus on hertseinä, koska silloin kaavoissa
ei ole ylimääräisiä $2\pi$-kertoimia.

Koodissa kreikkalaiset kirjaimet kirjoitetaan nimillä (`phi`, `theta`,
`omega`, `pi`), ja tulosteissa käytetään merkintöjä kuten `e^(i pi)`,
`sum` ja `int`, koska koodifontissa ei ole kaikkia matemaattisia
merkkejä.

## Työkalut

Esimerkit toimivat Python 3.12:lla ja NumPy 2:lla. Tyypit tarkistetaan
`mypy --strict` -tilassa ja tyyli `ruff`illa. Kehityskontissa
(`.devcontainer/signaalimatematiikka`) kaikki on valmiina. Jokainen
esimerkki ajetaan testeissä, ja sen tulostetta verrataan tallennettuun
tulosteeseen. Siksi tulosteet on pyöristetty, ja numeerisista virheistä
tulostetaan usein vain vertailu kuten `virhe < 1e-12: True`: liukulukujen
viimeiset desimaalit voivat vaihdella koneittain, mutta toleranssin
alittuminen ei vaihtele. Satunnaisdata tuotetaan aina kiinteällä
siemenellä (`numpy.random.default_rng(2026)`).

## Mitä tutoriaali ei kata

Tutoriaali on signaalinkäsittelyn matemaattinen perusta. Näytteistys,
aliasointi, diskreettiaikaiset järjestelmät, Z-muunnos ja DFT:n
käytännön kysymykset kuten ikkunointi ja vuotaminen ovat taidon
*Signaalit ja järjestelmät* aiheita; tässä niitä sivutaan vain siellä,
missä ne selittävät tuloksia. Laplace-muunnos, kompleksianalyysin
integraalilauseet ja jakaumateoria (Diracin delta täsmällisesti) jäävät
matematiikan kirjallisuuteen.
