# Lineaarinen elastisuus

Rakenteiden lujuuslaskenta on elementtimenetelmän alkuperäinen ja
edelleen yleisin käyttö. Fysiikka on tuttu luvun 6 sauvasta: tasapaino
ja Hooken laki. Uutta on, että tuntematon on vektori. Jokaisella
solmulla on siirtymä kumpaankin suuntaan, ja jännitys on usean
komponentin suure. Tässä luvussa lasketaan ulokepalkki ensin omalla
koodilla ja sitten kirjastolla, nähdään, miksi lineaarinen kolmio on
taivutuksessa huono elementti, ja lasketaan reiän aiheuttama
jännityskeskittymä.

## Venymä, jännitys ja tasojännitystila

Pisteen siirtymä on $(u, v)$. **Venymä** kertoo, miten kappale muuttaa
muotoaan siirtymän seurauksena, ja se on siirtymän derivaatta:

$$\varepsilon_{xx} = \frac{\partial u}{\partial x}, \qquad
  \varepsilon_{yy} = \frac{\partial v}{\partial y}, \qquad
  \gamma_{xy} = \frac{\partial u}{\partial y} + \frac{\partial v}{\partial x}.$$

Kaksi ensimmäistä ovat venymiä akselien suuntaan ja kolmas liukuma eli
suoran kulman muutos. Jäykän kappaleen siirto ja pieni kierto eivät
tuota venymää.

**Jännitys** on sisäinen voima pinta-alaa kohden. Lineaarisesti
kimmoisessa aineessa se on verrannollinen venymään. Ohuessa levyssä,
jota kuormitetaan omassa tasossaan, paksuuden suuntainen jännitys on
nolla. Tämä **tasojännitystila** antaa Hooken lain muodossa

$$\begin{pmatrix} \sigma_{xx} \\ \sigma_{yy} \\ \tau_{xy} \end{pmatrix}
  = \frac{E}{1 - \nu^2}
  \begin{pmatrix} 1 & \nu & 0 \\ \nu & 1 & 0 \\ 0 & 0 & \frac{1-\nu}{2} \end{pmatrix}
  \begin{pmatrix} \varepsilon_{xx} \\ \varepsilon_{yy} \\ \gamma_{xy} \end{pmatrix},$$

jossa $E$ on kimmomoduuli ja $\nu$ Poissonin luku: kun kappaletta
venytetään yhteen suuntaan, se kapenee poikittain osuudella $\nu$.

```{.python tiedosto="esimerkit/09-uloke.py" osa="materiaali"}
```

Paksu kappale, jonka venymä paksuussuunnassa on estetty (pato, pitkä
putki), on **tasovenymätilassa**. Yhtälöt ovat samat, mutta vakiot
erilaiset, ja väärä valinta muuttaa jäykkyyttä noin kymmenen prosenttia.

Heikko muoto on virtuaalisen työn periaate: sisäinen työ
$\int \boldsymbol\sigma(\mathbf u) : \boldsymbol\varepsilon(\mathbf v)\,dV$
on yhtä suuri kuin kuormien työ jokaisella testisiirtymällä
$\mathbf v$. Tuet ovat oleellisia reunaehtoja ja kuormat luonnollisia.
Kuormittamaton vapaa pinta ei vaadi mitään.

## Vakiovenymäkolmio

Lineaarisella kolmiolla kumpikin siirtymäkomponentti on taso, joten
venymä on elementissä vakio. Elementtiä kutsutaan siksi
vakiovenymäkolmioksi (*constant strain triangle*, CST). Venymän ja
solmusiirtymien yhteys kirjoitetaan matriisina $B$, jonka alkiot ovat
luvun 7 kantafunktioiden gradientit:

```{.python tiedosto="esimerkit/09-uloke.py" osa="elementti"}
```

Elementtimatriisi $t\,A\,B^\mathsf{T} D B$ on kooltaan 6 × 6, koska
kolmella solmulla on kullakin kaksi vapausastetta. Kokoaminen on sama
silmukka kuin ennen. Vapausasteet numeroidaan solmuittain: solmun $n$
vaakasiirtymä on indeksissä $2n$ ja pystysiirtymä indeksissä $2n + 1$.

## Ulokepalkki

Teräslatta, metrin pituinen, sata millimetriä korkea ja kymmenen
paksu, on toisesta päästään kiinni seinässä. Vapaata päätä painaa
yhden kilonewtonin voima. Palkkiteoria antaa vertailuarvon:
taivutuksesta pään taipuma on $FL^3/(3EI)$ ja leikkauksesta pieni
lisä.

