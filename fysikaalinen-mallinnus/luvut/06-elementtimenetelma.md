# Elementtimenetelmä yhdessä ulottuvuudessa

Differenssimenetelmä korvaa derivaatat erotuksilla. Elementtimenetelmä
(*finite element method*, FEM) tekee toisin: se etsii ratkaisua
yksinkertaisten funktioiden summana ja vaatii, että yhtälö toteutuu
keskimäärin. Tulos on yleensä samannäköinen yhtälöryhmä, mutta reitti
tuo kolme etua, joiden takia lähes kaikki rakenteiden ja monimutkaisten
geometrioiden laskenta tehdään sillä: verkko saa olla epäsäännöllinen,
aineiden rajat ja vuoreunaehdot hoituvat itsestään, ja virheelle on
vahva teoria. Tässä luvussa menetelmä rakennetaan yhdessä
ulottuvuudessa niin, että jokainen vaihe näkyy. Luku 7 siirtää saman
tasoon.

## Heikko muoto

Malliksi otetaan vetosauva. Sen siirtymä $u(x)$ toteuttaa yhtälön

$$-(EA\,u')' = f, \qquad u(0) = 0, \qquad EA\,u'(L) = F,$$

jossa $E$ on kimmomoduuli, $A$ poikkipinta-ala, $f$ jakautunut kuorma
pituutta kohden ja $F$ vapaan pään voima. Tämä **vahva muoto** vaatii
yhtälön toteutuvan jokaisessa pisteessä ja ratkaisulta kaksi
derivaattaa.

Kerrotaan yhtälö mielivaltaisella **testifunktiolla** $v$, jolle
$v(0) = 0$, ja integroidaan sauvan yli. Osittaisintegrointi siirtää
toisen derivaatan testifunktiolle:

$$\int_0^L EA\,u'\,v'\,dx = \int_0^L f\,v\,dx + F\,v(L).$$

Tämä on **heikko muoto**. Siinä on kolme huomionarvoista asiaa.

- Ratkaisulta vaaditaan enää yksi derivaatta. Taitteet, joita aineiden
  rajat ja pistekuormat tuottavat, ovat sallittuja.
- Vuoreunaehto $EA\,u'(L) = F$ ilmestyi yhtälöön itsestään
  osittaisintegroinnin reunatermistä. Sitä kutsutaan **luonnolliseksi
  reunaehdoksi**. Jos termiä ei kirjoiteta, saadaan $F = 0$: vapaa pää
  tai eristetty reuna on oletus, jota ei tarvitse ohjelmoida.
- Siirtymän reunaehto $u(0) = 0$ ei ilmesty itsestään, vaan se on
  vaadittava erikseen. Se on **oleellinen reunaehto**.

Mekaniikassa heikko muoto tunnetaan virtuaalisen työn periaatteena:
sisäisten voimien työ on yhtä suuri kuin ulkoisten voimien työ
jokaisessa kuvitellussa siirtymässä $v$. Lämpötehtävässä se on tase
painotettuna funktiolla $v$, ja kun $v$ on vakio, se on täsmälleen
luvun 2 energiatase.

## Kantafunktiot ja Galerkinin menetelmä

Jaetaan sauva **elementteihin**, joiden päätepisteet ovat **solmuja**
$x_0, \dots, x_n$. Ratkaisua etsitään muodossa

$$u_h(x) = \sum_{j} u_j\,\varphi_j(x),$$

jossa $\varphi_j$ on **kantafunktio**: paloittain lineaarinen funktio,
joka on yksi solmussa $j$ ja nolla kaikissa muissa. Muotonsa vuoksi sitä
kutsutaan hattufunktioksi. Kertoimet $u_j$ ovat suoraan ratkaisun arvot
solmuissa, ja solmujen välillä $u_h$ on suora viiva.

![Vasemmalla hattufunktiot epätasaisella verkolla: jokainen on nollasta
poikkeava vain kahdessa elementissä. Oikealla neljän elementin ratkaisu
tehtävälle, jonka tarkka ratkaisu on
$\sin \pi x$.](kuvat/hattu.png){width=95%}

**Galerkinin menetelmä** käyttää testifunktioina samoja
kantafunktioita. Kun heikkoon muotoon sijoitetaan $u_h$ ja $v =
\varphi_i$ jokaiselle $i$, tuloksena on yhtälöryhmä

$$K\,\mathbf u = \mathbf f, \qquad
  K_{ij} = \int_0^L EA\,\varphi_i'\,\varphi_j'\,dx, \qquad
  f_i = \int_0^L f\,\varphi_i\,dx + F\,\varphi_i(L).$$

$K$ on **jäykkyysmatriisi** ja $\mathbf f$ **kuormavektori**. Matriisi
on harva, koska kaksi hattua menee päällekkäin vain, jos solmut ovat
naapureita. Se on myös symmetrinen ja, kun oleellinen reunaehto on
asetettu, positiivisesti definiitti. Näistä ominaisuuksista hyötyvät
taidon *Numeeriset menetelmät* Choleskyn hajotelma ja
liittogradienttimenetelmä.

## Elementtimatriisi ja kokoaminen

Integraalit lasketaan elementti kerrallaan. Yhdessä elementissä, jonka
pituus on $h$, on kaksi nollasta poikkeavaa kantafunktiota, ja niiden
derivaatat ovat vakiot $-1/h$ ja $1/h$. Elementin osuus
jäykkyysmatriisiin on siis

$$K^e = \frac{EA}{h}\begin{pmatrix} 1 & -1 \\ -1 & 1 \end{pmatrix}.$$

Tämä on jousen jäykkyysmatriisi: elementti on jousi, jonka jousivakio
on $EA/h$. Koko sauva on jousia sarjassa, ja **kokoaminen** summaa
jokaisen jousen osuuden globaalin matriisin niille riveille ja
sarakkeille, joita elementin solmut vastaavat.

```{.python tiedosto="esimerkit/06-sauva.py" osa="kokoaminen"}
```

Silmukka on kaikissa elementtiohjelmissa sama: käy elementit läpi,
laske pieni elementtimatriisi ja lisää se paikalleen. Vain
elementtimatriisin kaava ja numerointi vaihtuvat, kun siirrytään tasoon
tai toiseen fysiikkaan. Pään voima on luonnollinen reunaehto, joten se
on yksi luku kuormavektorissa.

Oleellinen reunaehto asetetaan poistamalla kiinnitetyn solmun yhtälö.
Kokoamisen jälkeen $K$ on singulaarinen, koska mikään ei vielä estä
sauvaa liikkumasta kokonaisena. Tämä on sama asia kuin luvun 2 huomio
pelkistä Neumannin ehdoista.

```{.python tiedosto="esimerkit/06-sauva.py" osa="ratkaisu"}
```

Esimerkin terässauva on kaksi metriä pitkä ja suippenee niin, että
alapään poikkipinta on puolet yläpään pinnasta. Alapäässä riippuu
20 kN:n kuorma.

```{.python tiedosto="esimerkit/06-sauva.py" osa="tulos"}
```

```{.tuloste tiedosto="esimerkit/06-sauva.odotettu"}
```

Siirtymä on jo neljällä elementillä kolmen promillen päässä tarkasta.
Jännitys on huonompi: se lasketaan siirtymän derivaatasta, joka on
elementissä vakio, ja 16 elementilläkin suurin jännitys on kolme
prosenttia liian pieni. Havainto on yleinen ja tärkeä.
Elementtimenetelmän **ensisijainen suure** (siirtymä, lämpötila) on
tarkempi kuin siitä **johdettu suure** (jännitys, lämpövuo), ja
jälkimmäinen on se, jota mitoituksessa yleensä tarvitaan.

Elementin jännitys on tarkimmillaan elementin keskellä, ei päissä.
Tässä suurin jännitys on sauvan alapäässä, ja viimeisen elementin
keskipiste lähestyy sitä vasta elementtien pienentyessä.

## Virheen mittaaminen

Kun ratkaisu on funktio eikä pistejoukko, virheenkin voi mitata
funktiona. Kaksi normia on käytössä:

$$\|e\|_{L^2} = \left(\int_0^L e^2\,dx\right)^{1/2},
  \qquad
  \|e\|_E = \left(\int_0^L (e')^2\,dx\right)^{1/2}.$$

**$L^2$-normi** mittaa itse suureen virhettä ja **energianormi** sen
derivaatan virhettä eli jännityksen tai vuon virhettä. Lineaarisille
elementeille teoria lupaa sileälle ratkaisulle

$$\|u - u_h\|_{L^2} \le C h^2, \qquad \|u - u_h\|_E \le C h.$$

Galerkinin ratkaisu on lisäksi energianormissa **paras mahdollinen**:
mikään muu samojen kantafunktioiden yhdistelmä ei ole lähempänä tarkkaa
ratkaisua. Menetelmä ei siis hukkaa mitään siitä, mihin valitut
kantafunktiot pystyvät, ja virhe riippuu vain siitä, kuinka hyvin
ratkaisua voi niillä esittää.

Seuraava ohjelma ratkaisee tehtävän $-u'' = \pi^2 \sin \pi x$
mielivaltaisella verkolla ja laskee molemmat normit kvadratuurilla.
Kuormavektorikin integroidaan kvadratuurilla, koska kuorma ei ole
vakio.

```{.python tiedosto="esimerkit/06-kertaluku.py" osa="ratkaisu"}
```

```{.python tiedosto="esimerkit/06-kertaluku.py" osa="normit"}
```

```{.python tiedosto="esimerkit/06-kertaluku.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/06-kertaluku.odotettu"}
```

Kertaluvut ovat teorian mukaiset: kaksi $L^2$-normissa ja yksi
energianormissa. Derivaatta menettää yhden kertaluvun, mikä selittää
edellisen esimerkin jännitysten hitaan paranemisen.

Kaksi viimeistä riviä näyttävät kaksi muuta asiaa. Solmuissa virhe on
pyöristysvirheen tasolla, vaikka solmujen välillä se ei ole. Tämä on
yksiulotteisen tehtävän erikoisuus, joka ei yleisty tasoon. Ja verkko,
joka on tihennetty reunoille, antaa tälle tehtävälle huonomman tuloksen
kuin tasavälinen, vaikka solmuja on yhtä monta: ratkaisu $\sin \pi x$
kaartuu eniten keskellä, ja sinne jäi harvin verkko. Tihennys auttaa
vain, jos se on siellä, missä ratkaisu muuttuu nopeimmin (luku 11).

## Differenssimenetelmä ja elementtimenetelmä rinnakkain

Tasavälisellä verkolla ja vakiokertoimilla lineaaristen elementtien
jäykkyysmatriisi on $\frac{1}{h}\,\mathrm{tridiag}(-1, 2, -1)$, eli
sama kuin toisen differenssin matriisi kerrottuna hilavälillä. Erot
ovat muualla:

| Asia | Differenssimenetelmä | Elementtimenetelmä |
|---|---|---|
| tuntemattomat | arvot hilapisteissä | kantafunktioiden kertoimet; ratkaisu on funktio |
| lähtökohta | derivaatan likiarvo | heikko muoto (tase painotettuna) |
| geometria | suorakulmainen hila | mielivaltainen verkko |
| vuoreunaehto | haamupiste tai erillinen tase | luonnollinen: yksi termi tai ei mitään |
| aineiden raja | harmoninen keskiarvo | elementin raja kohdalle, muuta ei tarvita |
| kuorma | arvo pisteessä | integraali kantafunktion kanssa |
| virheteoria | Taylorin kehitelmä, vaatii sileyttä | paras approksimaatio energianormissa |
| toteutus | muutama rivi | kokoamissilmukka ja verkon tietorakenne |

Kumpikaan ei ole toista parempi kaikessa. Säännöllisessä geometriassa
differenssimenetelmä on yksinkertaisempi ja nopeampi, ja siksi sitä
käytetään esimerkiksi sääennusteissa ja aaltojen simuloinnissa.
Elementtimenetelmä on vahvimmillaan, kun geometria on mutkikas.
Kolmas sukulainen, kontrollitilavuusmenetelmä, diskretoi taseen suoraan
luvun 2 tapaan mielivaltaisessa verkossa ja hallitsee virtauslaskentaa.

## Käytännössä

- **Opettele lukemaan heikkoa muotoa.** Elementtikirjastoille tehtävä
  annetaan heikkona muotona, ei matriiseina (luku 8). Kun osaa johtaa
  sen osittaisintegroinnilla, osaa myös tarkistaa etumerkit ja
  reunatermit.
- **Luonnollinen reunaehto on oletus.** Jos reunalle ei aseteta
  mitään, se on vapaa tai eristetty. Unohtunut tuki ei aiheuta
  virheilmoitusta vaan singulaarisen matriisin tai, pahimmillaan,
  ratkaisijan tuottamaa kohinaa.
- **Johdettu suure on kertalukua huonompi.** Mitoita verkko
  jännityksen tai vuon tarkkuuden mukaan, älä siirtymän.
- **Lue jännitys elementin sisältä.** Lineaarisen elementin jännitys
  on tarkimmillaan keskipisteessä. Ohjelmien näyttämät sileät
  jännityskuvat on tehty keskiarvoistamalla, ja sileys voi peittää
  liian harvan verkon.
- **Aseta solmu aineen rajalle ja pistekuorman kohdalle.** Silloin
  ratkaisun taite osuu elementin rajalle, jossa kantafunktiot voivat
  esittää sen.

## Itsearviointi

- Osaat johtaa vahvasta muodosta heikon muodon osittaisintegroinnilla
  ja kertoa, mistä luonnollinen reunaehto tulee.
- Osaat erottaa oleellisen ja luonnollisen reunaehdon ja tiedät, miten
  kumpikin toteutetaan.
- Osaat kirjoittaa lineaarisen elementin jäykkyysmatriisin ja koota
  niistä globaalin matriisin silmukalla.
- Osaat selittää, miksi jännitys suppenee hitaammin kuin siirtymä, ja
  mitata kertaluvut $L^2$- ja energianormissa.
- Osaat vertailla differenssi- ja elementtimenetelmää ja valita
  niistä tehtävään sopivan.
