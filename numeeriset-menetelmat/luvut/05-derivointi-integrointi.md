# Numeerinen derivointi ja integrointi

Taidossa *Differentiaali- ja integraalilaskenta* erotusosamäärä,
puolisuunnikassääntö ja Simpsonin sääntö esiteltiin perusideoina. Tässä
luvussa ne asetetaan yhteiseen kehykseen: jokaisella säännöllä on
**kertaluku**, joka kertoo, kuinka nopeasti virhe pienenee askeleen
mukana, ja virheen voi ennustaa ja mitata. Lisäksi katsotaan, miten
kertaluvun voi nostaa (Richardson ja Gaussin kvadratuuri), miten
laskentatyö sijoitetaan sinne, missä sitä tarvitaan (adaptiivisuus), ja
mitä tehdään, kun integrandi ei ole sileä.

## Derivaatta ja optimaalinen askel

Erotusosamäärän kokonaisvirheessä on kaksi osaa: katkaisuvirhe, joka
pienenee askeleen $h$ mukana, ja pyöristysvirhe noin
$\varepsilon|f|/h$, joka kasvaa. Kun katkaisuvirhe on kertalukua
$h^p$, kokonaisvirhe $C h^p + \varepsilon/h$ on pienin, kun

$$h^* \approx \varepsilon^{1/(p+1)}, \qquad
\text{virhe} \approx \varepsilon^{p/(p+1)}.$$

Eteenpäin-erotukselle ($p = 1$) paras askel on noin
$\sqrt\varepsilon \approx 10^{-8}$, ja tarkkuutta jää noin kahdeksan
numeroa. Keskeiselle erotukselle ($p = 2$) paras askel on
$\varepsilon^{1/3} \approx 6 \cdot 10^{-6}$ ja tarkkuutta noin 11
numeroa.

**Richardsonin ekstrapolaatio** nostaa kertalukua yhdistelemällä
tuloksia eri askeleilla. Jos $D(h) = f' + Ch^2 + O(h^4)$, niin
$(4D(h/2) - D(h))/3$ kumoaa $h^2$-termin ja on kertalukua 4. Sama ajatus
toimii kaikille menetelmille, joiden virheen muoto tunnetaan, ja se on
integroinnin Rombergin menetelmän perusta.

**Kompleksiaskel** on kaunis temppu analyyttisille funktioille. Taylorin
kehitelmästä imaginaarisuuntaan saadaan
$f(x + ih) = f(x) + ihf'(x) - h^2 f''(x)/2 + \ldots$, joten
$f'(x) \approx \operatorname{Im} f(x + ih)/h$. Kaavassa ei ole
vähennyslaskua, joten pyöristysvirhe ei kasva, ja askeleeksi kelpaa
vaikkapa $10^{-100}$.

```{.python tiedosto="esimerkit/05-derivaatta.py" osa="kaavat"}
```

```{.python tiedosto="esimerkit/05-derivaatta.py" osa="paras"}
```

```{.tuloste tiedosto="esimerkit/05-derivaatta.odotettu"}
```

![Erotusosamäärien virhe askeleen funktiona. Oikealla katkaisuvirhe
pienenee kertaluvun mukaisella kulmakertoimella, vasemmalla
pyöristysvirhe kasvaa kuten $1/h$.](kuvat/derivaatta.png){width=62%}

Mitatut parhaat askeleet ja virheet osuvat teoreettisiin arvioihin.
Kompleksiaskel antaa derivaatan konetarkkuudella, mutta vaatii, että
funktion voi laskea kompleksiluvuilla. Tuotantokoodissa derivaatat
lasketaan usein **automaattisella derivoinnilla** (esimerkiksi JAX,
PyTorch, CasADi), joka soveltaa ketjusääntöä ohjelman jokaiseen
laskutoimitukseen ja antaa tarkan derivaatan ilman askelta.

## Integrointisääntöjen kertaluvut

