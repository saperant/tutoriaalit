# Kiihdytysrakenteet

Raakahaku testaa jokaisen säteen jokaista kolmiota vastaan. Kun
kohtauksessa on miljoona kolmiota ja kuvassa kaksi miljoonaa
pikseliä, ensimmäinen säde pikseliä kohden vaatii $2 \cdot 10^{12}$
leikkaustestiä, ja polunseuranta kymmeniä säteitä pikseliä kohden.
Kiihdytysrakenne järjestää kolmiot niin, että säde testaa vain
niitä, joiden lähellä se kulkee, ja hakuaika putoaa lineaarisesta
logaritmiseen.

Kiihdytysrakenteita on kahta päätyyppiä. *Avaruuden jako* (ruudukko,
oktopuu, kd-puu) jakaa tilan osiin ja luettelee kunkin osan kolmiot;
sama kolmio voi kuulua useaan osaan. *Kappaleiden jako* jakaa kolmiot
ryhmiin ja rajaa kunkin ryhmän laatikolla; laatikot voivat olla
päällekkäin, mutta jokainen kolmio on yhdessä ryhmässä. Jälkimmäinen,
rajaavien laatikoiden hierarkia eli BVH (*bounding volume hierarchy*),
on nykyään vallitseva: se on helppo rakentaa, päivittää liikkuville
kappaleille ja toteuttaa laitteistossa. Näytönohjainten
säteenseurantayksiköt käyvät läpi juuri BVH:ta.

## Rakenne

BVH on binääripuu. Sisäsolmulla on laatikko, joka rajaa sen molemmat
lapset, ja lehdellä laatikko ja muutama kolmio. Solmut ovat yhdessä
taulukossa, lapset vierekkäin, joten lapsen indeksi riittää
osoittimen sijaan. Kolmioita ei kopioida: lehdet viittaavat
järjestystaulukon väliin, ja rakentaminen järjestää sen niin, että
jokaisen lehden kolmiot ovat peräkkäin.

![Kahdeksan kolmion BVH tasossa: vasemmalla sisäkkäiset laatikot,
oikealla sama puuna. Saman tason laatikot ovat samanvärisiä.
Laatikot voivat mennä päällekkäin, mutta jokainen kolmio kuuluu
yhteen lehteen.](kuvat/04-bvh-periaate.png){width=90%}

```{.cpp tiedosto="esimerkit/yhteinen/bvh.hpp" osa="rakenne"}
```

Laatikoiden yhdisteessä on helppo tehdä virhe. Tyhjä laatikko on käänteinen: minimi $+\infty$
ja maksimi $-\infty$. Kun kaksi laatikkoa yhdistetään laajentamalla
ensimmäistä toisen kulmilla, tyhjän laatikon "kulmat" ovat
äärettömyyksiä, ja tuloksesta tulee ääretön. Oikea yhdiste ottaa
minimeistä minimin ja maksimeista maksimin, jolloin tyhjä laatikko on
neutraalialkio. Virhe ei kaada ohjelmaa eikä muuta kuvaa. Se
huonontaa puuta: SAH-jaossa jokainen tyhjä lokero tekee jaosta
äärettömän kalliin, ja lehdistä tulee kymmenien kolmioiden kokoisia.
Sen paljastavat vain laskurit:

```{.cpp tiedosto="esimerkit/yhteinen/sade.hpp" osa="yhdiste"}
```

## Rakentaminen ylhäältä alas

Rakentaminen on hajota ja hallitse -algoritmi. Solmun kolmiot jaetaan
kahteen joukkoon jonkin akselin suuntaisen tason mukaan: kolmio
kuuluu vasemmalle, jos sen keskipiste on tason vasemmalla puolella.
Jako tehdään paikallaan `std::partition`illa, ja kumpikin puolisko
käsitellään rekursiivisesti. Rekursio päättyy lehteen, kun kolmioita
on vähän tai jako ei erottele niitä.

```{.cpp tiedosto="esimerkit/yhteinen/bvh.hpp" osa="rakenna"}
```

Yksinkertaisin jakotaso on keskipisteiden laatikon pisimmän akselin
puoliväli. Se on nopea laskea ja toimii tasaisesti jakautuneille
kolmioille, mutta tuottaa huonon puun, kun kolmiot ovat
epätasaisesti: suuren tyhjän tilan ja tiheän esineen raja ei osu
puoliväliin.

