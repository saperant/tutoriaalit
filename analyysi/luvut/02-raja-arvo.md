# Raja-arvo ja jatkuvuus

Raja-arvo vastaa kysymykseen, mitä arvoa funktio lähestyy, kun muuttuja
lähestyy jotakin kohtaa. Funktion ei tarvitse olla määritelty itse
kohdassa: lauseke $\frac{\sin x}{x}$ on nollassa muotoa $\frac00$, mutta
sen arvot lähestyvät ykköstä. Raja-arvon varaan rakentuvat derivaatta
(luku 3), integraali (luku 5) ja sarjat (luku 7). Luvussa lasketaan
raja-arvoja symbolisesti, katsotaan, miksi numeerinen kokeilu voi pettää,
ja määritellään jatkuvuus.

## Raja-arvon käsite

Merkintä $\lim_{x \to a} f(x) = L$ tarkoittaa, että $f(x)$ saadaan
mielivaltaisen lähelle lukua $L$ valitsemalla $x$ riittävän läheltä
kohtaa $a$ (mutta $x \ne a$). Täsmällinen muoto on **epsilon–delta-
määritelmä**: jokaista virherajaa $\varepsilon > 0$ kohti on olemassa
$\delta > 0$ niin, että

$$0 < |x - a| < \delta \implies |f(x) - L| < \varepsilon.$$

Määritelmä on kuin sopimus asiakkaan kanssa. Asiakas vaatii tarkkuuden
$\varepsilon$, ja insinöörin on kerrottava, kuinka tarkasti syöte on
asetettava ($\delta$), jotta vaatimus täyttyy. Lineaariselle funktiolle
vastaus on suora: koska $|3x + 1 - 7| = 3|x - 2|$, kelpaa
$\delta = \varepsilon / 3$.

```{.python tiedosto="esimerkit/02-raja-arvo.py" osa="epsilon"}
```

Käytännössä raja-arvot lasketaan sääntöjen avulla eikä määritelmästä.
SymPyn `limit` tuntee säännöt ja erikoistapaukset. Toinen argumentti on
muuttuja ja kolmas kohta; ääretön kirjoitetaan `sp.oo`.

```{.python tiedosto="esimerkit/02-raja-arvo.py" osa="perus"}
```

Ensimmäinen ja toinen raja-arvo ovat muotoa $\frac00$. Toisessa muoto
katoaa sieventämällä: $\frac{x^2 - 4}{x - 2} = x + 2$, kun $x \ne 2$.
Kolmas on Neperin luvun $e$ määritelmä, ja neljännessä äärettömyydessä
ratkaisevat korkeimman asteen termit: $\frac{3x^2}{x^2} = 3$.

## Toispuoleiset raja-arvot

Raja-arvo voi riippua siitä, kummalta puolelta kohtaa lähestytään.
**Vasemmanpuoleinen** raja-arvo $\lim_{x \to a^-}$ lähestyy pienemmistä
arvoista ja **oikeanpuoleinen** $\lim_{x \to a^+}$ suuremmista. SymPyssä
suunta annetaan neljäntenä argumenttina `"-"` tai `"+"`. Raja-arvo on
olemassa vain, jos molemmat toispuoleiset raja-arvot ovat olemassa ja
yhtä suuret.

```{.python tiedosto="esimerkit/02-raja-arvo.py" osa="toispuoleinen"}
```

Funktio $1/x$ karkaa nollan molemmin puolin eri äärettömyyksiin, ja
$|x|/x$ on etumerkkifunktio, joka hyppää arvosta $-1$ arvoon $1$.
Kummallakaan ei ole raja-arvoa nollassa. Jos SymPyltä kysyy raja-arvoa
ilman suuntaa, se laskee oletuksena oikeanpuoleisen raja-arvon: kysymys
`limit(1/x, x, 0)` antaa vastauksen `oo`, vaikka raja-arvoa ei ole.
Kaksipuolinen raja-arvo pyydetään suunnalla `"+-"`. Jos puolet eroavat,
SymPy nostaa poikkeuksen tai palauttaa funktiolle $1/x$ arvon `zoo`
(suunnaton ääretön), joten tulos on silti luettava ajatuksella.

