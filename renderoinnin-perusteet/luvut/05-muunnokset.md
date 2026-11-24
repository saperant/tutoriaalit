# Muunnokset

Kolmioverkon kärjet on tallennettu mallin omaan koordinaatistoon:
kuution kärjet ovat $(\pm 1, \pm 1, \pm 1)$ riippumatta siitä, missä
kuutio on maailmassa tai mistä sitä katsotaan. Ennen rasterointia
jokainen kärki kuljetetaan koordinaatistosta toiseen, kunnes se on
pikseleinä ruudulla. Ketju on sama kaikissa grafiikkarajapinnoissa, ja
sen vaiheiden nimet kannattaa opetella, koska virheet löytyvät
kysymällä, missä koordinaatistossa mikin arvo on.

## Koordinaatistot

| Koordinaatisto | Muunnos seuraavaan | Huomio |
|----------------|--------------------|--------|
| malli | mallimatriisi $M$ | kappaleen omat akselit |
| maailma | näkymämatriisi $V$ | yhteinen kaikille kappaleille |
| kamera | projektiomatriisi $P$ | kamera origossa, katse $-z$ |
| leikkausavaruus | jako $w$:llä | homogeeninen, $w$ on etäisyys |
| NDC | näkymäportti | kuutio $[-1, 1]^3$ |
| ruutu | – | pikselit, $y$ alas, syvyys 0–1 |

Tässä tutoriaalissa käytetään samoja sopimuksia kuin taidossa
*Lineaarialgebra*: sarakevektorit, joten muunnos kirjoitetaan
vasemmalle ($M p$), ja OpenGL:n tyyliset koordinaatistot, joissa
kamera katsoo negatiivisen $z$-akselin suuntaan ja NDC:n syvyys on
välillä $-1 \ldots 1$. Lineaarialgebrassa leikkausavaruutta kutsuttiin
leikekoordinaateiksi. Direct3D ja Vulkan käyttävät syvyysväliä
$0 \ldots 1$, ja Vulkanin NDC:ssä $y$ osoittaa alas; ero näkyy vain
projektiomatriisissa ja näkymäportissa.

## Matriisit koodina

Pisteellä on homogeeninen koordinaatti $w = 1$ ja suunnalla $w = 0$,
joten siirto vaikuttaa pisteisiin mutta ei suuntiin:

```{.cpp tiedosto="esimerkit/yhteinen/vektori.hpp" osa="matriisi"}
```

Perusmuunnokset ovat siirto, skaalaus ja kierto. Kierrot annetaan
kosinina ja sinina, mikä pitää tulokset samoina eri kääntäjillä ja
on usein muutenkin kätevää: kulman kosini ja sini saadaan monesti
suoraan vektoreista ilman trigonometriaa.

```{.cpp tiedosto="esimerkit/yhteinen/vektori.hpp" osa="muunnokset"}
```

Mallimatriisi kootaan perusmuunnoksista, ja **järjestys ratkaisee**:
$T \cdot R$ kiertää ensin ja siirtää sitten, $R \cdot T$ siirtää ensin
ja kiertää sitten siirretyn kappaleen origon ympäri. Tavallinen
järjestys on skaalaus, kierto, siirto eli $M = T R S$, luettuna oikealta
vasemmalle.

## Kamera ja projektio

Näkymämatriisi on kameran asennon käänteismatriisi. `katse` rakentaa
sen silmän paikasta, kohteesta ja ylössuunnasta, ja `perspektiivi`
projisoi kamerakoordinaatit leikkausavaruuteen. Molemmat johdettiin
lineaarialgebran luvussa *Homogeeniset koordinaatit*; tässä ne ovat
C++:na:

```{.cpp tiedosto="esimerkit/yhteinen/vektori.hpp" osa="kamera"}
```

Projektiomatriisin parametri `f` on $1/\tan(\theta/2)$, missä
$\theta$ on pystysuora näkökenttä. Arvo 1,5 vastaa noin 67 astetta ja
1,2 noin 80 astetta. Suurempi `f` on kapeampi näkökenttä eli
"teleobjektiivi". Leveys jaetaan kuvasuhteella, jotta neliö näkyy
neliönä myös leveällä ruudulla.

Matriisin viimeinen rivi $(0, 0, -1, 0)$ kopioi kamerakoordinaattien
$-z$:n eli etäisyyden katsesuunnassa koordinaattiin $w$. Kun leikkausavaruuden
koordinaatit jaetaan myöhemmin $w$:llä, kaukaiset pisteet siirtyvät
lähemmäs keskustaa: se on perspektiivi.

## Verteksin matka

Seuraava ohjelma seuraa kuution yhtä kärkeä vaihe vaiheelta. Kolme
matriisia kerrotaan yhdeksi `mvp`-matriisiksi kerran, ja sillä
kerrotaan jokainen kärki:

```{.cpp tiedosto="esimerkit/05-muunnokset.cpp" osa="matriisit"}
```

```{.cpp tiedosto="esimerkit/05-muunnokset.cpp" osa="vaiheet"}
```