## Pinta-alaheuristiikka

Parempi jako minimoi säteen odotetun työn. Jos säteet tulevat
satunnaisista suunnista, todennäköisyys, että säde osuu kuperaan
kappaleeseen, kun se osuu sen sisältävään kappaleeseen, on
pinta-alojen suhde (Cauchyn kaava). Jaon odotettu hinta on silloin

$$C = C_\text{läpi} + \frac{A_V}{A}\,N_V\,C_\text{kolmio} +
\frac{A_O}{A}\,N_O\,C_\text{kolmio},$$

missä $A$ on solmun laatikon pinta-ala, $A_V$ ja $A_O$ lasten
laatikoiden pinta-alat ja $N_V$, $N_O$ lasten kolmioiden määrät.
Lehden hinta on $N\,C_\text{kolmio}$. Pinta-alaheuristiikka eli SAH
(*surface area heuristic*) kokeilee useita jakotasoja ja valitsee
halvimman, tai tekee lehden, jos jakaminen ei kannata.

Kaikkien mahdollisten tasojen kokeileminen on hidasta, joten
keskipisteet lajitellaan kahteentoista lokeroon akselia kohden, ja
jakotasoja kokeillaan vain lokeroiden rajoilla (Wald 2007):

```{.cpp tiedosto="esimerkit/yhteinen/bvh.hpp" osa="sah"}
```

Vakioiden suhde $C_\text{läpi} / C_\text{kolmio}$ ratkaisee, kuinka
suuria lehdistä tulee. Ensimmäinen versio käytti suhdetta 1, ja
melkein tasaiselle maastolle jako ei koskaan kannattanut: jos
kolmiot ovat tasossa, kummankin puoliskon laatikko on puolet
alkuperäisestä, ja hinta on $1 + N/2 + N/2 > N$. Ahne heuristiikka ei
näe, että seuraavat jaot kannattaisivat. Siksi tässä
$C_\text{läpi} = 1/8$, ja yli kahdeksan kolmion solmu jaetaan aina.

## Läpikäynti

Säde käy puun läpi pinolla. Juuren laatikko testataan ensin. Jos säde
osuu sisäsolmun laatikkoon, testataan molemmat lapset, ja lähempi
käsitellään ensin. Kun osuma löytyy, se lyhentää väliä
$(0, t_\text{max})$, jolloin kauempana alkavat laatikot ohitetaan
laskematta mitään:

```{.cpp tiedosto="esimerkit/yhteinen/bvh.hpp" osa="lapikaynti"}
```

Lähempi ensin -järjestys on tärkeä: jos lähin osuma löytyy
ensimmäisestä lapsesta, toisen laatikko alkaa usein sen takana ja
jää kokonaan käsittelemättä. Varjosäteelle järjestys on yhdentekevä,
koska mikä tahansa osuma riittää, ja läpikäynnin voi lopettaa
ensimmäiseen osumaan.

## Vertailu

Kohtauksessa on laaja, harva maasto ja sen keskellä tiheä pallo,
yhteensä 3 072 kolmiota:

```{.cpp tiedosto="esimerkit/04-bvh.cpp" osa="kohtaus"}
```

Sama kuva renderöidään raakahaulla ja kahdella BVH:lla, ja
laskurit kertovat, montako laatikkoa ja kolmiota säde keskimäärin
testasi:

```{.cpp tiedosto="esimerkit/04-bvh.cpp" osa="raaka"}
```

```{.cpp tiedosto="esimerkit/04-bvh.cpp" osa="vertailu"}
```

```{.cpp tiedosto="esimerkit/04-bvh.cpp" osa="main"}
```

Kuvien on oltava täsmälleen samat, koska BVH vain karsii testejä
eikä muuta yhtäkään leikkausta. Tarkistussumma varmistaa sen kaikille
768 pikselille. Satunnaiset säteet joka suunnasta testaavat
tapaukset, joita kamera ei näe, kuten säteet maaston alta:

```{.cpp tiedosto="esimerkit/04-bvh.cpp" osa="satunnaiset"}
```

```{.tuloste tiedosto="esimerkit/04-bvh.odotettu"}
```

