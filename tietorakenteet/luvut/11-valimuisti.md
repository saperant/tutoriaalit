# Välimuisti ja datan asettelu

Edellisten lukujen hinnat on laskettu operaatioina: vertailuja,
kopioita, kokeiluja. Malli olettaa, että jokainen muistihaku maksaa
saman verran. Nykyisessä suorittimessa näin ei ole. Rekisteri on
käytettävissä heti, ensimmäisen tason välimuisti muutamassa
kellojaksossa, ja keskusmuistiin kestää noin sata nanosekuntia –
satoja kellojaksoja, joiden aikana suoritin voisi tehdä satoja
laskutoimituksia. Siksi kaksi rakennetta, joilla on sama
O-merkinnän hinta, voivat erota nopeudeltaan kertaluokan verran.

## Välimuistirivit

Suoritin ei hae muistista yksittäisiä tavuja vaan *välimuistirivejä*,
x86-64:ssä ja useimmissa ARM-suorittimissa 64 tavua kerrallaan. Kun
ohjelma lukee yhden `int`-arvon, samalla rivillä olevat 15 seuraavaa
tulevat välimuistiin ilmaiseksi. Lisäksi suoritin tunnistaa
säännölliset hakukuviot ja hakee seuraavat rivit etukäteen
(engl. prefetching) ennen kuin ohjelma pyytää niitä.

Molemmat mekanismit palkitsevat samaa asiaa: *paikallisuutta*. Data,
jota käytetään peräkkäin, kannattaa sijoittaa muistiin peräkkäin.
Taulukko on paikallisuuden ihanne. Linkitetty lista, jonka solmut ovat
hajallaan, on sen vastakohta: jokainen solmu on todennäköisesti eri
rivillä, eikä seuraavan solmun osoitetta tiedetä ennen kuin edellinen
on luettu, joten etukäteishaku ei auta.

## Rivinvaihtojen laskeminen

Ajoitusmittaukset riippuvat koneesta, kuormasta ja kääntäjästä, joten
niitä ei voi verrata testissä tarkkaan tulokseen. Välimuistin
vaikutuksen voi kuitenkin mitata deterministisesti laskemalla, kuinka
monta kertaa läpikäynti siirtyy riviltä toiselle. Luku on alaraja
välimuistihuteille, jos data ei mahdu välimuistiin:

```{.c tiedosto="esimerkit/11-asettelu.c" osa="laskuri"}
```

Sama 65 536 kokonaisluvun data on taulukossa ja linkitetyssä
listassa. Listan solmut ovat yhdessä taulukossa mutta satunnaisessa
järjestyksessä, kuten käy, kun solmuja on lisätty ja poistettu
pitkään. Muistialueet varataan 64 tavun rajalle `aligned_alloc`-
funktiolla, jotta tulos ei riipu varaajan sijoittelusta:

```{.c tiedosto="esimerkit/11-asettelu.c" osa="taulukko"}
```

Taulukon läpikäynti vaihtaa riviä 4096 kertaa – kerran 16 luvun
välein. Lista vaihtaa riviä lähes jokaisella solmulla. Solmu on 16
tavua, joten neljä solmua mahtuu riville, mutta satunnaisessa
järjestyksessä peräkkäiset solmut ovat lähes aina eri riveillä:

```{.tuloste tiedosto="esimerkit/11-asettelu.odotettu"}
```

Listan läpikäynti koskettaa siis 16 kertaa enemmän rivejä, ja vielä
pahempaa on, että rivit haetaan yksi kerrallaan, koska seuraavan
solmun osoite on edellisen solmun sisällä.

## Ajoitus väljällä rajalla

Laskuri kertoo, montako riviä haetaan, mutta ei sitä, paljonko se
maksaa. Sen näkee vain ajoittamalla. Ajoitusmittaus on erillinen
ohjelma, joka käännetään optimoinneilla (`-O2`) ilman sanitoijia,
koska ne vääristäisivät tuloksen. Dataa on 2 miljoonaa `long`-arvoa
(32 Mt solmuina), jotta se ei mahdu välimuistiin:

```{.c tiedosto="esimerkit/mittaus/src/aika.c" osa="mittaus"}
```

Ohjelma ottaa parhaan viidestä toistosta ja tulostaa vain sen, onko
lista vähintään kolme kertaa hitaampi. Tarkat ajat menevät
virhetulosteeseen, jota ei verrata:

```{.tuloste tiedosto="esimerkit/mittaus/aika.odotettu"}
```

Raja on tarkoituksella väljä: tyypillisellä työasemalla lista on
50–200 kertaa hitaampi, joten raja ei petä kuormitetullakaan koneella.
Erään testikoneen ajossa taulukon summa vei noin kaksi millisekuntia ja listan
yli 250 millisekuntia. Molemmat tekevät saman määrän yhteenlaskuja;
ero on kokonaan muistihaun hinnassa. Mittaus ajetaan komennolla
`make -C esimerkit`.

## Tietuetaulukko vai kenttätaulukot?