Viimeinen vaihe on **näkymäportti** (viewport): NDC:n $x$ välillä
$-1 \ldots 1$ venytetään välille $0 \ldots \text{leveys}$, $y$
käännetään ja venytetään välille $0 \ldots \text{korkeus}$, ja syvyys
siirretään välille 0–1. Tämä on ainoa kohta, jossa ruudun $y$ alas
-suunta näkyy:

$$x_r = \frac{x_n + 1}{2} L, \qquad y_r = \frac{1 - y_n}{2} K, \qquad
z_r = \frac{z_n + 1}{2}.$$

Lopuksi piirretään kuution särmät Bresenhamin viivoilla. Kuution
jokaisella sivulla on omat neljä kärkeään, joten sivun reunat saadaan
kulkemalla sivun kärjet ympäri:

```{.cpp tiedosto="esimerkit/05-muunnokset.cpp" osa="rautalanka"}
```

```{.tuloste tiedosto="esimerkit/05-muunnokset.odotettu"}
```

Tulosteesta näkee jokaisen vaiheen merkityksen. Maailmassa kärki on
kierretty ja nostettu 0,5 ylös. Kamerakoordinaateissa sen $z$ on
negatiivinen (kärki on kameran edessä), ja itseisarvo on etäisyys
kamerasta katsesuunnassa. Leikkausavaruuden $w$ on sama luku. NDC:ssä kaikki
näkyvät pisteet ovat kuutiossa $[-1, 1]^3$, ja ruudulla kärki on
pikselissä (44, 16). Rautalankamallissa näkyvät myös takasärmät,
koska viivat eivät tiedä mitään peittämisestä.

## Kuution malli

Kuution sivut tallennetaan erikseen, vaikka kulmat ovat yhteisiä,
koska jokaisella sivulla on oma normaali ja omat
tekstuurikoordinaatit. Kärjen tiedot ovat yhdessä rakenteessa, ja
kolmiot viittaavat kärkiin indekseillä:

```{.cpp tiedosto="esimerkit/yhteinen/malli.hpp" osa="malli"}
```

```{.cpp tiedosto="esimerkit/yhteinen/malli.hpp" osa="kuutio"}
```

Kolmiot ovat ulkoa katsottuna vastapäivään. Sivun akselit $u$ ja $v$
valitaan niin, että $u \times v$ on sivun normaali, jolloin kulmat
järjestyksessä $(-u, -v), (u, -v), (u, v), (-u, v)$ kiertävät
vastapäivään normaalin suunnasta katsottuna. Kiertosuunta on osa
mallin dataa: luvussa *Syvyys ja näkyvyys* sen avulla hylätään
kameraan päin kääntymättömät kolmiot.

## Normaalit

Normaali on suunta, mutta sitä ei saa muuntaa samalla matriisilla
kuin tangenttisuuntia. Jos malli skaalataan epätasaisesti (esimerkiksi
venytetään $x$-suunnassa), pinnan tangentit venyvät, mutta normaalin on
pysyttävä kohtisuorassa niihin. Oikea matriisi on mallimatriisin
$3 \times 3$-osan **käänteismatriisin transpoosi**
$(M^{-1})^{\mathsf T}$:

```{.cpp tiedosto="esimerkit/yhteinen/vektori.hpp" osa="normaalit"}
```

Kofaktorimatriisi on $\det(M) \cdot (M^{-1})^{\mathsf T}$, joten se
osoittaa samaan suuntaan, kun determinantti on positiivinen, ja
normalisointi hoitaa pituuden. Pelkillä kierroilla ja tasaisella
skaalauksella tulos on sama kuin mallimatriisilla, ja moni moottori
käyttää silloin suoraan mallimatriisia.

## Käytännössä

- **Nimeä koordinaatistot.** Kirjoita muuttujien nimiin tai
  kommentteihin, missä koordinaatistossa arvo on (`p_maailma`,
  `n_kamera`). Valaistusvirheet johtuvat useimmiten kahden eri
  koordinaatiston vektorin vertailusta.
- **Kerro matriisit kerran, kärjet monta kertaa.** `mvp` lasketaan
  kerran piirtokutsua kohden, ja jokainen kärki kerrotaan sillä.
- **Pisteet $w = 1$, suunnat $w = 0$.** Silloin siirto ei koske
  suuntia, eikä erillisiä funktioita tarvita.
- **Normaalit käänteismatriisin transpoosilla**, ellei skaalaus ole
  tasainen.
- **Tarkista rajapinnan sopimukset**: syvyysväli ($-1 \ldots 1$ vai
  $0 \ldots 1$), NDC:n $y$-suunta ja matriisien tallennusjärjestys
  (rivit vai sarakkeet) muistissa.

## Itsearviointi

- Osaat luetella koordinaatistot mallista ruutuun ja kertoa, mikä
  muunnos vie kustakin seuraavaan.
- Osaat koota mallimatriisin siirrosta, kierrosta ja skaalauksesta
  oikeassa järjestyksessä.
- Osaat selittää, mitä leikkausavaruuden $w$ tarkoittaa ja mitä
  perspektiivijako tekee.
- Osaat muuntaa normaalin oikein epätasaisesti skaalatussa mallissa.
