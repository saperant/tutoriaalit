# Reduktio

**Reduktio** yhdistää taulukon yhdeksi arvoksi liitännäisellä
operaatiolla: summa, tulo, minimi, maksimi tai looginen tai. CPU:lla se
on yksi silmukka. GPU:lla miljoonat alkiot jaetaan tuhansille
säikeille, jotka summaavat osia rinnakkain, ja osasummat yhdistetään
puuna. Reduktio on rinnakkaisten primitiivien yksinkertaisin, mutta
siinä näkyvät kaikki GPU-algoritmien perusongelmat: työn jako,
tahdistus työryhmän sisällä, riippuvuus työryhmien välillä ja
liukulukujen laskujärjestys.

Esimerkki summaa noin 4,2 miljoonaa kokonaislukua kolmella tavalla ja
vertaa tuloksia CPU:lla laskettuun summaan:

```{.tuloste tiedosto="esimerkit/04-reduktio.odotettu"}
```

## Atominen summa

Suorin tapa on antaa jokaisen säikeen lisätä alkionsa yhteen
muistipaikkaan atomisella operaatiolla:

```{.glsl tiedosto="esimerkit/varjostimet/reduktio_atomi.comp" osa="atomi"}
```

Tulos on oikein, ja ajoja tarvitaan vain yksi. Jokainen 4,2 miljoonasta
lisäyksestä osuu kuitenkin samaan osoitteeseen, joten laitteisto
käsittelee ne peräkkäin. GPU:n atomiset operaatiot tehdään
välimuistissa (L2) lähellä muistia, ja yhden osoitteen läpäisy on
tyypillisesti yksi operaatio kellojaksoa kohden koko laitteelle.
Tuhansien kaistojen rinnakkaisuus katoaa. Luku 6 mittaa ilmiön
histogrammilla.

## Puu jaetussa muistissa

Tavallinen ratkaisu on kaksitasoinen. Jokainen työryhmä summaa oman
osansa jaetussa muistissa puuna ja kirjoittaa yhden osasumman. Puu
puolittaa aktiivisten säikeiden määrän jokaisella tasolla, ja tasojen
välissä on `barrier()`:

```{.glsl tiedosto="esimerkit/varjostimet/reduktio_jaettu.comp" osa="jaettu"}
```

![Sama puu kahdeksalle säikeelle ja 16 alkiolle. Värilliset solut
ovat tasolla aktiivisten säikeiden summat: aktiivisia on aina ryhmän
alusta 8, 4, 2 ja 1. Jokaisen tason jälkeen kaikki säikeet odottavat
esteellä.](kuvat/04-reduktiopuu.png){width=80%}

Kolme yksityiskohtaa on tärkeitä:

1. **Ensimmäinen yhteenlasku tehdään latauksessa.** Jokainen 256
   säikeestä lataa kaksi alkiota, joten työryhmä kattaa 512 alkiota.
   Jos säie latasi vain yhden, puolet säikeistä olisi toimettomana
   heti ensimmäisellä tasolla. Yleisemmin säie voi summata
   useita alkioita silmukassa ennen puuta (*thread coarsening*),
   jolloin työryhmiä ja osasummia on vähemmän.
2. **Aktiiviset säikeet ovat ryhmän alussa.** Ehto `oma < askel`
   pitää aktiiviset säikeet yhtenäisinä, joten kokonaiset aliryhmät
   lopettavat kerralla eivätkä hajaannu (luku 3). Varhainen versio,
   jossa ehto oli `oma % (2 * askel) == 0`, hajauttaa jokaisen
   aliryhmän jokaisella tasolla.
3. **`barrier()` on kaikkien säikeiden saavutettava.** Este on
   silmukassa, jonka kierrosmäärä on sama kaikille säikeille.
   Este ehtolauseen sisällä, jota vain osa säikeistä suorittaa, on
   määrittelemätöntä käytöstä ja jumittaa usein laitteen.

GLSL:n laskentavarjostimessa `barrier()` on sekä suoritus- että
muistieste jaetulle muistille: kaikki säikeet odottavat, ja niiden
jaettuun muistiin tekemät kirjoitukset näkyvät esteen jälkeen.
Luku 9 käsittelee esteitä tarkemmin.

### Työryhmien välinen riippuvuus

Työryhmä ei voi odottaa toisia saman ajon aikana. Osasummat summataan
siksi uudella ajolla, joka käyttää samaa varjostinta osasummien
taulukkoon. Jokainen ajo pienentää datan 512-osaan, joten 4,2
miljoonaa alkiota vaatii kolme ajoa (8 217 osasummaa, 17 osasummaa,
yksi summa):

```{.cpp tiedosto="esimerkit/04-reduktio.cpp" osa="monivaihe"}
```

Ajojen välissä on muistieste, koska seuraava ajo lukee edellisen
kirjoittamia osasummia. Kaikki ajot tallennetaan samaan
komentopuskuriin, joten CPU ei odota välissä. Ajojen välinen este
maksaa oikealla GPU:lla muutamia mikrosekunteja, koska edellisen ajon
kaikkien työryhmien on valmistuttava. Siksi viimeiset pienet vaiheet
tehdään joskus CPU:lla tai atomisella lisäyksellä: ensimmäinen ajo
kirjoittaa osasumman ja lisää sen samalla atomisesti
kokonaissummaan. Jokaista 512 alkiota kohden on silloin yksi atominen
operaatio, mikä ei enää sarjallista.