Sama periaate pätee tietueiden sisällä. Tavallinen tapa tallentaa
hiukkassimulaation data on *tietuetaulukko* (engl. array of structures,
AoS): taulukko, jonka jokainen alkio on kaikki yhden hiukkasen kentät.
Vaihtoehto on *kenttätaulukot* (engl. structure of arrays, SoA): oma
taulukko kullekin kentälle. Samoista asetteluista käytetään myös
nimiä rakenteiden taulukko ja taulukoiden rakenne, esimerkiksi taidossa
*Suorituskyvyn analyysi ja optimointi*, joka mittaa eron
suorituskykylaskureilla.

```{.c tiedosto="esimerkit/11-asettelu.c" osa="tietue"}
```

Jos silmukka käsittelee kaikkia kenttiä, asettelulla ei ole suurta
väliä. Mutta jos se tarvitsee vain yhtä – esimerkiksi laskee
x-koordinaattien summan – tietuetaulukko tuo välimuistiin myös seitsemän
tarpeetonta kenttää. Esimerkissä varataan kenttätaulukoista vain
x-kenttä, koska vain sitä käytetään:

```{.c tiedosto="esimerkit/11-asettelu.c" osa="asettelu"}
```

Tietuetaulukko vaihtaa riviä 32 768 kertaa (kaksi hiukkasta riviä
kohti), kenttätaulukko 4096 kertaa (16 lukua riviä kohti). Kahdeksan
kertaa vähemmän muistiliikennettä ilman ainoatakaan algoritmista
muutosta. Kenttätaulukot sopivat myös vektorikäskyille (SIMD), jotka
käsittelevät 4–16 peräkkäistä samantyyppistä arvoa kerralla.
Tietokantojen sarakepohjainen tallennus ja pelimoottorien
entiteettijärjestelmät perustuvat samaan havaintoon.

## Mitä tämä tarkoittaa rakenteille

| Rakenne | Paikallisuus | Parannuskeino |
|---------|--------------|---------------|
| vektori | erinomainen | – |
| linkitetty lista | huono | solmut yhdestä taulukosta, tai vektori |
| ketjutettu hajautustaulu | huono (solmu avainta kohti) | avoin osoitteistus |
| avoin osoitteistus | hyvä (kokeilut peräkkäin) | tilatavut erikseen, SIMD-vertailu |
| hakupuu | huono (polku osoittimia) | B-puu: monta avainta solmussa |
| binäärikeko | hyvä ylätasoilla | leveämpi keko (4 lasta) |
| vierekkäisyyslistat | huono | CSR |

Kaksi yleistä sääntöä seuraa. Ensinnäkin pienillä $n$:n arvoilla
lineaarinen haku taulukosta voittaa usein puun ja hajautustaulun,
koska koko taulukko on muutamalla välimuistirivillä ja haku etenee
ennustettavasti. Raja on tyypillisesti kymmenistä satoihin alkioihin,
ja se on aina mitattava. Toiseksi linkitetyn rakenteen saa usein
nopeammaksi varaamalla solmut yhdestä taulukosta (*muistialtaasta*,
engl. pool) ja käyttämällä osoittimien tilalla 32-bittisiä indeksejä,
mikä myös pienentää solmuja.

Tarkemmat työkalut – suorituskykylaskurit (`perf stat -e
cache-misses`), välimuistisimulaattorit ja mikrovertailujen sudenkuopat
– kuuluvat taitoon *Suorituskyvyn analyysi ja optimointi*.

## Käytännössä

- **Taulukko ensin.** Valitse linkitetty rakenne vain, kun tarvitset
  sen ominaisuutta (pysyvät osoittimet, vakioaikainen irrotus).
- **Mittaa rivinvaihdot tai laskurit, ei pelkkiä aikoja.** Ne ovat
  deterministisiä ja selittävät, *miksi* jokin on hidas.
- **Ajoitukset optimoidulla käännöksellä ja väljällä rajalla.** Paras
  monesta toistosta, ja tulos vertailuna, ei tarkkana lukuna.
- **Kenttätaulukot, kun silmukka käyttää harvoja kenttiä.**
  Tietuetaulukko, kun kaikkia kenttiä käytetään yhdessä.
- **Kuumat kentät yhteen.** Usein luetut kentät tietueen alkuun ja
  harvoin käytetyt erilliseen rakenteeseen, jotta kuuma osa mahtuu
  yhdelle riville.

## Itsearviointi

- Osaat selittää, mikä välimuistirivi on ja miksi peräkkäinen
  läpikäynti on nopeampi kuin osoittimien seuraaminen.
- Osaat laskea, montako riviä taulukon ja tietuetaulukon läpikäynti
  koskettaa.
- Osaat kirjoittaa ajoitusmittauksen, joka on luotettava kuormitetulla
  koneella, koska se vertaa väljällä rajalla.
- Osaat valita tietuetaulukon ja kenttätaulukoiden välillä sen
  perusteella, mitä kenttiä silmukka käyttää.