Tasavälisen **puolisuunnikassäännön** virhe on $O(h^2)$ ja
**Simpsonin säännön** $O(h^4)$. Kun funktion arvojen määrä
kaksinkertaistetaan, virhe pienenee siis 4- tai 16-kertaiseksi.
**Gaussin kvadratuuri** valitsee sekä pisteet että painot niin, että
$n$ pisteen sääntö integroi tarkasti kaikki polynomit astetta $2n-1$
asti. Pisteet ovat Legendren polynomin nollakohdat, samaan tapaan kuin
Tšebyšovin solmut luvussa 4.

```{.python tiedosto="esimerkit/05-kertaluvut.py" osa="saannot"}
```

```{.python tiedosto="esimerkit/05-kertaluvut.py" osa="kertaluvut"}
```

```{.tuloste tiedosto="esimerkit/05-kertaluvut.odotettu"}
```

![Integrointisääntöjen virhe funktion arvojen määrän funktiona
logaritmisella asteikolla. Gaussin kvadratuuri saavuttaa
konetarkkuuden kuudella arvolla.](kuvat/integrointi.png){width=62%}

Suhteet 4,0 ja 16,0 vahvistavat kertaluvut 2 ja 4. Gaussin kuuden
pisteen sääntö on tarkempi kuin Simpsonin sääntö 33 pisteellä, koska
sen virhe pienenee eksponentiaalisesti sileälle funktiolle. Siksi
Gaussin säännöt ovat kirjastojen adaptiivisten integraattorien ydin.

Tasavälisellä datalla on yksi tärkeä poikkeus: **jaksollisen
funktion integraali yhden jakson yli** on puolisuunnikassäännöllä
eksponentiaalisen tarkka, koska Euler–Maclaurinin virhetermit
kumoutuvat. Siksi DFT (taito *Kompleksiluvut ja Fourier-analyysi*)
laskee Fourier-kertoimet niin tarkasti.

## Adaptiivinen integrointi

Tasavälinen sääntö tuhlaa pisteitä sinne, missä funktio on loiva, ja
pistetiheys voi silti olla liian pieni siellä, missä funktio muuttuu
nopeasti. **Adaptiivinen** sääntö arvioi virheen kullakin osavälillä
ja jakaa vain ne välit, joilla arvio on liian suuri. Virhearvio saadaan
vertaamalla saman välin kahta sääntöä: koko välin Simpsonia ja kahden
puolikkaan Simpsonia. Niiden erotus on noin 15 kertaa tarkemman tuloksen
virhe, sillä Simpsonin säännön virhe pienenee puolitettaessa
16-kertaiseksi.

```{.python tiedosto="esimerkit/05-adaptiivinen.py" osa="adaptiivinen"}
```

```{.python tiedosto="esimerkit/05-adaptiivinen.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/05-adaptiivinen.odotettu"}
```

Samalla määrällä funktion arvoja adaptiivinen Simpson on 100 000 kertaa
tarkempi kuin tasavälinen. SciPyn `quad` (QUADPACK-kirjaston QAGS)
käyttää adaptiivisesti **Gaussin–Kronrodin** sääntöparia: 21 pisteen
Kronrodin sääntö sisältää 10 pisteen Gaussin säännön pisteet, joten
virhearvio saadaan ilman ylimääräisiä arvoja. Se saavuttaa
konetarkkuuden kahdeksasosalla arvoista. Lisäksi `quad` palauttaa oman
virhearvionsa, joka on yleensä varovainen.

## Singulariteetit

Integrandi $1/\sqrt x$ on äärettömän suuri pisteessä $x = 0$, mutta
integraali välillä $[0, 1]$ on äärellinen (2). Puolisuunnikassääntö ei
pysty edes laskemaan arvoa päätepisteessä. Keskipistesääntö välttää
päätepisteen, mutta suppenee hitaasti:

