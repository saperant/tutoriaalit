# Kitka

Ilman kitkaa mikään ei pysy rinteessä, pallo ei lähde vierimään eikä
pino kestä tönäisyä. Kitka on kosketuksen toinen puoli: normaalivoima
estää kappaleita menemästä sisäkkäin, ja kitka vastustaa niiden
liukumista toistensa pintaa pitkin. Tässä luvussa kitka lisätään
moottoriin ja tulos tarkistetaan kolmella kaavalla lukion fysiikasta.

## Coulombin malli

Peleissä käytetään Coulombin kitkamallia, jossa on yksi sääntö:
kitkavoiman suuruus on enintään kitkakerroin $\mu$ kertaa
normaalivoima,

$$|\mathbf F_t| \le \mu\,F_n.$$

Säännöstä seuraa kaksi tilaa. *Lepokitkassa* kitka on juuri niin
suuri, että liukumista ei synny, ja pienempi kuin raja. *Liukukitkassa*
raja on saavutettu, kitka on suurimmillaan ja osoittaa liukumissuuntaa
vastaan. Todellisilla materiaaleilla lepo- ja liukukitkan kertoimet
eroavat hieman, mutta useimmat moottorit käyttävät yhtä kerrointa.

Impulsseina sama sääntö on: kosketuspisteen sivuttainen suhteellinen
nopeus yritetään viedä nollaan, mutta kitkaimpulssi saa olla enintään
$\mu$ kertaa saman pisteen normaali-impulssi. Ratkaisija toteuttaa
tämän rajaamalla (*clamp*):

```{.cpp tiedosto="esimerkit/yhteinen/ratkaisija.hpp" osa="kitka"}
```

Rajaus koskee *kertynyttä* impulssia `jt1`, ei yhden kierroksen
lisäystä. Syy selitetään seuraavassa luvussa; tässä riittää, että
`jn` on pisteen normaali-impulssi ja `raja` sen mukainen kitkan
enimmäisarvo.

## Kitkakartio ja sen likiarvo

Sääntö $|\mathbf F_t| \le \mu F_n$ rajaa kitkavoiman ympyrän sisään
kosketustasossa. Kun mukaan otetaan normaalivoima, sallitut
kokonaisvoimat muodostavat kartion, *kitkakartion*.

Ympyräehto kytkee kaksi tangenttisuuntaa toisiinsa, mikä on
iteratiiviselle ratkaisijalle hankalaa. Yleinen likiarvo ratkaisee
kaksi kohtisuoraa tangenttisuuntaa erikseen ja rajaa kummankin
välille $\pm\mu F_n$. Ympyrästä tulee neliö ja kartiosta pyramidi.

```{.cpp tiedosto="esimerkit/yhteinen/ratkaisija.hpp" osa="tangentit"}
```

![Periaatekuva: kitkavoiman sallittu alue kosketustasossa. Kaksi
erikseen rajattua akselia antaa neliön, jonka kulmissa kitka on √2
kertaa liian suuri. Sisään piirretty neliö on aina kartion sisällä
mutta liian heikko akselien suunnassa.](kuvat/kitkakartio.png){width=42%}

Likiarvon virhe näkyy mittauksessa. Laatikko pannaan liukumaan ensin
tangenttiakselin suuntaan ja sitten vinottain:

```{.cpp tiedosto="esimerkit/06-kitka.cpp" osa="liuku"}
```

```{.tuloste tiedosto="esimerkit/06-kitka.odotettu" alkaen="liukumatka" asti="vinottain"}
```

Akselin suunnassa jarrutusmatka on lähellä kaavan $v^2 / (2\mu g)$
arvoa. Vinottain laatikko pysähtyy lyhyemmällä matkalla, koska
kumpikin akseli jarruttaa täydellä voimalla ja yhteensä kitkaa on
$\sqrt2$ kertaa liikaa. Useimmissa peleissä ero ei haittaa. Jos se
haittaa, tangentit valitaan liukumissuunnan mukaan tai kaksi
impulssia rajataan yhdessä ympyrään.

## Kalteva taso

