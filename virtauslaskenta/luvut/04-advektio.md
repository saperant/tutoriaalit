# Advektio

Advektio on pelkkää siirtymistä: virtaus kuljettaa pitoisuusjakaumaa
muuttamatta sen muotoa. Yhtälö on yksinkertaisin mahdollinen, ja silti
sen diskretointi on virtauslaskennan vanhin vaikeus. Tässä luvussa
kokeillaan neljää tapaa ja nähdään, että tarjolla on kolme huonoa
ominaisuutta, joista on valittava: epästabiilius, leviäminen tai
heilahtelu. Luvun lopussa rajoitin yhdistää kaksi kaaviota niin, että
pahimmat puolet jäävät pois.

## Koetehtävä

Yhdessä ulottuvuudessa ja vakionopeudella $u > 0$ kuljetusyhtälö ilman
diffuusiota on

$$\frac{\partial c}{\partial t} + u\,\frac{\partial c}{\partial x} = 0,
  \qquad\text{ratkaisu}\quad c(x, t) = c_0(x - ut).$$

Alkutila siirtyy nopeudella $u$ sellaisenaan. Koetehtävässä alue on
jaksollinen, joten yhden kierroksen jälkeen tarkka ratkaisu on sama kuin
alkutila ja kaikki ero siihen on kaavion virhettä. Alkutilassa on sileä
kumpu ja jyrkkäreunainen porras, koska kaaviot kohtelevat niitä eri
tavoin.

Kaikki kaaviot ovat säilyvässä muodossa. Ruudun uusi arvo on vanha
arvo miinus oikean ja vasemman pinnan voiden erotus, ja kaaviot eroavat
vain siinä, miten pinnan arvo arvioidaan. Aika-askelta mittaa
**Courantin luku** $C = u\,\Delta t/h$: kuinka monta ruutua virtaus
kulkee askeleessa.

```{.python tiedosto="esimerkit/04-advektio.py" osa="vuot"}
```

```{.python tiedosto="esimerkit/04-advektio.py" osa="kierros"}
```

```{.tuloste tiedosto="esimerkit/04-advektio.odotettu" rivit="1-5"}
```

![Kumpu ja porras yhden kierroksen jälkeen (ruskea) ja tarkka ratkaisu
(harmaa). Keskeisdifferenssi on pysäytetty 40 askeleen jälkeen, ennen
kuin heilahtelu peittää kaiken.](kuvat/advektio.png){width=95%}

Aineen määrä säilyy kaikissa kaavioissa, kuten säilyvältä muodolta
sopii odottaa. Muu vaihtelee.

## Keskeisdifferenssi: aina epästabiili

Luontevin arvio pinnan arvolle on naapurien keskiarvo. Se on toista
kertalukua ja toimi diffuusiolle moitteetta. Advektiolle se yhdessä
Eulerin aika-askeleen kanssa hajoaa aina, kuinka pieni askel tahansa
valitaan. Stabiilisuusanalyysi antaa aallolle, jonka aaltoluku on $k$,
kasvukertoimen

$$|G|^2 = 1 + C^2 \sin^2(kh) > 1,$$

joten jokainen aalto kasvaa joka askeleella.

Syy on fysikaalinen. Advektiossa tieto kulkee vain virtauksen suuntaan:
pisteen tuleva arvo riippuu siitä, mitä vastavirran puolella on.
Keskiarvo antaa myötävirran puolelle saman painon, ja kaavio reagoi
tietoon, jota pisteeseen ei koskaan saavu.

Keskeisdifferenssi ei silti ole käyttökelvoton. Se toimii, kun mukana on
riittävästi diffuusiota (luku 5) tai kun aika-askel on parempi kuin
Eulerin (luku 7). Yksinään näin käytettynä se ei toimi.

## Vastavirtakaavio ja numeerinen diffuusio

