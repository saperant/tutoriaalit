# Stokastinen pyöristys

Pyöristys lähimpään on yksittäiselle laskulle paras mahdollinen: virhe
on enintään puoli porrasta. Se on kuitenkin *deterministinen*. Sama
syöte pyöristyy aina samaan suuntaan, ja kun sama tilanne toistuu,
sama virhe toistuu. Luvun 6 kello pysähtyi, koska millisekunnin lisäys
pyöristyi joka kerta alas. Luvun 7 naiivi summa ajautui sivuun samasta
syystä. Matalan tarkkuuden muodoissa (luku 8) porras on suuri, joten
ilmiö tulee vastaan nopeasti.

*Stokastinen pyöristys* (stochastic rounding) valitsee pyöristyssuunnan
satunnaisesti niin, että tulos on *keskimäärin* oikea. Yksittäinen
tulos on huonompi kuin lähimpään pyöristetty, mutta virheet eivät enää
kerry samaan suuntaan.

## Määritelmä

Luku $x$ on kahden esitettävän luvun välissä. Stokastinen pyöristys
valitsee ylemmän naapurin todennäköisyydellä, joka on $x$:n etäisyys
alemmasta naapurista suhteessa naapurien väliin, ja muuten alemman:

$$P(\text{ylös}) = \frac{x - \lfloor x \rfloor}{\text{väli}}, \qquad
P(\text{alas}) = 1 - P(\text{ylös}).$$

Tässä $\lfloor x \rfloor$ on alempi naapuri. Mitä lähempänä naapuria
luku on, sitä todennäköisemmin se pyöristyy siihen. Esitettävä luku
pysyy aina ennallaan.

![Luku, joka on 0,3 välin päässä alemmasta naapuristaan, pyöristyy alas
70 prosentin ja ylös 30 prosentin todennäköisyydellä. Lähimpään
pyöristys veisi sen aina alas.](kuvat/stokastinen.png){width=72%}

Kiinteän askeleen hilalle, kuten kokonaisluvuille tai kiinteän pilkun
luvuille, toteutus on kolme riviä:

```{.python tiedosto="esimerkit/09-stokastinen.py" osa="maaritelma"}
```

## Harhaton mutta kohiseva

Pyöristyksen odotusarvo on tarkka arvo:
$(1-p) \lfloor x \rfloor + p (\lfloor x \rfloor + \text{väli}) = x$,
kun $p$ on ylöspäin pyöristymisen todennäköisyys. Pyöristys on siis
*harhaton*. Lähimpään pyöristys ei ole: arvo 0,3 pyöristyy aina nollaan,
ja virhe on aina −0,3. Koe 100 000 pyöristyksellä vahvistaa tämän:

```{.python tiedosto="esimerkit/09-stokastinen.py" osa="harhaton"}
```

Harhattomuuden hinta on hajonta. Yksittäisen pyöristyksen virheen
keskihajonta on $\sqrt{p(1-p)}$ väliä, suurimmillaan puoli väliä, kun
luku on naapurien puolivälissä. Pahimmillaan virhe on lähes koko väli,
kaksi kertaa niin suuri kuin lähimpään pyöristyksen.

Hyöty näkyy, kun pyöristyksiä on monta peräkkäin. Summaan lisätään
toistuvasti 0,3 väliä, ja summa pyöristetään jokaisen lisäyksen
jälkeen:

```{.python tiedosto="esimerkit/09-stokastinen.py" osa="kasvu"}
```

Tulosteen ensimmäinen taulukko on harhattomuuskoe ja toinen kertymä.
Virheet ovat välin monikertoja:

```{.tuloste tiedosto="esimerkit/09-stokastinen.odotettu"}
```

Lähimpään pyöristettäessä jokainen lisäys katoaa, ja virhe on koko
summa: se kasvaa suoraan lisäysten määrän $n$ mukana. Stokastisesti
pyöristettäessä virheet ovat riippumattomia ja kumoavat osin toisensa,
joten virheen neliöllinen keskiarvo (rms) kasvaa kuten $\sqrt{n}$.
Viimeinen sarake pysyy vakiona lähellä yhden pyöristyksen hajontaa
0,46. Sama pätee yleisemmin: lähimpään pyöristyksen virherajat kasvavat
pahimmassa tapauksessa kuten $n$, stokastisen pyöristyksen suurella
todennäköisyydellä kuten $\sqrt{n}$ (Connolly ym. 2021).

Lähimpään pyöristyksen virhe ei aina kasva näin nopeasti. Jos
pyöristettävät arvot vaihtelevat, virheet osuvat kumpaankin suuntaan
ja kumoutuvat usein yhtä hyvin. Ongelma on tilanne, jossa ne eivät
vaihtele.

## Pysähtynyt kello käy taas

