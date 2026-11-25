# Turbulenssi

Kaikki tähän asti lasketut virtaukset ovat olleet laminaareja:
Reynoldsin luku on ollut enintään satoja. Luvun 2 taulukon arkiset
virtaukset ovat tuhansista kymmeniin miljooniin, ja ne ovat
turbulentteja. Tässä luvussa ei toteuteta turbulenssimallia. Sen sijaan
selvitetään, miksi turbulenssia ei voi vain laskea auki, mitä mallit
tekevät sen sijaan ja mitä ne vaativat hilalta. Nämä ovat ne asiat,
jotka valmiin ohjelman käyttäjän on tiedettävä, jotta mallin valinta ei
jää arvaukseksi.

## Mitä turbulenssi on

Turbulentti virtaus on pyörteinen, kolmiulotteinen ja ajassa
epäsäännöllinen. Sen hetkellinen tila ei toistu eikä ole
ennustettavissa, mutta sen keskiarvot ja muut tilastolliset suureet
ovat vakaita ja toistettavia. Insinööriä kiinnostavat juuri ne:
keskimääräinen vastus, painehäviö ja lämmönsiirto.

Olennaista on mittakaavojen kirjo. Suurimmat pyörteet ovat kappaleen
kokoisia ja ottavat energiansa päävirtauksesta. Ne ovat epästabiileja ja
hajoavat pienemmiksi, jotka hajoavat taas pienemmiksi. Energia valuu
näin suurista pyörteistä pieniin, kunnes pyörteet ovat niin pieniä,
että viskositeetti ehtii muuttaa niiden liikkeen lämmöksi. Tätä sanotaan
**energiakaskadiksi**, ja pienimpien pyörteiden kokoa **Kolmogorovin
mittakaavaksi** $\eta$.

Turbulenssin tärkein käytännön vaikutus on sekoittuminen. Pyörteet
kuljettavat liikemäärää, lämpöä ja aineita poikittain virtaukseen
nähden satoja tai tuhansia kertoja tehokkaammin kuin molekyylien
liike. Siksi turbulentti rajakerros kestää paremmin irtoamatta, kitka
on suurempi ja kahvi sekoittuu lusikalla.

## Suoran simuloinnin hinta

Navier–Stokesin yhtälöt kuvaavat myös turbulenssia. Sitä varten ei
tarvita uutta fysiikkaa, vain hila, joka erottaa pienimmät pyörteet, ja
aika-askel, joka seuraa niitä. Tätä sanotaan **suoraksi simuloinniksi**
(*direct numerical simulation*, DNS). Kolmogorovin mittakaavan suhde
kappaleen kokoon on

$$\frac{\eta}{L} \sim \mathrm{Re}^{-3/4},$$

joten hilapisteitä tarvitaan kolmessa ulottuvuudessa
$\mathrm{Re}^{9/4}$ ja aika-askelia CFL-ehdon vuoksi
$\mathrm{Re}^{3/4}$. Työmäärä kasvaa Reynoldsin luvun kolmannessa
potenssissa.

```{.python tiedosto="esimerkit/11-mittakaavat.py" osa="hinta"}
```

```{.tuloste tiedosto="esimerkit/11-mittakaavat.odotettu"}
```

![Suoran simuloinnin laskenta-aika yhtä läpivirtausta kohden koneella,
joka päivittää miljardi ruutua sekunnissa. Arvio on suuruusluokka:
vakiokertoimet on jätetty pois.](kuvat/hinta.png){width=60%}

Luvut ovat karkeita, ja oikeissa laskuissa tarvitaan lisäksi kymmeniä
läpivirtauksia tilastojen keräämiseen. Johtopäätös ei siitä muutu.
Reynoldsin luvulla kymmenentuhatta suora simulointi mahtuu vielä
työasemaan. Sadallatuhannella se vaatii teratavuja muistia ja viikkoja
aikaa, ja henkilöauton virtaus on kymmenientuhansien vuosien päässä.
Kymmenkertainen Reynoldsin luku maksaa
tuhatkertaisen laskennan, joten koneiden nopeutuminen ei ratkaise
asiaa. Suora simulointi on tutkimuksen työkalu, jolla selvitetään
turbulenssin fysiikkaa ja tuotetaan vertailuaineistoa malleille.

## Kaksi ulottuvuutta ei riitä

Luvun 7 ratkaisijalla voisi laskea onkalovirtauksen Reynoldsin luvulla
sata tuhatta, ja tulos näyttäisi pyörteiseltä ja epäsäännölliseltä.
Turbulenssia se ei olisi. Energiakaskadin mekanismi on pyörteiden
venyminen: pyörre, jota virtaus venyttää akselinsa suuntaan, ohenee ja
kiihtyy. Tasovirtauksessa pyörteiden akselit ovat kohtisuorassa tasoa
vastaan, eikä venymistä ole. Kaksiulotteisessa virtauksessa energia
kulkee päinvastoin kohti suuria pyörteitä, jotka sulautuvat yhä
suuremmiksi.