```{.python tiedosto="esimerkit/09-uloke.py" osa="ratkaisu"}
```

```{.python tiedosto="esimerkit/09-uloke.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/09-uloke.odotettu"}
```

![Ulokepalkin vaakajännitys ja muodonmuutos verkolla 80 × 8.
Siirtymät on piirretty 30-kertaisina. Yläpinta on vedolla ja alapinta
puristuksella, ja jännitys kasvaa lineaarisesti kohti
kiinnitystä.](kuvat/uloke.png){width=95%}

Karkein verkko antaa taipumasta vain 23 prosenttia. Tulos ei ole
hieman epätarkka vaan täysin väärä, ja se näyttäisi uskottavalta
kuvalta. Vasta 1458 vapausasteella päästään 95 prosenttiin.

Syy on elementissä. Taivutuksessa venymä muuttuu lineaarisesti palkin
korkeuden yli, vedosta puristukseen. Vakiovenymäkolmio ei pysty
esittämään sitä, vaan taipuessaan sen on pakko leikkautua, ja tämä
ylimääräinen leikkausjäykkyys tekee mallista liian jäykän. Ilmiötä
kutsutaan **lukkiutumiseksi**. Se ei ole koodin virhe, ja kertaluku on
oikea; vakio vain on niin suuri, että järkevällä verkolla ei päästä
tarkkuuteen.

Jännityssarakkeissa on toinen opetus. Palkin keskikohdan jännitys
lähestyy teorian arvoa 30 MPa. Kiinnityksen jännitys sen sijaan ylittää
teorian arvon 60 MPa ja jatkaa kasvuaan: kiinnitetyn reunan nurkka on
samanlainen singulariteetti kuin luvun 7 sisäkulma. Täysin jäykkää
seinää ei ole olemassa, ja ääretön jännitys nurkassa on reunaehdon
idealisoinnin tuote. Suurinta jännitystä ei siis voi lukea suoraan
kuvan punaisimmasta kohdasta.

## Toisen asteen elementti

Sama palkki kirjastolla. Valmis muoto `linear_elasticity` ottaa Lamén
vakiot, ja vektoriarvoinen kanta tehdään kääreellä `ElementVector`.
Kuorma on reunaintegraali, joka kootaan reunan kannalla `FacetBasis`.

```{.python tiedosto="esimerkit/09-kirjasto.py" osa="malli"}
```

```{.python tiedosto="esimerkit/09-kirjasto.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/09-kirjasto.odotettu"}
```

![Pään taipuma osuutena palkkiteorian arvosta. Toisen asteen
elementti on karkeimmallakin verkolla prosentin päässä, lineaarinen
elementti ei yllä siihen millään kokeillulla
verkolla.](kuvat/taipuma.png){width=62%}

Lineaarisen elementin sarake toistaa oman koodin luvut numero
numerolta, mikä on jälleen kahden toteutuksen ristiintarkistus. Toisen
asteen elementti antaa 126 vapausasteella 99,1 prosenttia, enemmän kuin
lineaarinen 1458 vapausasteella. Sen venymä on elementissä lineaarinen,
joten se esittää taivutuksen luonnostaan. Tästä syystä rakenteiden
laskennassa käytetään toisen asteen elementtejä tai erityisiä
taivutukseen sopivia nelikulmioita, ja lineaarista kolmiota vältetään.

Tulos tasoittuu arvoon 99,8 prosenttia, ei sataan. Ero ei ole
numeerista virhettä vaan kahden mallin ero: palkkiteoria olettaa, että
poikkileikkaus pysyy tasona, ja tasomalli kiinnittää koko päädyn, myös
poikittaisen kutistumisen. Kumpikin on malli, eikä kumpikaan ole
"oikea" vastaus.

## Jännityskeskittymä reiän reunalla

Levyä, jonka keskellä on pyöreä reikä, vedetään. Reikä pakottaa
voimavirran kiertämään itsensä, ja jännitys keskittyy reiän reunalle.
Äärettömän suurelle levylle tehtävällä on tarkka ratkaisu, jonka
mukaan suurin jännitys on kolminkertainen vetojännitykseen nähden
reiän koosta riippumatta (Kirsch, 1898).

Levy on symmetrinen kummankin akselin suhteen, joten mallinnetaan
neljännes. Symmetriatasolla tasoa vastaan kohtisuora siirtymä on nolla
ja tason suuntainen vapaa.