## Aliryhmäoperaatiot

Jaetun muistin puussa on yhdeksän tasoa ja yhdeksän estettä.
Aliryhmän summa `subgroupAdd` korvaa kahdeksan kaistan levyisellä
aliryhmällä kolme alinta tasoa, ja 32 kaistan aliryhmällä viisi.
Jaettuun muistiin kirjoitetaan vain aliryhmien summat, ja este
tarvitaan vain kerran:

```{.glsl tiedosto="esimerkit/varjostimet/reduktio_aliryhma.comp" osa="aliryhma"}
```

Ensimmäinen aliryhmä summaa aliryhmien summat. Silmukka käsittelee
tapauksen, jossa aliryhmiä on enemmän kuin kaistoja: lavapipellä 256
säikeen ryhmässä on 32 aliryhmää mutta kaistoja on 8. 32 kaistan
laitteella aliryhmiä on 8, ja silmukka tekee yhden kierroksen.

Mittaustilassa aliryhmäversio oli lavapipellä selvästi nopein
(noin 40–60 ms), atominen versio seuraavana (80–90 ms) ja jaetun
muistin puu hitain (100–200 ms). Jaetun muistin puun hitaus johtuu
lavapipen esteiden hinnasta (luku 3). Oikealla GPU:lla atominen versio
on yleensä selvästi hitain, ja aliryhmäversio on nopein, koska sen
nopeutta rajoittaa vain muistin kaista.

## Liukulukujen laskujärjestys

Liukulukujen yhteenlasku ei ole liitännäinen: $(a + b) + c$ ja
$a + (b + c)$ pyöristyvät eri tavoin. Rinnakkainen reduktio laskee
yhteenlaskut eri järjestyksessä kuin peräkkäinen silmukka, joten
tulokset eroavat. Esimerkki summaa 4,2 miljoonaa lukua väliltä
$[0, 1)$ peräkkäin CPU:lla ja puuna GPU:lla ja vertaa molempia
kaksoistarkkuudella laskettuun viitteeseen:

```{.cpp tiedosto="esimerkit/04-reduktio.cpp" osa="liukuluku"}
```

Peräkkäinen summa oli virheellisempi: noin $5 \cdot 10^{-5}$, kun
puusumman virhe oli noin $10^{-7}$. Kun summa kasvaa kahteen
miljoonaan, jokainen lisäys pyöristyy floatin 24 bitin tarkkuuteen
noin 0,1:n tarkkuudella, ja virheet kertyvät. Puussa yhteenlaskettavat
ovat aina samaa suuruusluokkaa, ja virhe kasvaa vain
logaritmisesti.

Tästä seuraa kaksi sääntöä. Ensinnäkin GPU:n tulosta ei voi verrata
CPU:n peräkkäiseen tulokseen tarkasti, vaan toleranssilla, ja
referenssi kannattaa laskea suuremmalla tarkkuudella. Toiseksi
liukulukureduktio on deterministinen vain, jos laskujärjestys on
kiinteä. Tämän luvun puu on deterministinen, koska jokainen osasumma
lasketaan samassa järjestyksessä joka ajossa. Atominen
liukulukusumma (`atomicAdd` floatille, laajennus
`VK_EXT_shader_atomic_float`) ei ole: järjestys riippuu siitä, missä
järjestyksessä työryhmät sattuvat valmistumaan, ja tulos voi vaihdella
ajosta toiseen viimeisissä biteissä.

## Käytännössä

- **Kaksitasoinen rakenne on perusmalli.** Ensin työryhmän sisäinen
  reduktio (aliryhmäoperaatiot ja jaettu muisti), sitten työryhmien
  välinen joko uudella ajolla tai yhdellä atomisella operaatiolla
  työryhmää kohden.
- **Säie tekee useamman alkion työn.** Säikeiden ja työryhmien määrä
  mitoitetaan laitteelle (muutama työryhmä laskentayksikköä kohden),
  ei datalle. Jokainen säie summaa silmukassa useita alkioita, mikä
  vähentää osasummia ja esteitä.
- **Referenssi kaksoistarkkuudella.** Liukulukujen vertailu tehdään
  suhteellisella toleranssilla tarkkaa viitettä vastaan. Jos
  bittitarkka toistettavuus on vaatimus, laskujärjestys kiinnitetään
  eikä liukulukuja lasketa atomisesti.
- **Kirjastot tekevät tämän valmiiksi.** CUB (NVIDIA), rocPRIM (AMD)
  ja oneDPL tarjoavat viritetyt reduktiot. Oma toteutus kannattaa,
  kun reduktio yhdistetään toiseen vaiheeseen (*kernel fusion*) ja
  välitulos jää kirjoittamatta muistiin.

## Itsearviointi

- Osaat toteuttaa reduktion puuna jaetussa muistissa ja selittää,
  miksi aktiivisten säikeiden on oltava ryhmän alussa ja miksi esteen
  on oltava kaikkien säikeiden saavutettavissa.
- Osaat yhdistää työryhmien osasummat monivaiheisesti ja kertoa,
  miksi työryhmät eivät voi odottaa toisiaan saman ajon aikana.
- Osaat korvata puun alimmat tasot aliryhmäoperaatioilla.
- Osaat selittää, miksi rinnakkainen liukulukusumma eroaa
  peräkkäisestä, ja valita oikean vertailutavan ja toleranssin.