Kaksiulotteinen lasku on siis pätevä vain, kun virtaus itse on
kaksiulotteinen: laminaari tai keskiarvoistettu. Turbulenssin
auki laskeminen vaatii aina kolme ulottuvuutta.

## Mallinnuksen kolme tasoa

Koska kaikkia mittakaavoja ei voi laskea, osa korvataan mallilla.
Tasoja on kolme, ja ne eroavat siinä, mihin raja vedetään.

| Taso | Mitä lasketaan | Mitä mallinnetaan | Hila ja aika | Käyttö |
|---|---|---|---|---|
| suora simulointi (DNS) | kaikki pyörteet | ei mitään | 3D, ajasta riippuva, $\mathrm{Re}^{9/4}$ pistettä | tutkimus, pienet Re |
| suurten pyörteiden simulointi (LES) | hilaa suuremmat pyörteet | hilaa pienempien vaikutus | 3D, ajasta riippuva, tiheä | palaminen, melu, irtoavat virtaukset |
| keskiarvoistetut yhtälöt (RANS) | vain keskiarvovirtaus | kaikki turbulenssi | 2D tai 3D, usein tasapainotila | valtaosa teollisesta laskennasta |

**RANS** (*Reynolds-averaged Navier–Stokes*) lähtee siitä, että nopeus
jaetaan keskiarvoon ja heilahteluun, $u = \overline u + u'$, ja
yhtälöt keskiarvoistetaan. Advektiotermi on epälineaarinen, joten
keskiarvoistuksessa siitä jää ylimääräinen termi: heilahtelujen
tulojen keskiarvo $\overline{u'v'}$, jota sanotaan **Reynoldsin
jännitykseksi**. Se kuvaa liikemäärää, jota pyörteet kuljettavat.
Yhtälöitä on nyt vähemmän kuin tuntemattomia, ja puuttuva tieto on
tuotava mallilla.

Yleisin oletus on **pyörreviskositeetti**: turbulenssi vaikuttaa
keskiarvovirtaukseen kuin lisäviskositeetti $\nu_t$, joka on
moninkertainen nesteen omaan verrattuna ja vaihtelee paikasta toiseen.
Turbulenssimalli on resepti sen laskemiseen. Kahden yhtälön mallit
($k$–$\varepsilon$, $k$–$\omega$ ja niiden yhdistelmä SST) ratkaisevat
kaksi ylimääräistä kuljetusyhtälöä, turbulenssin liike-energialle ja
sen häviämisnopeudelle, ja laskevat pyörreviskositeetin niistä. Yhtälöt
ovat luvun 3 kuljetusyhtälöitä lähdetermein, ja niihin pätee kaikki
luvuissa 4 ja 5 sanottu.

Malleissa on vakioita, jotka on sovitettu kokeisiin yksinkertaisissa
virtauksissa: putkissa, tasolevyillä ja suihkuissa. Ne toimivat hyvin
seinää myötäilevissä rajakerroksissa ja heikommin siellä, missä virtaus
irtoaa, kiertää tai muuttuu laminaarista turbulentiksi. Mallin
valinta on siis mallinnuspäätös samassa mielessä kuin reunaehto, ja sen
virhe ei pienene hilaa tihentämällä.

**LES** (*large eddy simulation*) laskee suuret, geometriasta riippuvat
pyörteet suoraan ja mallintaa vain hilaa pienemmät, jotka ovat
yleisluontoisempia ja helpompia mallintaa. Se on tarkempi mutta vaatii
aina kolmiulotteisen, ajasta riippuvan laskun tiheällä hilalla ja
pitkän keskiarvoistuksen. Luvun 10 havainto pätee siihen erityisen
ankarasti: numeerinen diffuusio toimii kuin ylimääräinen
pyörreviskositeetti, joten LES tehdään keskeisdifferenssin tapaisilla
vähän vaimentavilla kaavioilla.

## Seinän läheisyys

Turbulentin virtauksen jyrkimmät nopeuden muutokset ovat seinän
vieressä, ja juuri siellä syntyvät kitka ja lämmönsiirto. Seinän
lähellä nopeus ja etäisyys skaalautuvat **kitkanopeudella**
$u_\tau = \sqrt{\tau_w/\rho}$, jossa $\tau_w$ on seinän
leikkausjännitys:

$$u^+ = \frac{u}{u_\tau}, \qquad y^+ = \frac{y\,u_\tau}{\nu}.$$