## l'Hôpitalin sääntö

Kun raja-arvo on muotoa $\frac00$ tai $\frac\infty\infty$ ja funktiot
ovat derivoituvia, **l'Hôpitalin sääntö** sanoo, että

$$\lim_{x \to a} \frac{f(x)}{g(x)} = \lim_{x \to a} \frac{f'(x)}{g'(x)},$$

kunhan oikea puoli on olemassa. Sääntöä voi soveltaa toistuvasti.
Lausekkeessa $\frac{e^x - 1 - x}{x^2}$ ensimmäinen derivointi antaa
uudelleen muodon $\frac00$, ja vasta toinen ratkaisee raja-arvon.
Derivaatat lasketaan luvussa 3; tässä riittää, että `sp.diff` laskee ne.

```{.python tiedosto="esimerkit/02-raja-arvo.py" osa="lhopital"}
```

```{.tuloste tiedosto="esimerkit/02-raja-arvo.odotettu"}
```

l'Hôpital ei ole taikasana. Ennen sen käyttöä on tarkistettava, että
muoto todella on $\frac00$ tai $\frac\infty\infty$: esimerkiksi
$\frac{x + 1}{x}$, kun $x \to 1$, ei ole, ja derivaattojen suhde $1/1$
antaisi väärän vastauksen 1 oikean arvon 2 sijaan.

## Numeerisen raja-arvon sudenkuopat

Raja-arvoa on houkuttelevaa arvioida laskemalla funktion arvoja yhä
lähempänä kohtaa. Liukuluvuilla kokeilu pettää kahdella tavalla.

**Kumoutuminen.** Lauseke $\frac{1 - \cos x}{x^2}$ lähestyy arvoa
$\tfrac12$. Kun $x$ on pieni, $\cos x$ on hyvin lähellä ykköstä, ja
vähennyslaskussa $1 - \cos x$ merkitsevät numerot kumoutuvat: jäljelle
jää pelkkää pyöristysvirhettä. Kun $x = 10^{-9}$, $\cos x$ pyöristyy
tasan ykköseksi ja tulos on nolla. Korjaus on muuttaa lauseke muotoon,
jossa vähennyslaskua ei ole. Kaavalla $1 - \cos x = 2\sin^2(x/2)$
tulos pysyy tarkkana.

```{.python tiedosto="esimerkit/02-liukuluvut.py" osa="kumoutuminen"}
```

**Pyöristys.** Lausekkeessa $(1 + 1/n)^n$ termi $1/n$ katoaa ykkösen
pyöristykseen, kun $n$ on suuri: liukuluvulla on noin 16 merkitsevää
numeroa, joten $1 + 10^{-16}$ on tasan 1, ja $1^n = 1$. Jo arvolla
$n = 10^{12}$ tulos on pielessä neljännessä desimaalissa. Pythonin
`math.log1p(t)` laskee $\ln(1 + t)$ tarkasti pienillä $t$:n arvoilla,
ja sen avulla lauseke saadaan tarkaksi.

```{.python tiedosto="esimerkit/02-liukuluvut.py" osa="e"}
```

```{.tuloste tiedosto="esimerkit/02-liukuluvut.odotettu"}
```

Liukulukujen esitys ja pyöristys käsitellään perusteellisesti taidossa
*Miten tietokone laskee*. Tässä riittää nyrkkisääntö: numeerinen
raja-arvon arvaus on kokeilu, ei todistus, ja kahden lähes yhtä suuren
luvun erotus on epäilyttävä.

## Jatkuvuus

Funktio $f$ on **jatkuva** kohdassa $a$, jos

$$\lim_{x \to a} f(x) = f(a),$$

eli raja-arvo on olemassa, funktio on määritelty kohdassa ja nämä ovat
samat. Alkeisfunktiot (polynomit, rationaalifunktiot, juuret,
eksponentti, logaritmi ja trigonometriset funktiot) ovat jatkuvia
määrittelyjoukossaan. Tarkistettavaa jää paloittain määriteltyjen
funktioiden rajakohdissa ja kohdissa, joissa lauseke ei ole määritelty.

