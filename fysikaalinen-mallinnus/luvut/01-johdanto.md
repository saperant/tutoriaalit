# Johdanto {.runko-johdanto}

Fysikaalinen malli on yhtälö, joka kertoo, miten lämpötila, siirtymä,
paine tai jokin muu suure jakautuu kappaleessa ja muuttuu ajassa.
Simulointi on tuon yhtälön ratkaisemista tietokoneella. Sillä
mitoitetaan jäähdytyslevyjä ja siltoja, ennustetaan säätä ja
suunnitellaan mikropiirejä, koska laskenta on halvempaa ja nopeampaa
kuin prototyyppi ja koska monia asioita ei voi mitata lainkaan.

Simulointi tuottaa aina vastauksen, ja värikäs kuva näyttää
uskottavalta, vaikka se olisi väärä. Siksi tämä tutoriaali opettaa
laskemisen rinnalla tarkistamisen. Kaikki luvut noudattavat samaa
ketjua:

```{.dot otsikko="Mallinnuksen ketju. Jokaisessa vaiheessa tehdään oma virheensä, ja jokaiselle on oma tarkistuksensa."}
digraph {
  node [shape=box];
  laki [label="säilymislaki\n+ aineen laki"];
  yhtalo [label="differentiaali-\nyhtälö"];
  disk [label="diskretointi:\nhila tai verkko"];
  ryhma [label="yhtälöryhmä"];
  ratkaisu [label="ratkaisu"];
  tarkistus [label="tarkistus"];
  {rank=same; laki; yhtalo; disk}
  {rank=same; tarkistus; ratkaisu; ryhma}
  laki -> yhtalo [label="oletukset"];
  yhtalo -> disk [label="katkaisuvirhe"];
  disk -> ryhma;
  tarkistus -> ratkaisu [dir=back];
  ratkaisu -> ryhma [dir=back, label="ratkaisija"];
  laki -> tarkistus [dir=back, style=dashed, label="väärä malli?"];
  disk -> tarkistus [dir=back, style=dashed, label="liian harva?", constraint=false];
}
```

1. **Säilymislaki** sanoo, että energia, massa tai liikemäärä ei
   synny eikä häviä. **Aineen laki** kertoo, miten aine käyttäytyy:
   lämpö virtaa kuumasta kylmään, jousi venyy voiman suhteessa.
2. Yhdessä ne antavat **differentiaaliyhtälön** reuna- ja
   alkuehtoineen. Tässä vaiheessa tehdään mallin oletukset.
3. **Diskretointi** korvaa jatkuvan kentän äärellisellä määrällä
   lukuja: arvoilla hilapisteissä (differenssimenetelmä) tai
   kantafunktioiden kertoimilla (elementtimenetelmä).
4. Tuloksena on **yhtälöryhmä**, usein harva ja suuri.
5. Sen **ratkaisu** on likiarvo.
6. **Tarkistus** vastaa kahteen eri kysymykseen: ratkaistiinko yhtälöt
   oikein (*verifiointi*) ja ratkaistiinko oikeat yhtälöt
   (*validointi*).

Jokainen menetelmä toteutetaan ensin itse NumPyllä ja SciPyllä niin
pienessä tehtävässä, että jokainen vaihe näkyy. Vasta sen jälkeen sama
tehdään kirjastolla. Kirjasto on tuotantotyössä oikea valinta, mutta sen
tulosta osaa arvioida vain, jos tietää, mitä se tekee.

## Esitiedot ja rajaus

Tutoriaali olettaa taidot *Numeeriset menetelmät* ja
*Differentiaaliyhtälöt ja Laplace-muunnos*. Edellisestä tarvitaan
katkaisuvirhe ja kertaluku, tavallisten differentiaaliyhtälöiden
ratkaisijat stabiilisuusalueineen ja jäykkyyksineen sekä harvat matriisit
ja liittogradienttimenetelmä. Jälkimmäisestä tarvitaan mallintaminen
tavallisilla differentiaaliyhtälöillä: tase, alkuehto, värähtelijä ja
ominaistaajuus. Näitä ei johdeta uudelleen, vaan niihin viitataan.

Tutoriaali käsittelee lineaarisia tehtäviä: lämmönjohtumista, aaltoja
ja lineaarista elastisuutta yhdessä ja kahdessa ulottuvuudessa.
Rajauksen ulkopuolelle jäävät

- nesteiden ja kaasujen virtaus (advektio ja Navier–Stokesin yhtälöt),
  joka on oma taitonsa *Virtauslaskenta*,
- reaaliaikainen simulointi peleissä, jossa tavoite on uskottavuus ja
  stabiilisuus kiinteässä aikabudjetissa eikä tarkkuus: taito
  *Pelifysiikka*,
- epälineaarinen mekaniikka (plastisuus, suuret siirtymät, kontaktit)
  ja kolmiulotteiset verkot, joista on lyhyt katsaus viimeisessä
  luvussa,
- kaupalliset ohjelmistot. Niiden käyttöliittymät vaihtuvat, mutta
  menetelmät niiden sisällä ovat tämän tutoriaalin menetelmiä.

## Työkalut

Esimerkit ovat Pythonia. NumPy ja SciPy riittävät lukuihin 1–7. Luvusta
8 alkaen käytetään lisäksi **scikit-fem**-kirjastoa. Se on puhdasta
Pythonia oleva elementtimenetelmäkirjasto, joka asentuu komennolla
`pip install scikit-fem` eikä tarvitse kääntäjää. Luku 12 johtaa
lähdetermejä SymPyllä.

