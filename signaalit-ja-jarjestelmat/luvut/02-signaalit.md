# Diskreettiaikaiset signaalit

Diskreettiaikainen signaali on jono $x[n]$, jossa indeksi $n$ on
kokonaisluku. Kun jono syntyy näytteistämällä, $x[n] = x(nT_s)$, mutta
jono on myös itsenäinen matemaattinen olio: sillä ei ole arvoa
näytteiden välissä. Tässä luvussa käydään läpi perussignaalit, signaalien
luokittelu energian ja tehon mukaan sekä diskreetin ajan yllätys:
sinijono ei aina ole jaksollinen, ja taajuudet ovat monikäsitteisiä.

## Jatkuva, diskreetti ja digitaalinen

Signaaleja luokitellaan kahdella akselilla. **Aika** on jatkuva
(kaikki reaaliluvut $t$) tai diskreetti (kokonaisluvut $n$).
**Amplitudi** on jatkuva (mikä tahansa reaaliluku) tai kvantisoitu
(äärellinen määrä tasoja). Mikrofonin jännite on jatkuva molemmilta
osin. Näytteistetty mutta kvantisoimaton jono on teorian
diskreettiaikainen signaali. **Digitaalinen** signaali on sekä
näytteistetty että kvantisoitu: 16-bittinen äänitiedosto on sellainen.

Teoria käsittelee lähes aina diskreettiaikaisia mutta kvantisoimattomia
jonoja, ja kvantisointi mallinnetaan erikseen pienenä lisäkohinana
(luku 3). NumPyn `float64`-taulukko on käytännössä kvantisoimaton, koska
sen virhe on noin $10^{-16}$ suhteessa arvoon.

## Perussignaalit

Kolme jonoa toistuu kaikkialla. **Yksikköimpulssi** $\delta[n]$ on 1,
kun $n = 0$, ja muuten 0. **Yksikköaskel** $u[n]$ on 1, kun $n \ge 0$, ja
muuten 0. **Eksponenttijono** $a^n u[n]$ alkaa hetkellä nolla ja kasvaa
tai vaimenee kertoimen $a$ mukaan. Kun $a$ on kompleksinen,
$a = re^{i\omega}$, jono on pyörivä ja kasvava tai vaimeneva osoitin,
ja sen reaaliosa on vaimeneva sini. Tämä jono on luvun 6
rekursiivisten suotimien impulssivaste.

NumPyssa jono on taulukko, jonka indeksit alkavat nollasta. Kun jono
alkaa negatiivisesta indeksistä, indeksit pidetään erillisessä
taulukossa, ja jonot lasketaan vertailuilla:

```{.python tiedosto="esimerkit/02-perussignaalit.py" osa="perus"}
```

Aikaindeksin operaatiot ovat **viive** $x[n - n_0]$ (siirto oikealle,
kun $n_0 > 0$), **aikakääntö** $x[-n]$ ja niiden yhdistelmät. Jokainen
jono on summa siirrettyjä ja skaalattuja impulsseja:

$$x[n] = \sum_k x[k]\,\delta[n - k].$$

Kaava näyttää itsestään selvältä, mutta se on LTI-teorian perusta:
luvussa 4 järjestelmän vaste lasketaan tästä hajotelmasta.

```{.python tiedosto="esimerkit/02-perussignaalit.py" osa="operaatiot"}
```

```{.tuloste tiedosto="esimerkit/02-perussignaalit.odotettu"}
```

Kahden askeleen erotus $u[n] - u[n-3]$ on pulssi, jossa on kolme
ykköstä. Sama tekniikka rakentaa ikkunoita ja portteja.

## Energia ja teho

Jonon **energia** on $E = \sum_n |x[n]|^2$, ja sen **teho** on
keskiarvo kasvavan ikkunan yli:

$$P = \lim_{M\to\infty} \frac{1}{2M+1}\sum_{n=-M}^{M} |x[n]|^2.$$

**Energiasignaalin** energia on äärellinen, jolloin sen teho on nolla.
Lyhyt pulssi ja vaimeneva eksponentti ovat energiasignaaleja.
**Tehosignaalin** teho on äärellinen ja nollasta poikkeava, jolloin sen
energia on ääretön. Jaksolliset signaalit, askel ja kohina ovat
tehosignaaleja. Jako ratkaisee, mitä työkalua käytetään: energiasignaalille
lasketaan energiaspektri ja tehosignaalille tehospektri (luku 9).

Eksponenttijonon energia on geometrinen sarja:
$\sum_{n\ge 0} a^{2n} = 1/(1 - a^2)$, kun $|a| < 1$.

```{.python tiedosto="esimerkit/02-energia.py" osa="energia"}
```

Askeleen teho lähestyy arvoa $1/2$, koska ikkunasta puolet on nollia, ja
amplitudin $A$ sinin teho lähestyy arvoa $A^2/2$. Askeleen energia sen
sijaan kasvaa ikkunan mukana rajatta.