Esimerkissä lämmittimen teho pienenee lineaarisesti ja on nolla
20 asteesta ylöspäin. Kirjoitusvirheellisessä versiossa teho hyppää
rajakohdassa 10 wattiin, mikä säätöpiirissä aiheuttaisi värähtelyä
rajan molemmin puolin. Funktio laskee kunkin palan toispuoleisen
raja-arvon erikseen.

```{.python tiedosto="esimerkit/02-jatkuvuus.py" osa="jatkuva"}
```

**Poistuva epäjatkuvuus** on kohta, jossa funktio ei ole määritelty mutta
raja-arvo on olemassa. Kun funktion arvoksi määritellään raja-arvo,
funktiosta tulee jatkuva. Signaalinkäsittelyn **sinc-funktio**
$\operatorname{sinc} x = \frac{\sin x}{x}$ ($\operatorname{sinc} 0 = 1$)
on tällainen.

```{.python tiedosto="esimerkit/02-jatkuvuus.py" osa="poistuva"}
```

```{.tuloste tiedosto="esimerkit/02-jatkuvuus.odotettu"}
```

Jatkuvuudella on käytännön seurauksia. **Bolzanon lause** takaa, että
jatkuva funktio, joka on välin päätepisteissä erimerkkinen, saa
välillä arvon nolla. Puolitushaku ja SciPyn `brentq` nojaavat siihen.
**Weierstrassin lause** takaa, että jatkuva funktio saa suljetulla
välillä suurimman ja pienimmän arvonsa, mikä tekee luvun 4 ääriarvotehtävistä
ratkeavia.

## Samat laskut Maximalla

Maximassa raja-arvo lasketaan funktiolla `limit`. Ääretön on `inf` ja
miinus ääretön `minf`, ja suunta annetaan sanoilla `plus` ja `minus`.

```{.maxima tiedosto="esimerkit/maxima/02-raja-arvo.mac" osa="raja"}
```

```{.tuloste tiedosto="esimerkit/maxima/02-raja-arvo.odotettu"}
```

## Käytännössä

- **Tarkista muoto ennen sääntöä.** l'Hôpital ja muut keinot koskevat
  vain epämääräisiä muotoja. Sijoita kohta ensin ja katso, mitä saat.
- **Toispuoleiset raja-arvot erikseen.** Paloittain määritellyissä
  funktioissa ja itseisarvoissa raja-arvo voi olla eri suunnista eri.
  Testaa rajakohdat erikseen myös ohjelmakoodissa, koska `<` ja `<=`
  menevät helposti sekaisin.
- **Epäile vähennyslaskua.** Kahden lähes yhtä suuren liukuluvun erotus
  hävittää merkitseviä numeroita. Kirjastot tarjoavat tarkkoja
  muunnelmia, kuten `log1p`, `expm1` ja `hypot`.
- **Numeerinen kokeilu ei ole todistus.** Taulukko arvoista antaa
  aavistuksen, mutta symbolinen lasku tai epäyhtälöarvio ratkaisee.
- **Jatkuvuus on oletus monessa algoritmissa.** Juurenhaku ja
  optimointi olettavat jatkuvuuden; epäjatkuvassa kohdassa ne voivat
  palauttaa järjettömän tuloksen ilman virheilmoitusta.

## Itsearviointi

- Osaat selittää raja-arvon epsilon–delta-määritelmän omin sanoin ja
  löytää $\delta$:n lineaariselle funktiolle.
- Osaat laskea raja-arvoja, toispuoleisia raja-arvoja ja raja-arvoja
  äärettömyydessä SymPyllä ja Maximalla.
- Osaat soveltaa l'Hôpitalin sääntöä ja tarkistaa sen ehdot.
- Osaat tunnistaa kumoutumisen numeerisessa raja-arvossa ja kirjoittaa
  lausekkeen tarkkaan muotoon.
- Osaat tutkia paloittain määritellyn funktion jatkuvuuden
  toispuoleisilla raja-arvoilla.
