# Dynaaminen taulukko

Dynaaminen taulukko (vektori) on käytännössä tärkein tietorakenne. Se
on yhtenäinen muistialue, jonka alkioihin pääsee indeksillä vakioajassa
ja joka kasvaa tarpeen mukaan. C-kielen muistinhallintaluvussa rakennettiin kasvava
taulukko `realloc`-funktiolla; tässä luvussa tarkastellaan, *miten*
taulukon kannattaa kasvaa ja miksi oikea strategia tekee lisäyksestä
keskimäärin vakioaikaisen.

## Kasvatusstrategiat

Kun taulukko on täynnä, varataan suurempi alue ja vanhat alkiot
kopioidaan sinne. Kysymys on, kuinka paljon suurempi. Neljä
vaihtoehtoa:

```{.c tiedosto="esimerkit/03-kasvatus.c" osa="strategiat"}
```

Kopioiden määrän voi laskea suoraan, ilman oikeaa muistia. Malli
lisää $n$ alkiota yksi kerrallaan ja kirjaa, montako alkiota kukin
kasvatus siirtää:

```{.c tiedosto="esimerkit/03-kasvatus.c" osa="malli"}
```

```{.tuloste tiedosto="esimerkit/03-kasvatus.odotettu"}
```

Ero on valtava. Kun kapasiteetti kasvaa vakiomäärällä $c$, kopioita on

$$c + 2c + 3c + \dots \approx \frac{n^2}{2c},$$

eli kopioita alkiota kohti on $O(n)$: sata tuhatta alkiota tuottaa
lähes viisi miljardia kopiota yhden alkion lisäyksellä ja 78 miljoonaa
64 alkion lisäyksellä. Kun kapasiteetti kerrotaan vakiolla $k > 1$,
kopioiden summa on geometrinen sarja:

$$n + \frac{n}{k} + \frac{n}{k^2} + \dots = n \cdot \frac{k}{k - 1}.$$

Tuplauksella ($k = 2$) kopioita on enintään $2n$, kertoimella 1,5
enintään $3n$. Mittaus vahvistaa: 1,31 ja 2,76 kopiota alkiota kohti.

## Tasoitettu aika

Yksittäinen lisäys voi olla kallis: se, joka laukaisee kasvatuksen,
kopioi koko taulukon. Mutta kalliit lisäykset ovat harvinaisia, ja
niiden hinta jakautuu kaikille lisäyksille. Tätä sanotaan
*tasoitetuksi* (engl. amortized) ajaksi: $n$ lisäyksen kokonaishinta on
$O(n)$, joten lisäys maksaa keskimäärin $O(1)$ – pahimmassakin
lisäysjonossa, ei vain odotusarvoisesti.

Tasoitettu vakioaika ei tarkoita, että jokainen lisäys on nopea.
Reaaliaikajärjestelmässä, jossa yksikään operaatio ei saa kestää
liian kauan, kasvatus on varattava etukäteen (`vektori_varaa`) tai
käytettävä rakennetta, joka ei koskaan kopioi kaikkea kerralla.

## Kertoimen valinta

Taulukon viimeinen sarake näyttää kasvatuksen hinnan toisen puolen:
varattu mutta käyttämätön tila. Tuplauksessa enintään puolet ja
keskimäärin noin neljännes kapasiteetista on hukkaa; kertoimella 1,5
enintään kolmannes. Suurempi kerroin tarkoittaa vähemmän kopioita ja
enemmän hukkaa.

Kertoimella 1,5 on lisäksi käytännön etu: vapautetut vanhat alueet
ovat yhteensä pian riittävän suuria uutta taulukkoa varten, jolloin
muistinvaraaja voi käyttää niitä uudelleen. Tuplauksessa uusi alue on
aina suurempi kuin kaikki aiemmat yhteensä. MSVC:n `std::vector` ja
Javan `ArrayList` käyttävät kerrointa 1,5, libstdc++ ja libc++
kerrointa 2. glibc:n `realloc` taas pystyy usein kasvattamaan suuren alueen paikallaan, jolloin kopiointia
ei tapahdu lainkaan.

## Vektorin toteutus