```{.python tiedosto="esimerkit/02-energia.py" osa="teho"}
```

```{.tuloste tiedosto="esimerkit/02-energia.odotettu"}
```

Kun $a = 0.99$, energia on 50: vaimeneva jono on pitkä, ja sen pituus
näkyy energiassa. Sama luku tulee vastaan luvussa 6, kun lasketaan, kuinka
paljon eksponentiaalinen tasoitin vaimentaa kohinaa.

## Jaksollisuus diskreetissä ajassa

Jatkuva sini $\cos(2\pi f t)$ on jaksollinen kaikilla taajuuksilla.
Diskreetti jono $x[n] = \cos(2\pi f n)$, jossa $f$ on taajuus jaksoina
näytettä kohti, on jaksollinen vain, jos jokin kokonaisluku $N$ täyttää
ehdon $fN \in \mathbb{Z}$. Toisin sanoen $f$ on rationaaliluku $p/q$,
ja supistetussa muodossa jakso on $N = q$ näytettä.

Esimerkiksi $f = 3/8$ tarkoittaa, että kahdeksassa näytteessä kuluu
kolme kokonaista jaksoa, joten jono toistuu kahdeksan näytteen välein,
vaikka yksi aalto on $8/3$ näytettä pitkä. Jos kulmataajuus on
$\omega = 1$ radiaani näytettä kohti, $f = 1/(2\pi)$ on irrationaalinen,
eikä jono koskaan toistu täsmälleen.

```{.python tiedosto="esimerkit/02-jaksollisuus.py" osa="jakso"}
```

Käytännössä tällä on merkitystä silloin, kun ohjelma tuottaa sinin
taulukosta tai laskee DFT:tä: vain kokonainen määrä jaksoja ikkunassa
tuottaa siistin spektrin (luku 9).

## Taajuuksien monikäsitteisyys

Diskreetillä jonolla on toinen ominaisuus, jota jatkuvalla signaalilla
ei ole. Taajuudet $f$ ja $f + 1$ (jaksoina näytettä kohti) tuottavat
täsmälleen samat näytteet, koska $e^{2\pi i (f+1) n} = e^{2\pi i f n}
e^{2\pi i n}$ ja $e^{2\pi i n} = 1$ kaikilla kokonaisluvuilla $n$.
Kosinille myös $f$ ja $-f$ ovat samat, joten $f$ ja $1 - f$ antavat
saman jonon.

```{.python tiedosto="esimerkit/02-jaksollisuus.py" osa="moni"}
```

```{.tuloste tiedosto="esimerkit/02-jaksollisuus.odotettu"}
```

Neljä eri taajuutta tuottaa saman jonon. Siksi diskreetin ajan
taajuusakseli on ympyrä: kaikki erottuvat taajuudet mahtuvat välille
$-1/2 < f \le 1/2$ eli $-\pi < \omega \le \pi$. Suurin taajuus on
$\pi$ radiaania näytettä kohti, jolloin jono vaihtaa merkkiään joka
näytteellä: $(-1)^n$. Kun jono on syntynyt näytteistämällä, tämä
monikäsitteisyys on aliasointia, ja se on seuraavan luvun aihe.

## Käytännössä

- **Pidä indeksit erillään taulukosta.** Kun jono alkaa negatiivisesta
  hetkestä, säilytä aikaindeksi omana taulukkonaan, äläkä luota siihen,
  että taulukon indeksi 0 on hetki $n = 0$.
- **Ilmaise taajuus selvillä yksiköillä.** Hertsit, jaksot näytettä
  kohti ja radiaanit näytettä kohti sekoittuvat helposti. Muuttujan nimi
  tai kommentti kertoo yksikön.
- **Luokittele ennen kuin analysoit.** Energiasignaalista lasketaan
  energia, tehosignaalista teho. Kohinan energia kasvaa rajatta, joten
  kohinaa verrataan aina tehona.
- **Tuota testisignaalit kokonaisin jaksoin**, jos haluat siistin
  spektrin, ja tarkista jaksollisuus rationaaliluvuilla
  (`fractions.Fraction`) eikä liukuluvuilla.

## Itsearviointi

- Osaat muodostaa NumPylla impulssin, askeleen, eksponenttijonon,
  viiveen ja aikakäännön sekä hajottaa jonon siirretyiksi impulsseiksi.
- Osaat luokitella signaalin energia- tai tehosignaaliksi ja laskea
  eksponenttijonon energian sekä sinin ja askeleen tehon.
- Osaat päätellä, milloin $\cos(2\pi f n)$ on jaksollinen, ja laskea
  sen jakson.
- Osaat selittää, miksi taajuudet $f$, $f + 1$ ja $1 - f$ tuottavat
  saman kosinijonon ja miksi suurin taajuus on $\pi$ radiaania
  näytettä kohti.
