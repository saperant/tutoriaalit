# Johdanto {.runko-johdanto}

Numeeriset menetelmät ovat algoritmeja, joilla matemaattinen tehtävä
ratkaistaan likimäärin luvuilla: yhtälön juuri, integraalin arvo,
yhtälöryhmän ratkaisu, differentiaaliyhtälön käyrä tai funktion minimi.
Symbolinen laskenta antaa kaavan, kun sellainen on olemassa. Useimmille
käytännön tehtäville kaavaa ei ole, tai se on liian raskas, ja silloin
tarvitaan numeriikkaa.

Numeerisen tuloksen kanssa tulee aina kaksi kysymystä:

1. **Kuinka tarkka tulos on?** Jokaisessa menetelmässä on
   *katkaisuvirhe*, koska ääretön prosessi (raja-arvo, sarja, jatkuva
   funktio) korvataan äärellisellä. Lisäksi tietokoneen liukuluvuissa on
   *pyöristysvirhe*.
2. **Kuinka paljon tulos maksaa?** Funktion arvojen, kertolaskujen tai
   iteraatioiden määrä kasvaa, kun tarkkuutta vaaditaan lisää.
   Menetelmän *kertaluku* kertoo, kuinka nopeasti.

Tämä tutoriaali käy läpi insinöörin ja diplomi-insinöörin tärkeimmät
numeeriset menetelmät ja keskittyy noihin kahteen kysymykseen. Jokainen
menetelmä toteutetaan ensin itse lyhyesti, jotta sen toiminta ja virheet
ymmärretään. Sen jälkeen käytetään valmista kirjastoa, koska tuotannossa
kirjasto on lähes aina parempi. Jokaisen virheen suuruutta verrataan
teoreettiseen rajaan, joten lukija näkee, milloin teoria pitää ja milloin
ei.

## Esitiedot ja rajaus

Tutoriaali olettaa taidot *Differentiaali- ja integraalilaskenta*
(derivaatta, integraali, Taylorin polynomi, Newtonin menetelmä) ja
*Lineaarialgebra* (matriisit, Gaussin eliminointi, LU- ja
QR-hajotelmat, ominaisarvot). Niissä menetelmät esitellään; tässä
syvennytään siihen, miksi ne toimivat tai eivät toimi tietokoneessa.
Liukulukujen esitysmuoto (IEEE 754), pyöristystilat ja ulp käsitellään
taidossa *Miten tietokone laskee*, eikä niitä toisteta.

Differentiaaliyhtälöiden mallintaminen ja analyyttinen ratkaiseminen
kuuluvat taitoon *Differentiaaliyhtälöt ja Laplace-muunnos*. Tämä
tutoriaali käsittelee numeeristen ratkaisijoiden kertaluvut,
stabiilisuuden ja askeleen valinnan.

## Työkalut

Esimerkit kirjoitetaan Pythonilla, ja niissä käytetään kirjastoja NumPy
(taulukot ja lineaarialgebra) ja SciPy (integrointi, optimointi,
interpolointi, harvat matriisit ja differentiaaliyhtälöt). Kirjastojen
perusteet esitellään taidossa *Matematiikan perusteet
ohjelmallisesti*.

Rinnakkaistyökaluna on **GNU Octave**, avoimen lähdekoodin numeerisen
laskennan ympäristö, jonka kieli on lähes sama kuin kaupallisen
MATLABin. Monissa yrityksissä ja korkeakouluissa numeriikkaa tehdään
MATLABilla, joten sen kieltä kannattaa osata lukea. Useimmissa luvuissa
on lyhyt Octave-esimerkki, joka tekee saman kuin Python-esimerkit.
Octave-skripti ajetaan eräajona:

```{.make tiedosto="esimerkit/Makefile" osa="octave"}
```

Kaikkien esimerkkien tulosteet on tarkistettu. Liukulukujen viimeiset
numerot voivat vaihdella koneen ja lineaarialgebrakirjaston (BLAS,
LAPACK) mukaan, joten tulosteissa näytetään vain luotettavat numerot tai
tieto siitä, alittaako virhe teoreettisen rajan.