Toteutus pitää kirjaa käytetystä koosta ja varatusta kapasiteetista.
Invariantti on yksinkertainen:

```{.c tiedosto="esimerkit/03-vektori.c" osa="rakenne"}
```

Lisäys varmistaa ensin tilan. Kasvatukseen lisätään vakio 8, jotta
tyhjä taulukko ei kasva yhden alkion askelin:

```{.c tiedosto="esimerkit/03-vektori.c" osa="lisaa"}
```

Poistossa on kaksi vaihtoehtoa. Jos järjestys on tärkeä, loppuosa
siirretään yhden paikan verran ($O(n)$). Jos ei, aukkoon siirretään
viimeinen alkio ($O(1)$):

```{.c tiedosto="esimerkit/03-vektori.c" osa="poista"}
```

```{.tuloste tiedosto="esimerkit/03-vektori.odotettu"}
```

Pääohjelma poistaa virheelliset näytteet käymällä taulukkoa läpi
*lopusta alkuun*. Silloin poisto ei siirrä alkioita, joita ei ole vielä
käsitelty. Jos poistettavia on paljon, parempi tapa on yksi läpikäynti
kahdella indeksillä: lukuindeksi käy kaikki alkiot ja kirjoitusindeksi
kopioi säilytettävät taulukon alkuun. Silloin koko suodatus on $O(n)$.

Vektori ei pienene automaattisesti. Kutistamisen kanssa on oltava
varovainen: jos taulukko puolitetaan heti, kun se on puoliksi tyhjä,
vuorotellen lisäävä ja poistava ohjelma voi kopioida koko taulukon joka
operaatiolla. Turvallinen sääntö on kutistaa vasta, kun koko on
pudonnut neljännekseen kapasiteetista.

## Roikkuvat osoittimet

Kasvatuksella on seuraus, joka yllättää usein: `realloc` voi siirtää
datan uuteen paikkaan. Kaikki osoittimet vanhaan alueeseen ovat sen
jälkeen virheellisiä:

```{.c tiedosto="esimerkit/03-mitatoityminen.kaatuu.c"}
```

AddressSanitizer pysäyttää ohjelman:

```{.tuloste tiedosto="esimerkit/03-mitatoityminen.virhe"}
```

Ilman sanitoijaa ohjelma luultavasti tulostaisi luvun 10, koska
vapautettua muistia ei ole vielä käytetty muuhun. Virhe paljastuisi
vasta myöhemmin, kun muisti on varattu uudelleen ja luettu arvo on
jotain aivan muuta. Siksi dynaamiseen taulukkoon viitataan
*indeksillä*, ei osoittimella, aina kun taulukko voi kasvaa viittauksen
elinaikana.

## Käytännössä

- **Kasvata kertomalla, älä lisäämällä.** Kerroin 1,5–2 antaa
  tasoitetun vakioajan; vakiolisäys tekee lisäyksestä lineaarisen.
- **Varaa etukäteen, kun koko tiedetään.** Yksi `vektori_varaa(v, n)`
  ennen silmukkaa poistaa kaikki kasvatukset.
- **Indeksi, ei osoitin.** Taulukon sisäinen osoitin elää vain siihen
  asti, kun taulukkoa seuraavan kerran kasvatetaan.
- **Poisto vaihtamalla,** kun järjestyksellä ei ole väliä: $O(1)$
  siirron $O(n)$ sijaan.
- **Laske kapasiteetin ylivuoto.** Tuotantokoodissa tarkista, ettei
  `uusi * sizeof *data` vuoda yli (`ckd_mul` C23:n
  `<stdckdint.h>`-otsakkeesta).

## Itsearviointi

- Osaat laskea, montako kopiota $n$ lisäystä aiheuttaa vakiolisäyksellä
  ja kertoimella kasvatettaessa.
- Osaat selittää, mitä tasoitettu vakioaika tarkoittaa ja mitä se ei
  lupaa yksittäisestä operaatiosta.
- Osaat toteuttaa kasvatuksen niin, että muistin loppuminen jättää
  vektorin ennalleen.
- Osaat kertoa, miksi osoitin vektorin sisään voi mitätöityä ja miten
  virheen voi välttää.