Kaltevalla tasolla lepokitka riittää pitämään kappaleen paikallaan,
kun $\tan\theta \le \mu$. Jyrkemmässä rinteessä kappale liukuu
kiihtyvyydellä $g(\sin\theta - \mu\cos\theta)$.

```{.cpp tiedosto="esimerkit/06-kitka.cpp" osa="rinne"}
```

```{.tuloste tiedosto="esimerkit/06-kitka.odotettu" rivit="1-5"}
```

Kummassakin tilassa simulaatio osuu kaavaan kahden desimaalin
tarkkuudella. Lepokitka ei vaadi omaa koodiaan: kun rajaus ei osu
rajaan, impulssi on juuri se, joka pysäyttää liukumisen.

## Liukumisesta vierimiseen

Kolmas koe yhdistää kitkan ja pyörimisen. Pallo lähtee liukumaan
lattiaa pitkin pyörimättä. Kitka vaikuttaa kosketuspisteessä
liikesuuntaa vastaan: se hidastaa etenemistä ja samalla kiihdyttää
pyörimistä. Kun kehänopeus $\omega r$ saavuttaa etenemisnopeuden,
kosketuspiste ei enää liu'u, kitka lakkaa ja pallo vierii. Tasaiselle
pallolle loppunopeus on $\tfrac57 v_0$ kitkakertoimesta riippumatta.

```{.cpp tiedosto="esimerkit/06-kitka.cpp" osa="pallo"}
```

```{.tuloste tiedosto="esimerkit/06-kitka.odotettu" alkaen="t = 0.0 s"}
```

![Liukuva pallo alkaa vieriä: etenemisnopeus laskee ja kehänopeus
nousee suoraviivaisesti, kunnes ne kohtaavat arvossa 5/7 · 7 m/s = 5
m/s.](kuvat/kitka.png){width=60%}

Tulos $\tfrac57$ on hyvä testi, koska siihen tarvitaan kaikki tähän
asti rakennettu: pisteen nopeus, hitausmomentti, impulssin
vääntövaikutus ja kitkan raja. Jos yksikin on väärin, loppunopeus on
jokin muu.

Vierivä pallo ei tässä mallissa pysähdy koskaan. *Vierimisvastus*
johtuu pinnan ja pallon muodonmuutoksesta, jota jäykkä kappale ei
mallinna. Moottorit lisäävät sen erillisenä kulmanopeuden
vaimennuksena.

## Käytännössä

- **Kitka riippuu normaali-impulssista.** Kitka ratkaistaan samassa
  ratkaisijassa kuin normaalit, ja sen raja päivittyy joka
  kierroksella. Kevyesti koskettava kappale liukuu helpommin kuin
  raskaasti painava.
- **Kahden materiaalin kerroin** yhdistetään säännöllä, tavallisesti
  geometrisella keskiarvolla $\sqrt{\mu_a\mu_b}$: jää on liukasta
  kaikkea vastaan.
- **Pyramidi on oletus.** Kartion likiarvo kahdella akselilla on
  halpa, ja virhe on suunnasta riippuva jarrutusmatka. Ajopeleissä,
  joissa renkaan pito ratkaisee, kitka mallinnetaan erikseen.
- **Kitka ja pyöriminen kosketuspisteen ympäri.** Pistekosketus ei
  vastusta pyörimistä normaalin ympäri, joten yhden pisteen varassa
  seisova kappale pyörii paikallaan loputtomasti. Useampi piste
  tuottaa vastuksen itsestään; yhdelle pisteelle moottorit lisäävät
  erillisen kiertokitkan.
- **Hinta:** kitka kolminkertaistaa ratkaistavien rivien määrän: yksi
  normaali ja kaksi tangenttia pistettä kohden.

## Itsearviointi

- Osaat esittää Coulombin kitkan ehtona impulsseille ja erottaa lepo-
  ja liukukitkan.
- Osaat selittää, mitä kitkakartio tarkoittaa ja mikä virhe syntyy,
  kun se korvataan pyramidilla.
- Osaat tarkistaa kitkan toteutuksen kaltevan tason ja vierivän pallon
  kaavoilla.
- Osaat kertoa, miksi vierimisvastus ja kiertokitka on lisättävä
  erikseen.