## Ensimmäinen esimerkki: sama luku kahdella algoritmilla

Lasketaan $e^{-20}$ Taylorin sarjasta
$e^x = \sum_{k=0}^{\infty} x^k/k!$, joka suppenee kaikilla $x$.
Matemaattisesti on yhdentekevää, laskeeko suoraan arvolla $x = -20$
vai laskeeko $e^{20}$ ja ottaa käänteisluvun.

```{.python tiedosto="esimerkit/01-eksponentti.py" osa="sarja"}
```

```{.python tiedosto="esimerkit/01-eksponentti.py" osa="vertailu"}
```

```{.python tiedosto="esimerkit/01-eksponentti.py" osa="syy"}
```

```{.tuloste tiedosto="esimerkit/01-eksponentti.odotettu"}
```

Suora sarja antaa tuloksen, joka on kolminkertainen ja täysin väärä,
vaikka jokainen yhteenlasku on tehty niin tarkasti kuin liukuluvuilla
voi. Syy näkyy kahdesta viimeisestä rivistä. Sarjan termit vuorottelevat
merkiltään ja kasvavat suurimmillaan arvoon $4 \cdot 10^7$, ja jo
yhden tällaisen termin pyöristysvirhe on $5 \cdot 10^{-9}$ eli
suurempi kuin koko tulos. Kun suuret termit kumoavat toisensa, jäljelle
jää pelkkiä pyöristysvirheitä. Käänteisluvun kautta kaikki termit ovat
positiivisia, eikä kumoutumista synny.

Esimerkki tiivistää koko tutoriaalin: **algoritmi ratkaisee, ei kaava**.
Sama matemaattinen kaava voi olla numeerisesti erinomainen tai
käyttökelvoton sen mukaan, missä järjestyksessä laskut tehdään. Luku 2
antaa välineet tällaisten tilanteiden tunnistamiseen.

Sama koe Octavella näyttää kielen tyypilliset piirteet: vektorit
luodaan väliltä `0:149`, ja operaattorit `.^` ja `./` toimivat
alkioittain, joten silmukkaa ei tarvita.

```{.octave tiedosto="esimerkit/octave/01-alku.m"}
```

```{.tuloste tiedosto="esimerkit/octave/01-alku.odotettu"}
```

Octaven suora sarja antaa jopa väärän merkin. Tulos on eri kuin
Pythonilla, koska Octave laskee termit ja summan eri järjestyksessä.
Kun tulos on pelkkää pyöristysvirhettä, laskujärjestyksen pienikin
muutos muuttaa sitä.

## Tutoriaalin rakenne

1. Johdanto
2. Virheet ja stabiilisuus – ehtoluku, kumoutuminen, stabiili ja
   epästabiili algoritmi, kompensoitu summa
3. Epälineaariset yhtälöt – puolitus, kiintopiste, Newton, sekantti,
   kertaluvun mittaaminen, polynomien juuret ja yhtälöryhmät
4. Interpolointi ja sovitus – Newtonin muoto, Rungen ilmiö, splinit,
   pienimmän neliösumman sovitus
5. Numeerinen derivointi ja integrointi – optimaalinen askel,
   Richardson, Gaussin kvadratuuri, adaptiivisuus ja singulariteetit
6. Lineaariset yhtälöryhmät – tuenta, hajotelmat, ehtoluku ja
   virherajat
7. Harvat matriisit ja iteratiiviset menetelmät – Jacobi,
   Gauss–Seidel, liittogradientti, esiehdostus
8. Differentiaaliyhtälöiden ratkaisijat – kertaluvut, stabiilisuus,
   jäykkyys ja adaptiivinen askel
9. Optimointi – kultainen leikkaus, gradientti- ja Newtonin menetelmä,
   BFGS, lineaarinen optimointi
10. Lopuksi – nyrkkisäännöt, Python ja Octave rinnakkain, lähteet