Esimerkit ajetaan hakemistossa `esimerkit/`, esimerkiksi
`python3 01-ripa.py`. Jokaisen esimerkin tuloste on tallennettu
tiedostoon `.odotettu`, ja testit vertaavat ajon tulosta siihen. Kuvat
piirtää `kuvat/piirra.py` samoilla funktioilla, joita esimerkit
käyttävät (`make kuvat`). Pyöristysvirheen tasoiset luvut vaihtelevat
koneesta toiseen, joten tulosteissa näytetään vain luotettavat numerot.

## Ensimmäinen esimerkki: koko ketju kerralla

Alumiinitanko on kiinni kahdessa 100-asteisessa seinässä, ja 20-asteinen
huoneilma jäähdyttää sitä. Kuinka kylmä tangon keskikohta on?

**Säilymislaki.** Tarkastellaan tangon lyhyttä palaa. Tasapainossa
palaan johtuu yhtä paljon lämpöä kuin siitä poistuu: johtumalla
naapuripaloihin ja konvektiolla ilmaan. **Aineen lait** ovat Fourier'n
laki (lämpövuo on verrannollinen lämpötilan derivaattaan,
$q = -k\,u'$) ja Newtonin jäähtymislaki (pinta luovuttaa lämpöä
tehon $h(u - T_\infty)$ pinta-alayksikköä kohden).

**Yhtälö.** Kun palan pituus lähestyy nollaa, tase antaa

$$u'' = m^2 (u - T_\infty), \qquad m^2 = \frac{hP}{kA},$$

jossa $P$ on poikkileikkauksen piiri ja $A$ sen ala. Oletuksia on
kolme: lämpötila on poikkileikkauksessa vakio, aineen ominaisuudet eivät
riipu lämpötilasta, ja säteilyä ei ole. Reunaehdot ovat seinien
lämpötilat.

```{.python tiedosto="esimerkit/01-ripa.py" osa="malli"}
```

Tälle yhtälölle on tarkka ratkaisu, joten diskretoinnin virhe voidaan
mitata. Yleensä tarkkaa ratkaisua ei ole, ja juuri siksi tarkistuksen
menetelmät harjoitellaan tehtävillä, joissa se on.

**Diskretointi ja yhtälöryhmä.** Tanko jaetaan pisteisiin, joiden väli
on $h$, ja toinen derivaatta korvataan erotusosamäärällä
$(u_{i-1} - 2u_i + u_{i+1})/h^2$. Jokaisesta sisäpisteestä tulee yksi
yhtälö, jossa on kolme tuntematonta, joten matriisi on
kolmilävistäjäinen.

```{.python tiedosto="esimerkit/01-ripa.py" osa="ratkaisu"}
```

**Tarkistus.** Ratkaisu lasketaan viidellä hilalla, joista jokainen on
edellistä kaksi kertaa tiheämpi.

```{.python tiedosto="esimerkit/01-ripa.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/01-ripa.odotettu"}
```

![Tangon lämpötila kolmella ja seitsemällä sisäpisteellä sekä tarkka
ratkaisu. Seitsemällä pisteellä ero on enää sadasosa
astetta.](kuvat/ripa.png){width=70%}

Kun pisteväli puolittuu, virhe pienenee neljäsosaan. Menetelmä on siis
toista kertalukua, kuten erotusosamäärän Taylorin kehitelmä lupaa. Tämä
**kertaluvun mittaaminen** on tutoriaalin tärkein yksittäinen työkalu:
jos mitattu kertaluku on teorian mukainen, koodi ratkaisee yhtälön
oikein, ja jos se ei ole, jossain on virhe. Luku 12 käyttää samaa
ajatusta tehtäviin, joiden tarkkaa ratkaisua ei tunneta.

Vastaus kysymykseen on 90,9 °C. Onko se oikea vastaus oikealle
tangolle, on eri kysymys: lämmönsiirtokerroin $h = 25$ on käsikirjan
suuruusluokka, ei mitattu arvo, ja sen epävarmuus on paljon suurempi
kuin diskretoinnin virhe. Tähänkin palataan luvussa 12.

## Tutoriaalin rakenne

1. Johdanto
2. Säilymislaista yhtälöksi – kontrollitilavuus, vuo, lämpö- ja
   aaltoyhtälö, reunaehdot, dimensiottomat luvut
3. Differenssimenetelmä: tasapainotila – rajapinnat, reunaehtojen
   kertaluku, Poissonin yhtälö levyssä
4. Lämpöyhtälö ajassa – eksplisiittinen ja implisiittinen menetelmä,
   stabiilisuusraja, Crank–Nicolson, Biot'n luku
5. Aallot ja CFL-ehto – kieli, energian säilyminen, kalvon
   ominaistaajuudet
6. Elementtimenetelmä yhdessä ulottuvuudessa – heikko muoto,
   kantafunktiot, kokoaminen, virheen normit
7. Elementtimenetelmä tasossa – kolmiot, oma pieni kirjasto,
   kulmasingulariteetti, luonnolliset reunaehdot
8. Sama kirjastolla – scikit-fem, korkeampi aste
9. Lineaarinen elastisuus – ulokepalkki, jännityskeskittymä
10. Ominaisvärähtelyt ja aikariippuvat tehtävät – massamatriisi,
    ominaisarvot, lämpeneminen ajassa
11. Verkot ja ratkaisijat – verkon laatu, porrastus, täyttyminen ja
    iteraatiot
12. Verifiointi ja validointi – valmistettu ratkaisu, Richardsonin
    ekstrapolointi, malli vastaan mittaus
13. Lopuksi – työnkulku, jatkotaidot, lähteet

Luvut 2–5 muodostavat differenssimenetelmän kokonaisuuden ja luvut 6–10
elementtimenetelmän. Luvut 11 ja 12 koskevat molempia. Lukijalle, jolle
differenssimenetelmä on tuttu, riittää luvuista 3–5 itsearviointien
läpikäynti.