Näissä yksiköissä nopeusprofiili on lähes sama kaikissa seinää
myötäilevissä turbulenteissa virtauksissa.

![Turbulentin rajakerroksen nopeusprofiili seinäyksiköissä
(periaatekuva). Varjostetut alueet ovat ne kaksi paikkaa, joihin
seinän viereinen ruutu voidaan asettaa.](kuvat/seinalaki.png){width=70%}

Aivan seinän vieressä, kun $y^+ < 5$, pyörteet eivät mahdu liikkumaan
ja viskositeetti hallitsee: $u^+ = y^+$. Kauempana, kun $y^+$ on
kolmestakymmenestä muutamaan sataan, profiili on logaritminen. Hilan
seinän viereisen ruudun $y^+$ ratkaisee, miten seinä käsitellään:

- **Lasketaan seinään asti:** ensimmäinen ruutu on viskoosissa
  alikerroksessa, $y^+ \approx 1$. Tarkin tapa, mutta vaatii hyvin
  ohuet ruudut.
- **Seinäfunktio:** ensimmäinen ruutu on logaritmisella alueella,
  $y^+ \approx 30$–$300$, ja ohjelma laskee seinän kitkan
  logaritmisesta laista ratkaisematta alikerrosta. Säästää ruutuja
  mutta olettaa, että rajakerros noudattaa lakia, mikä ei päde
  irtoamisen lähellä.
- Väliin jäävä alue $5 < y^+ < 30$ on kummallekin tavalle huono.

Ruudun korkeus on arvioitava ennen hilan tekemistä, vaikka kitkanopeus
on laskennan tulos. Arvioon riittää tasolevyn kokeellinen
kitkakerroin.

```{.python tiedosto="esimerkit/11-seina.py" osa="seina"}
```

```{.tuloste tiedosto="esimerkit/11-seina.odotettu"}
```

Henkilöauton pinnalla seinään asti laskeva hila tarvitsee ensimmäisen
ruudun, jonka keskipiste on 15 mikrometrin päässä pinnasta, kun auto on
neljä ja puoli metriä pitkä. Ruudut ovat siksi seinän lähellä
äärimmäisen litteitä: ohuita seinää vastaan kohtisuorassa ja pitkiä sen
suunnassa. Seinäfunktiolla ensimmäinen ruutu saa olla viisikymmentä
kertaa paksumpi.

## Käytännössä

- **Tarkista Reynoldsin luvusta, onko virtaus turbulentti.** Laminaari
  lasku turbulentista virtauksesta suppenee siististi väärään
  tulokseen tai ei suppene lainkaan.
- **RANS on lähtökohta, LES perusteltu poikkeus.** Jos kiinnostavat
  keskiarvot ja virtaus myötäilee pintoja, RANS riittää. Jos
  kiinnostavat heilahtelut, melu tai voimakkaasti irtoava virtaus,
  tarvitaan LES ja sata- tai tuhatkertainen laskenta.
- **Laske $y^+$ ennen hilaa ja tarkista se tuloksesta.** Ohjelma
  tulostaa seinän viereisten ruutujen $y^+$-arvot. Niiden on oltava
  valitun seinäkäsittelyn alueella koko pinnalla.
- **Kokeile kahta turbulenssimallia.** Jos tulos muuttuu olennaisesti,
  ero on arvio mallin epävarmuudesta, jota mikään muu tarkistus ei
  näytä.
- **Validoi mittausta vasten.** Verifiointi kertoo, onko mallin
  yhtälöt ratkaistu oikein. Onko malli itse oikea tälle virtaukselle,
  selviää vain vertaamalla mittaukseen samanlaisesta tapauksesta.
- **Turbulenssisuureetkin tarvitsevat reunaehdot.** Sisäänvirtauksen
  turbulenssin voimakkuus ja mittakaava ovat usein arvauksia, ja niiden
  vaikutus kannattaa kokeilla.

## Itsearviointi

- Osaat kuvata energiakaskadin ja selittää, mikä määrää pienimpien
  pyörteiden koon.
- Osaat arvioida, miten suoran simuloinnin työmäärä kasvaa Reynoldsin
  luvun mukana, ja perustella, miksi se ei sovi suunnittelulaskentaan.
- Osaat selittää, miksi kaksiulotteinen lasku ei voi kuvata
  turbulenssia.
- Osaat kertoa, mitä DNS, LES ja RANS laskevat ja mitä ne mallintavat,
  ja mitä pyörreviskositeetti tarkoittaa.
- Osaat arvioida seinän viereisen ruudun korkeuden annetulle $y^+$:lle
  ja valita sen mukaan seinäkäsittelyn.
