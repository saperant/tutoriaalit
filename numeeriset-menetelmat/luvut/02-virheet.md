# Virheet ja stabiilisuus

Numeerisen tuloksen virhe syntyy kolmesta lähteestä:

- **Datavirhe**: syöte on mitattu tai pyöristetty, joten se ei ole
  täsmälleen oikea.
- **Katkaisuvirhe**: menetelmä korvaa äärettömän prosessin
  äärellisellä, esimerkiksi derivaatan erotusosamäärällä tai sarjan
  osasummalla. Se riippuu menetelmästä ja sen parametreista (askel,
  termien määrä), ja se on olemassa tarkoillakin luvuilla.
- **Pyöristysvirhe**: jokainen liukulukulasku pyöristää tuloksen
  lähimpään esitettävään lukuun. Kaksoistarkkuudella yksittäisen
  laskutoimituksen suhteellinen virhe on enintään
  $u = 2^{-53} \approx 1{,}1 \cdot 10^{-16}$. Konetarkkuus
  $\varepsilon = 2u \approx 2{,}2 \cdot 10^{-16}$ on ykkösen ja sitä
  seuraavan liukuluvun erotus (taito *Miten tietokone laskee*, luku 6).

Jos tarkka arvo on $x$ ja likiarvo $\hat x$, **absoluuttinen virhe** on
$|\hat x - x|$ ja **suhteellinen virhe** $|\hat x - x| / |x|$.
Suhteellinen virhe kertoo oikeiden merkitsevien numeroiden määrän:
virhe $10^{-6}$ tarkoittaa noin kuutta oikeaa numeroa. Absoluuttinen
virhe on oikea mitta, kun tarkka arvo on nolla tai lähellä sitä.

Tämän luvun pääajatus on erottaa kaksi asiaa, jotka usein sekoitetaan:
**ongelman herkkyys** (ehtoluku) ja **algoritmin laatu** (stabiilisuus).
Huonokuntoista ongelmaa ei mikään algoritmi ratkaise tarkasti, mutta
huono algoritmi voi pilata hyväkuntoisenkin ongelman.

## Ehtoluku

Ongelman **ehtoluku** kertoo, kuinka paljon syötteen pieni suhteellinen
muutos muuttaa tulosta suhteellisesti. Derivoituvalle funktiolle $f$
Taylorin kehitelmästä saadaan