Luvun 6 kello kasvatti `float`-muuttujaa millisekunnin välein ja
pysähtyi 32 768 sekuntiin. Liukuluvuille stokastinen pyöristys tehdään
samalla periaatteella kuin hilalle. Summa lasketaan ensin leveämmällä
tarkkuudella, ja sen naapurit kohdemuodossa haetaan funktiolla
`nextafterf`:

```{.c tiedosto="esimerkit/09-kello.c" osa="pyoristys"}
```

Satunnaisluvut tulevat pienestä generaattorista, jonka alkutila on
kiinteä:

```{.c tiedosto="esimerkit/09-kello.c" osa="satunnainen"}
```

```{.c tiedosto="esimerkit/09-kello.c" osa="kello"}
```

```{.tuloste tiedosto="esimerkit/09-kello.odotettu"}
```

Kello ei ole tarkka, mutta se käy: vuorokauden jälkeen virhe on
yhdeksän sekuntia eikä viisitoista tuntia. Kun väli on 0,0039 sekuntia,
millisekunnin lisäys pyöristyy ylös noin joka neljännellä kerralla, ja
keskimäärin aika etenee oikeaa vauhtia. Oikea korjaus kellolle on
edelleen kokonaisluku. Esimerkki näyttää, mitä stokastinen pyöristys
tekee silloin, kun leveämpää tyyppiä ei ole.

## Pienet päivitykset

Koneoppimisessa tilanne on juuri tämä. Painoa päivitetään askeleella,
joka on oppimisnopeus kertaa gradientti, ja koulutuksen edetessä askel
pienenee. Kun paino tallennetaan matalalla tarkkuudella, askel jää
jossain vaiheessa portaan puolikasta pienemmäksi. Seuraavassa
esimerkissä yhtä painoa viedään kohti arvoa 0,7, ja paino pyöristetään
kahdeksaan murtobittiin jokaisen askeleen jälkeen:

```{.python tiedosto="esimerkit/09-paivitys.py" osa="paivitys"}
```

```{.tuloste tiedosto="esimerkit/09-paivitys.odotettu"}
```

![Painon kulku neljällä pyöristystavalla. Katkaisu pysähtyy, kun askel
on alle portaan, ja lähimpään pyöristys, kun askel on alle puoli
porrasta. Stokastinen pyöristys seuraa tarkkaa
laskentaa.](kuvat/paivitys.png){width=74%}

Katkaisu ja lähimpään pyöristys pysähtyvät kauas tavoitteesta, eikä
lisäaskelista ole apua. Stokastisesti pyöristetty paino jatkaa perille,
koska pienikin askel siirtää painoa joskus kokonaisen portaan. Kohina
ei myöskään kasva rajatta: lähellä tavoitetta askel on pieni, ja paino
siirtyy enää harvoin.

Tämä havainto teki stokastisesta pyöristyksestä tunnetun. Gupta ym.
(2015) kouluttivat neuroverkkoja 16 bitin kiinteän pilkun luvuilla:
stokastisella pyöristyksellä tulos oli lähes sama kuin 32 bitin
liukuluvuilla, lähimpään pyöristämällä koulutus epäonnistui.

## Toteutus kokonaisluvuilla

Kokonaisluvuilla ja kiinteän pilkun luvuilla stokastinen pyöristys on
halpa. Kun arvosta pudotetaan $k$ alinta bittiä, siihen lisätään ensin
$k$-bittinen tasaisesti jakautunut satunnaisluku. Summa ylittää
seuraavan portaan täsmälleen niin usein kuin määritelmä vaatii:

```{.c tiedosto="esimerkit/09-lfsr.c" osa="pudotus"}
```

Lähimpään pyöristys on sama operaatio vakiolla: siinä lisätään aina
puolikas porras. Laitteistossa satunnaisbitit tuotetaan tavallisesti
takaisinkytketyllä siirtorekisterillä (LFSR), joka on muutama kiikku ja
XOR-portti (taidot *Digitaalitekniikka* ja *RTL-suunnittelu
SystemVerilogilla*):

```{.c tiedosto="esimerkit/09-lfsr.c" osa="lfsr"}
```

Esimerkki pudottaa 12-bittisestä näytteestä neljä bittiä jokaisella
rekisterin tilalla ja laskee tulosten keskiarvon koko jakson yli:

```{.tuloste tiedosto="esimerkit/09-lfsr.odotettu"}
```

Katkaisu ja lähimpään pyöristys antavat aina 18. Stokastisten tulosten
keskiarvo on tarkka arvo 18,1875, vaikka jokainen yksittäinen tulos on
18 tai 19. Äänen ja kuvien käsittelyssä samaa tekniikkaa kutsutaan
nimellä *dither*: pieni kohina ennen kvantisointia muuttaa portaista
johtuvan vääristymän tasaiseksi kohinaksi, ja hitaasti vaihteleva
signaali erottuu portaan kokoa pienemmällä tarkkuudella. Aihe jatkuu
taidoissa *Digitaalinen signaalinkäsittely* ja *Lukujen esitys ja
kiinteän pilkun aritmetiikka*.