Verkko tehdään **kuvaamalla**: säännöllinen ruudukko parametritasossa
kuvataan alueeseen niin, että ruudukon toinen suunta kulkee reiän
reunalta ulkoreunalle ja toinen kiertää reikää. Solmut tihennetään
reikää kohti, missä jännitys muuttuu nopeimmin.

```{.python tiedosto="esimerkit/09-reika.py" osa="verkko"}
```

```{.python tiedosto="esimerkit/09-reika.py" osa="ratkaisu"}
```

Jännitys on siirtymän derivaatta ja siksi epäjatkuva elementtien
rajoilla. Ohjelma projisoi sen jatkuvaksi kentäksi, jonka arvo luetaan
reiän laelta.

```{.python tiedosto="esimerkit/09-reika.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/09-reika.odotettu"}
```

![Vasemmalla kuvattu verkko, kun reiän säde on viidesosa levyn
puolileveydestä. Oikealla vaakajännitys vetojännityksen
kerrannaisina: huippu on reiän laella, ja reiän sivulla on lähes
jännityksetön alue.](kuvat/reika.png){width=95%}

Tulokset suppenevat kolmen merkitsevän numeron tarkkuuteen, joten
numeerinen virhe on hallinnassa. Pienellä reiällä keskittymäkerroin on
3,02, lähellä Kirschin arvoa. Reiän kasvaessa kerroin nousee: kun reiän
säde on 40 prosenttia puolileveydestä, kerroin on 4,8. Kirschin kaava
ei ole väärä, mutta sen oletus äärettömästä levystä ei enää päde, kun
reiän ja reunan väliin jää kapea kannas.

Tässä on validoinnin ydin pienoiskoossa. Numeerinen ratkaisu vastaa
kysymykseen "mitä nämä yhtälöt antavat tälle geometrialle", ja se
vastaa siihen hyvin. Kaava vastaa eri kysymykseen. Kumpaa käyttää,
riippuu siitä, kumman oletukset ovat lähempänä todellista kappaletta.

Reiän reuna ei ole singulariteetti, toisin kuin ulokepalkin nurkka:
reuna on sileä, jännitys on äärellinen ja se suppenee. Ero näkyy
suoraan tulosteista, ja se on syy siihen, että kulmat pyöristetään
oikeissa rakenteissa.

## Käytännössä

- **Älä käytä lineaarista kolmiota taivutukseen.** Toisen asteen
  elementit ovat rakenteiden laskennan oletus. Jos tulos on
  huomattavasti käsilaskua jäykempi, epäile lukkiutumista.
- **Laske ensin käsin.** Palkkiteoria, vetosauva ja painesäiliön
  kaavat antavat suuruusluokan minuuteissa. Elementtimalli, joka on
  eri mieltä kertoimella kaksi, on todennäköisemmin väärässä kuin
  kaava.
- **Tarkista tukireaktiot.** Tukivoimien summan pitää olla yhtä suuri
  kuin kuormien summa. Tämä on rakenteen energiatase, ja se löytää
  väärät kuormat ja yksikkövirheet.
- **Käytä symmetriaa.** Neljännesmalli on neljä kertaa pienempi ja
  poistaa samalla jäykän kappaleen liikkeet, jotka muuten pitäisi
  estää keinotekoisilla tuilla.
- **Erota singulariteetti keskittymästä.** Pyöristetyn muodon huippu
  suppenee, terävän nurkan ei. Tihennä verkkoa kahdesti: jos huippu
  kasvaa joka kerralla, se on singulariteetti, ja sen arvo on
  merkityksetön.
- **Valitse tasojännitys tai tasovenymä tietoisesti.** Ohut levy on
  tasojännitystilassa, pitkän kappaleen poikkileikkaus
  tasovenymätilassa. Kirjastojen oletus on usein jälkimmäinen.

## Itsearviointi

- Osaat kirjoittaa venymän siirtymien derivaattoina ja tasojännitystilan
  Hooken lain matriisimuodossa.
- Osaat koota vakiovenymäkolmion jäykkyysmatriisin ja selittää
  vapausasteiden numeroinnin.
- Osaat selittää, mitä lukkiutuminen on ja miksi toisen asteen
  elementti ratkaisee sen.
- Osaat asettaa symmetriareunaehdot ja kuormittaa reunaa kirjaston
  välineillä.
- Osaat erottaa jännityssingulariteetin jännityskeskittymästä
  verkkoa tihentämällä.
- Osaat arvioida, milloin analyyttinen kaava ja milloin numeerinen
  malli vastaa paremmin todellista kappaletta.