$$\frac{|f(x(1+\delta)) - f(x)|}{|f(x)|} \approx
\underbrace{\left|\frac{x f'(x)}{f(x)}\right|}_{\kappa_f(x)} |\delta|.$$

Ehtoluku $\kappa$ on ongelman ominaisuus, ei algoritmin. Esimerkki
laskee sen neljälle funktiolle ja kokeilee, kasvaako häiriö ennusteen
mukaan.

```{.python tiedosto="esimerkit/02-ehtoluku.py" osa="ehtoluku"}
```

```{.tuloste tiedosto="esimerkit/02-ehtoluku.odotettu"}
```

Neliöjuuri puolittaa suhteellisen virheen, joten se on hyväkuntoinen.
Eksponenttifunktion ehtoluku on $|x|$, eli suurilla argumenteilla
syötteen virhe kasvaa. Logaritmi ykkösen lähellä ja tangentti
napansa lähellä ovat huonokuntoisia: syötteen kymmenes numero
vaikuttaa tuloksen kuudenteen numeroon. Nyrkkisääntö: **tuloksessa on
noin $\log_{10}\kappa$ numeroa vähemmän oikein kuin syötteessä.**
Jos $\kappa \approx 10^{16}$, kaksoistarkkuus ei riitä yhteenkään
oikeaan numeroon.

Sama käsite koskee yhtälöryhmiä (luku 6), polynomien juuria (luku 3)
ja pienimmän neliösumman sovitusta (luku 4). Niissä ehtoluku lasketaan
matriisista, mutta tulkinta on sama.

## Stabiili ja epästabiili algoritmi

Algoritmi on **stabiili**, jos sen tuottama virhe on samaa
suuruusluokkaa kuin ongelman ehtoluvun aiheuttama väistämätön virhe.
Johdannon Taylorin sarja arvolla $x = -20$ on epästabiili, vaikka
tehtävä $e^{-20}$ on hyväkuntoinen: ehtoluku on vain 20.

Selkeä esimerkki on rekursio. Integraalit

$$I_n = \int_0^1 x^n e^{x-1}\,dx$$

toteuttavat osittaisintegroinnin perusteella palautuskaavan
$I_n = 1 - n I_{n-1}$, ja $I_0 = 1 - 1/e$. Kaava näyttää täydelliseltä
tavalta laskea koko jono, mutta jokaisella askeleella edellisen arvon
virhe kerrotaan luvulla $n$. Kun kaavan kääntää muotoon
$I_{n-1} = (1 - I_n)/n$ ja laskee taaksepäin, virhe *jaetaan* luvulla
$n$. Silloin aloitusarvon voi jopa arvata.

```{.python tiedosto="esimerkit/02-rekursio.py" osa="eteen"}
```

```{.python tiedosto="esimerkit/02-rekursio.py" osa="taakse"}
```

```{.python tiedosto="esimerkit/02-rekursio.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/02-rekursio.odotettu"}
```

Eteenpäin laskettu jono on hyvä pitkään, kunnes virhe räjähtää:
arvon $I_0$ pyöristysvirhe enintään $7 \cdot 10^{-17}$ kerrotaan
luvulla $20! \approx 2{,}4 \cdot 10^{18}$. Taaksepäin laskettu jono on
oikein, vaikka aloitusarvo $I_{40} = 0$ on täysin väärä: sen virhe on
jaettu luvulla $40 \cdot 39 \cdots 21$, ennen kuin päästään arvoon
$I_{20}$.

Sama ilmiö esiintyy kaikissa palautuskaavoissa, kuten Besselin
funktioissa, ortogonaalipolynomeissa ja digitaalisissa suotimissa.
Sääntö on: **laske siihen suuntaan, jossa virhe pienenee**.

## Kumoutuminen ja uudelleenkirjoitus

Kahden lähes yhtä suuren luvun erotuksessa merkitsevät numerot
kumoutuvat. Itse vähennyslasku on tarkka, mutta se paljastaa
operandien aiemmat virheet. Lääke on kirjoittaa kaava uudelleen
muotoon, jossa vähennyslaskua ei tarvita. Klassisia esimerkkejä ovat
$\sqrt{x+1} - \sqrt{x} = 1/(\sqrt{x+1} + \sqrt{x})$, kirjastojen
`log1p` ja `expm1` sekä toisen asteen yhtälön stabiili ratkaisukaava
(taito *Matematiikan perusteet ohjelmallisesti*, luku 3).

Opettavaisempi esimerkki on otosvarianssi. Oppikirjojen
"laskukaava" $s^2 = \bigl(\sum x_i^2 - n\bar x^2\bigr)/(n-1)$ kerää
summat yhdellä läpikäynnillä, mikä tuntuu tehokkaalta:

```{.python tiedosto="esimerkit/02-varianssi.py" osa="yksivaihe"}
```

Kaksivaiheinen algoritmi laskee ensin keskiarvon ja sitten
poikkeamien neliöt. **Welfordin algoritmi** päivittää keskiarvoa ja
neliösummaa yhdellä läpikäynnillä niin, ettei suuria lukuja vähennetä
toisistaan:

```{.python tiedosto="esimerkit/02-varianssi.py" osa="kaksivaihe"}
```

```{.python tiedosto="esimerkit/02-varianssi.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/02-varianssi.odotettu"}
```

Mittaukset ovat noin $10^9$, joten niiden neliöt ovat noin $10^{18}$.
Kaksoistarkkuudella lukujen $10^{18}$ väli on 128, eikä varianssi 30
erotu niiden erotuksesta lainkaan. Ongelma ei ole teoreettinen: sama
kaava on monen taulukkolaskentaohjelman ja anturiohjelmiston
varianssifunktiossa, ja aikaleimat, koordinaatit ja rahasummat ovat
juuri tällaista dataa, jossa suuri tasoarvo ja pieni vaihtelu.

## Eteenpäin- ja taaksepäinvirhe

Kun algoritmi palauttaa likiarvon $\hat y$ tehtävälle $y = f(x)$,
virheen voi mitata kahdella tavalla:

- **Eteenpäinvirhe** $|\hat y - y|$ on se, mitä käyttäjä haluaa tietää,
  mutta tarkkaa $y$:tä ei yleensä tunneta.
- **Taaksepäinvirhe** on pienin syötteen muutos $\Delta x$, jolla
  $\hat y$ on *tarkka* vastaus: $\hat y = f(x + \Delta x)$. Algoritmi
  on **taaksepäin stabiili**, jos taaksepäinvirhe on
  pyöristysvirheen suuruinen.

Nämä kytkeytyvät toisiinsa ehtoluvun kautta:

$$\text{eteenpäinvirhe} \lesssim \kappa \cdot \text{taaksepäinvirhe}.$$

Arvion merkitys on suuri. Taaksepäinvirheen voi usein laskea
(yhtälöryhmälle se on jäännös $b - A\hat x$, luku 6), ja ehtoluvun voi
arvioida. Niistä saadaan raja virheelle, jota ei voi mitata suoraan.
Gaussin eliminointi tuennalla, QR-hajotelma ja kirjastojen
peruslaskut ovat taaksepäin stabiileja, joten huono tulos niistä
kertoo huonokuntoisesta ongelmasta, ei huonosta ohjelmasta.

## Summauksen virhe ja Kahanin summa

Kun $n$ lukua lasketaan yhteen järjestyksessä, jokainen yhteenlasku voi
tehdä suhteellisen virheen $u$, ja virheet kasautuvat. Pahimmassa
tapauksessa suhteellinen virhe on noin $(n-1)u$ (kun termit ovat
samanmerkkisiä). **Kahanin kompensoitu summa** kerää jokaisen
yhteenlaskun pyöristysvirheen erilliseen muuttujaan ja lisää sen
seuraavaan termiin:

```{.python tiedosto="esimerkit/02-kahan.py" osa="kahan"}
```

Rivi `c = (t - s) - y` näyttää matemaattisesti nollalta, ja juuri siksi
se toimii: liukuluvuilla se on täsmälleen se osa luvusta `y`, joka ei
mahtunut summaan. Kääntäjä ei saa sieventää riviä pois, minkä vuoksi
C-ohjelmissa ei käytetä valitsinta `-ffast-math` (taito *Miten
tietokone laskee*, luku 7).

```{.python tiedosto="esimerkit/02-kahan.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/02-kahan.odotettu"}
```

Esimerkki laskee 32-bittisillä luvuilla, joissa on noin seitsemän
numeroa, jotta ero näkyy jo sadallatuhannella termillä. Tavallinen
summa menettää lähes kolme numeroa, mutta pysyy selvästi pahimman
tapauksen rajan alapuolella, koska pyöristysvirheet ovat osin
satunnaisia ja kumoavat toisiaan. Kahanin summa on lähes täsmälleen
oikein. NumPyn `sum` käyttää **parittaista summausta**: se laskee
puolikkaat erikseen ja yhdistää ne, jolloin virhe kasvaa vain kuten
$u\log_2 n$. Pythonin `math.fsum` on vielä parempi, sillä se antaa
oikein pyöristetyn tuloksen.

## Käytännössä

- **Arvioi ehtoluku ennen kuin syytät algoritmia.** Jos ehtoluku on
  $10^{12}$, kaksoistarkkuudella saa enintään neljä oikeaa numeroa.
  Silloin tehtävä kannattaa muotoilla uudelleen (esimerkiksi
  ortogonaalisilla kantafunktioilla) tai hankkia tarkempaa dataa.
- **Etsi vähennyslaskut, joissa operandit ovat lähes yhtä suuria.**
  Ne ovat tavallisin tarkkuuden menetys. Kirjoita kaava uudelleen tai
  käytä erikoisfunktiota (`log1p`, `expm1`, `hypot`).
- **Älä laske varianssia yhden läpikäynnin oppikirjakaavalla.** Käytä
  kahta läpikäyntiä tai Welfordin algoritmia. Sama koskee
  kovarianssia ja korrelaatiota.
- **Palautuskaavoissa ja iteraatioissa tarkista, kasvaako vai
  pieneneekö virhe.** Kerroin $n$ joka askeleella on hälytysmerkki.
- **Summaa kirjastofunktiolla.** `math.fsum`, NumPyn `sum` ja
  Kahanin summa ovat tarkempia kuin silmukka. Suurissa summissa
  järjestyksellä on väliä: pienet termit ensin.
- **Testaa numeerista koodia tunnetulla vastauksella**, ja vertaa
  tulosta suhteellisella toleranssilla, ei yhtäsuuruudella.

## Itsearviointi

- Osaat erottaa toisistaan datavirheen, katkaisuvirheen ja
  pyöristysvirheen sekä absoluuttisen ja suhteellisen virheen.
- Osaat laskea funktion ehtoluvun ja arvioida siitä, kuinka monta
  oikeaa numeroa tulokseen voi odottaa.
- Osaat selittää, miksi palautuskaava voi olla epästabiili toiseen
  suuntaan ja stabiili toiseen.
- Osaat tunnistaa kumoutumisen ja kirjoittaa kaavan, kuten varianssin,
  stabiiliin muotoon.
- Osaat selittää eteenpäin- ja taaksepäinvirheen ja niiden yhteyden
  ehtoluvun kautta.
- Osaat käyttää kompensoitua tai parittaista summaa ja tiedät, miksi
  tavallisen summan virhe kasvaa termien määrän mukana.