![Vasemmalla kohtaus SAH-puulla renderöitynä, oikealla
laatikkotestien määrä pikseleittäin: musta 0, punainen 30, keltainen 60
ja valkoinen vähintään 90 testiä. Kalleimpia ovat säteet, jotka
hipovat pallon reunaa tai maaston pintaa: ne käyvät läpi monta
laatikkoa osumatta mihinkään.](kuvat/04-bvh.png){width=95%}

Raakahaku testaa jokaista 3 072 kolmiota; BVH:t testaavat noin
kahta kolmiota ja 16–19 laatikkoa. Laatikkotesti on halvempi kuin
kolmiotesti, joten työ pienenee yli sataan osaan. Ero kasvaa
kohtauksen mukana, sillä puun syvyys kasvaa logaritmisesti.
Kameran säteille kahden puun ero on pieni, koska ne kulkevat
kaikki samasta pisteestä samaan suuntaan. Satunnaisille säteille
SAH-puu testaa noin 15 % vähemmän laatikoita, ja se on myös
matalampi (15 tasoa 21:n sijaan). Suuremmissa ja epätasaisemmissa
kohtauksissa ero kasvaa moninkertaiseksi.

Lukuja kannattaa verrata laskureina eikä aikoina. Laskurit ovat
deterministiset ja riippumattomia koneesta, kääntäjästä ja
sanitoijista; aika riippuu kaikista niistä. Kun algoritmi on oikein,
aikaa mitataan erikseen optimoidulla käännöksellä (taito
*Suorituskyvyn analyysi ja optimointi*).

## Muita rakenteita ja tekniikoita

- **Ruudukko** jakaa tilan tasaisiin soluihin. Se on nopea rakentaa,
  mutta solukoon valinta on vaikea, kun kohtauksessa on sekä suuria
  että pieniä kappaleita.
- **kd-puu** jakaa tilaa akselien suuntaisilla tasoilla. Se oli
  pitkään nopein rakenne staattisille kohtauksille, mutta sen
  rakentaminen on hitaampaa ja muistinkulutus vaikeammin ennustettavaa
  kuin BVH:n.
- **Kaksitasoinen BVH**: jokaisella mallilla on oma puu (alataso), ja
  ylätaso sisältää mallien instanssit muunnosmatriiseineen.
  Liikkuvat kappaleet päivittävät vain ylätasoa. Vulkanin ja
  DirectX:n säteenseurantarajapinnat käyttävät juuri tätä jakoa.
- **Leveät puut**: neljä tai kahdeksan lasta solmua kohden, jolloin
  lasten laatikot testataan yhdellä SIMD-käskyllä.
- **Lineaarinen BVH** järjestää kolmiot Mortonin koodin mukaan ja
  rakentaa puun järjestyksestä. Se on hyvin nopea rakentaa myös
  näytönohjaimella, mutta puu on huonompi kuin SAH:lla.

## Käytännössä

- **Käytä BVH:ta ja SAH-jakoa.** Keskikohtajako kelpaa nopeaan
  rakentamiseen, mutta SAH tuottaa paremman puun samaan hintaan
  kertaluokassa.
- **Testaa kiihdytysrakenne raakahakua vastaan.** Saman kuvan
  tarkistussumma ja satunnaiset säteet paljastavat puuttuvat osumat,
  jotka muuten näkyisivät satunnaisina reikinä.
- **Mittaa laskureilla.** Testien määrä säteeltä kertoo puun laadun
  koneesta riippumatta.
- **Käy lähempi lapsi ensin** ja lyhennä väliä jokaisen osuman
  jälkeen. Varjosäteelle riittää ensimmäinen osuma.
- **Tarkista tyhjät tapaukset**: tyhjä laatikko, tyhjä lokero ja
  kolmiot, joiden keskipisteet ovat samassa kohdassa.

## Itsearviointi

- Osaat kuvata BVH:n rakenteen ja rakentaa sen ylhäältä alas
  keskikohtajaolla ja SAH-jaolla.
- Osaat perustella pinta-alaheuristiikan todennäköisyyspäättelyllä
  ja selittää läpikäynti- ja kolmiotestin hintasuhteen vaikutuksen.
- Osaat toteuttaa läpikäynnin pinolla niin, että lähempi lapsi
  käsitellään ensin ja kauempana alkavat solmut ohitetaan.
- Osaat testata kiihdytysrakenteen raakahakua vastaan ja vertailla
  rakenteita deterministisillä laskureilla.