Satunnaislukujen laadulla on väliä. LFSR:n peräkkäiset tilat ovat
toistensa siirtoja, joten peräkkäiset satunnaisluvut riippuvat
toisistaan. Jos sama rekisteri ohjaa monta pyöristäjää tai jos
satunnaisbittejä on vähemmän kuin pudotettavia bittejä, pyöristys ei
enää ole harhaton.

## Käyttökohteet ja hinta

Stokastista pyöristystä käytetään siellä, missä tarkkuutta on vähän ja
laskuja paljon:

- **Neuroverkkojen koulutus matalalla tarkkuudella.** Painot ja
  gradientit 16 tai 8 bitin muodoissa. Joissakin
  koneoppimiskiihdyttimissä stokastinen pyöristys on laitteiston
  ominaisuus.
- **Kiinteän pilkun laskenta** sulautetuissa järjestelmissä ja
  signaalinkäsittelyssä, kun kertymä ei saa ajautua.
- **Pitkät simulaatiot matalalla tarkkuudella.** Sää- ja
  ilmastomalleissa sekä differentiaaliyhtälöiden ratkaisijoissa on
  tutkittu, voiko 64 bitin laskennan korvata 16 tai 32 bitillä, kun
  pyöristys on stokastinen (Croci ym. 2022).

Hinnat ovat seuraavat:

- **Kohina.** Yksittäinen tulos on epätarkempi kuin lähimpään
  pyöristetty. Jos laskuja on vähän tai virheet eivät toistu samaan
  suuntaan, stokastinen pyöristys vain huonontaa tulosta.
- **Toistettavuus.** Tulos riippuu satunnaisluvuista. Ajo on
  toistettava vain, jos siemen ja satunnaislukujen kulutusjärjestys on
  kiinnitetty, mikä on rinnakkaisessa laskennassa vaikeaa. Testit
  kirjoitetaan toleranssilla tai kiinteällä siemenellä, kuten tämän
  luvun esimerkit.
- **Satunnaisluvut maksavat.** Jokainen pyöristys tarvitsee
  satunnaisbittejä, ja prosessorien liukulukukäskyt eivät tue
  stokastista pyöristystä: IEEE 754 ei määrittele sitä. Ohjelmistossa
  se on moninkertaisesti hitaampi kuin tavallinen pyöristys.
- **Osa algoritmeista olettaa determinismin.** Kahanin summa ja
  virheettömät muunnokset (luku 7) perustuvat siihen, että pyöristys
  on lähimpään.

## Käytännössä

- **Ensin leveämpi tyyppi tai parempi algoritmi.** Kokonaislukukello,
  `double`-kertymä ja Kahanin summa poistavat ongelman kokonaan.
  Stokastinen pyöristys on keino silloin, kun tarkkuutta ei voi lisätä:
  muisti, kaistanleveys tai laitteisto ei riitä.
- **Tunnista pysähtyvä kertymä.** Jos samaan muuttujaan lisätään
  toistuvasti arvoja, jotka ovat alle puoli porrasta, lähimpään
  pyöristys hukkaa ne kaikki. Vertaa lisäyksen kokoa muuttujan ulp:hen
  tai kiinteän pilkun portaaseen.
- **Pyöristä stokastisesti vain tallennettaessa.** Laske leveämmällä
  tarkkuudella ja pyöristä kerran, kun tulos tallennetaan kapeaan
  muotoon. Välitulosten pyöristäminen lisää kohinaa ilman hyötyä.
- **Riittävästi satunnaisbittejä.** Vähintään yhtä monta kuin
  pudotettavia bittejä, ja eri pyöristäjille riippumattomat lähteet.
- **Kiinnitä siemen.** Tallenna siemen tulosten mukana, jotta ajon voi
  toistaa. Vertaa tuloksia toleranssilla, ei bitti bitiltä.

## Itsearviointi

- Osaat määritellä stokastisen pyöristyksen ja perustella, miksi se on
  harhaton.
- Osaat selittää, miksi lähimpään pyöristys pysähtyy, kun lisäykset ovat
  alle puoli porrasta, ja miksi stokastinen pyöristys ei pysähdy.
- Osaat kertoa, miten kertyvä virhe kasvaa lisäysten määrän mukana
  kummallakin pyöristystavalla.
- Osaat toteuttaa stokastisen pyöristyksen kokonaisluvuille lisäämällä
  satunnaisluvun ennen katkaisua.
- Osaat arvioida, milloin stokastinen pyöristys kannattaa ja mitä se
  maksaa toistettavuudessa ja nopeudessa.