**Vastavirtakaavio** (*upwind*) ottaa pinnan arvon siitä ruudusta, josta
virtaus tulee. Se on stabiili, kun $C \le 1$, eli kun virtaus kulkee
askeleessa enintään yhden ruudun. Tämä on sama CFL-ehto kuin aalloilla,
ja peruste on sama: kaavion riippuvuusalueen on katettava yhtälön
riippuvuusalue. Lisäksi kaavio on **monotoninen**: uusi arvo on aina
vanhojen arvojen painotettu keskiarvo, joten uusia huippuja tai
negatiivisia pitoisuuksia ei voi syntyä.

Hinta näkyy kuvassa. Kumpu on puolittunut ja porras levinnyt mäeksi.
Leviämisen suuruus selviää, kun kaavioon sijoitetaan Taylorin kehitelmä
ja katsotaan, minkä yhtälön kaavio *tarkalleen ottaen* ratkaisee.
Johtavaan kertalukuun se on

$$\frac{\partial c}{\partial t} + u\,\frac{\partial c}{\partial x}
  = D_\text{num}\,\frac{\partial^2 c}{\partial x^2},
  \qquad D_\text{num} = \frac{u h}{2}\,(1 - C).$$

Vastavirtakaavio ratkaisee siis advektio–diffuusioyhtälön, jonka
diffuusiokerroin riippuu hilasta. Tätä sanotaan **numeeriseksi
diffuusioksi**. Väitteen voi mitata: kapean kummun varianssi kasvaa
diffuusiossa nopeudella $2D$, joten kasvusta saadaan kerroin.

```{.python tiedosto="esimerkit/04-numdiff.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/04-numdiff.odotettu"}
```

![Vastavirtakaavion tulos on sama kuin tarkan advektion ja
diffuusioyhtälön yhdistelmä, kun diffuusiokertoimeksi valitaan kaavan
antama numeerinen diffuusio.](kuvat/numdiff.png){width=70%}

Mitattu kerroin on sama kuin kaavan ennustama. Kolme havaintoa:

- Numeerinen diffuusio on verrannollinen ruudun kokoon. Se pienenee
  hilaa tihentämällä, mutta vain ensimmäisessä kertaluvussa: puolet
  virheestä maksaa kaksinkertaisen hilan.
- Arvolla $C = 1$ se häviää ja kaavio on tarkka, koska ruudun sisältö
  siirtyy askeleessa täsmälleen naapuriin. Todellisessa virtauksessa
  nopeus vaihtelee paikasta toiseen, joten tätä ei voi käyttää hyväksi.
- Ilmassa aineiden diffuusiokerroin on luokkaa $10^{-5}$ m²/s. Jos tuuli
  on 1 m/s ja ruutu senttimetrin, numeerinen diffuusio on
  $5 \cdot 10^{-3}$ m²/s eli satoja kertoja fysikaalista suurempi.
  Tulos kuvaa silloin hilaa, ei ilmaa.

## Toinen kertaluku ja heilahtelut

**Lax–Wendroffin kaavio** lisää vastavirta-arvoon korjauksen, joka
kumoaa numeerisen diffuusion johtavan termin. Kaavio on toista
kertalukua sekä ajassa että paikassa, ja sileä kumpu säilyy kuvassa
selvästi paremmin. Portaan kohdalla tulos on kuitenkin pahempi kuin
vastavirralla: pitoisuus käy arvossa $-0{,}21$ ja nousee arvoon 1,22.
Negatiivinen pitoisuus ei ole pelkkä kauneusvirhe. Jos suure on
lämpötila, tiheys tai kemiallisen reaktion lähtöaine, negatiivinen arvo
voi kaataa koko laskun.

Tämä ei ole juuri tämän kaavion vika. **Godunovin lause** sanoo, että
lineaarinen kaavio, joka ei luo uusia ääriarvoja, on korkeintaan
ensimmäistä kertalukua. Lineaarisella kaaviolla on siis valittava
leviämisen ja heilahtelun väliltä.

## Rajoittimet

Lauseesta pääsee ohi tekemällä kaaviosta epälineaarisen: kaavio katsoo
ratkaisua ja päättää paikan mukaan, kumpaa menetelmää käyttää.
**Rajoitin** (*flux limiter*) kertoo Lax–Wendroffin korjauksen luvulla
$\psi(r)$, jossa $r$ on peräkkäisten erotusten suhde:

- Sileässä kohdassa peräkkäiset erotukset ovat lähes yhtä suuret,
  $r \approx 1$ ja $\psi \approx 1$: täysi toisen kertaluvun korjaus.
- Ääriarvon tai hypyn kohdalla erotukset ovat erimerkkiset tai hyvin
  erisuuret, ja $\psi$ pienenee kohti nollaa: paikallisesti
  vastavirtakaavio.

Esimerkin rajoitin on van Leerin, $\psi(r) = (r + |r|)/(1 + |r|)$.
Koodissa se on funktio `rajoitettu` luvun alun listauksessa. Tulos on
taulukon paras: ei yli- eikä alituksia, porras pysyy jyrkkänä ja
keskivirhe on neljäsosa vastavirtakaavion virheestä. Hinnan näkee
kummun huipusta, joka on madaltunut. Rajoitin ei voi erottaa aitoa
kapeaa huippua alkavasta heilahtelusta, joten se leikkaa molempia.

Kertaluvut mitataan sileällä alkutilalla:

```{.python tiedosto="esimerkit/04-advektio.py" osa="kertaluku"}
```

```{.tuloste tiedosto="esimerkit/04-advektio.odotettu" alkaen="sileä alkutila"}
```

Vastavirta on ensimmäistä kertalukua, muut toista. Neljälläsadalla
ruudulla vastavirtakaavion virhe on yhä suurempi kuin Lax–Wendroffin
virhe viidelläkymmenellä.

Rajoittimia on kymmeniä (minmod, van Leer, superbee, van Albada), ja ne
eroavat siinä, kuinka rohkeasti ne päästävät korjauksen läpi. Periaate
on kaikissa sama, ja sama ajatus on korkeamman kertaluvun
menetelmissäkin: tarkka kaavio siellä, missä ratkaisu on sileä, ja varma
siellä, missä se ei ole.

## Käytännössä

- **Courantin luku alle yhden.** Eksplisiittisen kaavion aika-askelta
  rajoittaa suurin nopeus ja pienin ruutu. Valmiit ohjelmat säätävät
  askelta itse annetun Courantin luvun mukaan.
- **Ensimmäisen kertaluvun vastavirta on alkuarvaus, ei tulos.** Se on
  vankka ja sopii laskun käynnistämiseen, mutta sen tulos on väärällä
  tavalla sileä ja uskottavan näköinen. Lopullinen tulos lasketaan
  toisen kertaluvun kaaviolla.
- **Rajoitettu toisen kertaluvun kaavio on oletusvalinta** suureille,
  jotka eivät saa heilahdella: pitoisuuksille, lämpötilalle ja
  turbulenssisuureille.
- **Rajatun suureen pitää pysyä rajoissaan.** Jos pitoisuus käy
  negatiivisena tai osuus ylittää yhden, kaavio heilahtelee. Tämä on
  helppo tarkistaa ja kertoo paljon.
- **Epäile sileää tulosta.** Jos jyrkkä rintama levenee matkalla,
  kysymys on, levittääkö sitä fysiikka vai hila. Vastaus selviää
  tihentämällä hilaa: fysikaalinen leveys pysyy, numeerinen kapenee.

## Itsearviointi

- Osaat selittää, miksi keskeisdifferenssi Eulerin aika-askeleella on
  advektiolle epästabiili ja mitä tekemistä tiedon kulkusuunnalla on
  asian kanssa.
- Osaat kirjoittaa vastavirtakaavion, sen stabiilisuusehdon ja
  numeerisen diffuusion kertoimen.
- Osaat mitata kaavion numeerisen diffuusion kummun leviämisestä.
- Osaat kertoa, mitä Godunovin lause sanoo ja miten rajoitin kiertää
  sen.
- Osaat valita advektiokaavion sen mukaan, saako suure heilahdella ja
  kuinka tarkka tulos tarvitaan.