```{.python tiedosto="esimerkit/05-singulariteetti.py" osa="keskipiste"}
```

Virhe pienenee vain kuten $h^{1/2}$: sata kertaa enemmän pisteitä antaa
yhden lisänumeron. Kertaluvut pätevät vain sileille funktioille, ja
singulariteetti romuttaa ne. Parhaat korjauskeinot ovat:

1. **Muuttujanvaihto**, joka poistaa singulariteetin. Sijoitus
   $x = t^2$ muuttaa integrandin vakioksi.
2. **Painofunktio**: kirjastolle kerrotaan singulariteetin muoto, ja
   se käyttää siihen räätälöityä sääntöä.
3. **Välin jakaminen** singulariteetin tai epäjatkuvuuskohdan kohdalta
   (`quad`-funktion `points`-parametri).

```{.python tiedosto="esimerkit/05-singulariteetti.py" osa="sijoitus"}
```

```{.python tiedosto="esimerkit/05-singulariteetti.py" osa="quad"}
```

```{.tuloste tiedosto="esimerkit/05-singulariteetti.odotettu"}
```

`quad` selviää päätepisteen singulariteetista, koska Gaussin säännön
pisteet eivät osu päätepisteisiin ja adaptiivinen jako tihentää pisteitä
nollan lähellä, ja sen sisäinen ekstrapolointi (Wynnin
epsilon-algoritmi) kiihdyttää suppenemista. Integraalit äärettömän
välin yli lasketaan samalla tavalla muuttujanvaihdolla, jonka `quad`
tekee automaattisesti, kun rajana on `np.inf`.

## Sama Octavella

```{.octave tiedosto="esimerkit/octave/05-integraali.m"}
```

```{.tuloste tiedosto="esimerkit/octave/05-integraali.odotettu"}
```

Octaven `integral` ja `quadgk` ovat adaptiivisia Gaussin–Kronrodin
integraattoreita. `trapz` integroi taulukoidun datan
puolisuunnikassäännöllä.

## Käytännössä

- **Valitse erotusosamäärän askel kertaluvun mukaan.** Keskeiselle
  erotukselle $h \approx \varepsilon^{1/3}|x|$ on hyvä lähtökohta.
  Skaalaa askel argumentin suuruuden mukaan.
- **Derivoi analyyttisesti tai automaattisesti, kun voit.**
  Erotusosamäärä on varakeino ja tarkistusväline, ei ensisijainen
  menetelmä.
- **Funktiolle `quad`, datalle `trapezoid` tai `simpson`.** Kun
  funktion voi laskea missä tahansa, adaptiivinen kirjastorutiini on
  lähes aina paras valinta.
- **Lue kirjaston virhearvio ja varoitukset.** `quad` varoittaa, jos
  se ei saavuttanut tarkkuutta; älä vaimenna varoitusta tutkimatta
  syytä.
- **Kerro singulariteetit ja epäjatkuvuudet kirjastolle.** Jaa väli
  hyppykohdista, käytä painofunktioita tai tee muuttujanvaihto.
- **Tarkista kertaluku puolittamalla askel.** Jos virhe ei pienene
  odotetusti, funktio ei ole niin sileä kuin luulit, tai koodissa on
  virhe.

## Itsearviointi

- Osaat johtaa erotusosamäärän optimaalisen askeleen ja virheen
  katkaisu- ja pyöristysvirheen tasapainosta.
- Osaat käyttää Richardsonin ekstrapolaatiota ja kompleksiaskelta.
- Osaat mitata integrointisäännön kertaluvun ja selittää, miksi Gaussin
  kvadratuuri on niin tarkka.
- Osaat selittää adaptiivisen integroinnin virhearvion ja milloin
  adaptiivisuus kannattaa.
- Osaat tunnistaa singulaarisen integrandin ja käsitellä sen
  muuttujanvaihdolla, painofunktiolla tai välin jaolla.
