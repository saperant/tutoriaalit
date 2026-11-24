# Johdanto {.runko-johdanto}

Liukuluku on ohjelmoijalle mukava: se kattaa valtavan arvoalueen, ja
pyöristys tapahtuu automaattisesti. Laitteistossa mukavuudella on hinta.
Liukulukusummain tarvitsee eksponenttien vertailun, mantissan
kohdistussiirron, normalisoinnin ja pyöristyslogiikan, ja se vie monta
kertaa enemmän pinta-alaa ja energiaa kuin saman levyinen
kokonaislukusummain. Siksi signaalinkäsittelyn kiihdyttimet,
radiolaitteiden datapolut, äänikoodekit, moottorinohjaimet ja monet
neuroverkkokiihdyttimet laskevat *kiinteän pilkun* luvuilla.

Kiinteän pilkun luku on tavallinen kokonaisluku, jonka suunnittelija
tulkitsee murtoluvuksi: binääripilkun paikka on sovittu etukäteen eikä
tallennu lukuun. Laitteiston kannalta se on pelkkä bittivektori, ja
summain ja kertoja ovat samoja kuin kokonaisluvuille. Kaikki vaikeus on
suunnittelijan päässä. Hänen on päätettävä, montako bittiä kukin signaali
tarvitsee, missä pilkku on, miten tulokset pyöristetään ja mitä
tapahtuu, kun arvo ei mahdu.

Tämä tutoriaali opettaa nuo päätökset:

- **Q-formaatit:** arvoalue, tarkkuus ja muunnokset muodosta toiseen.
- **Aritmetiikka:** bittikasvu summissa, tuloissa ja kertymissä sekä
  vartijabitit.
- **Pyöristys ja ylivuoto:** pyöristystapojen harha mitattuna,
  saturaatio vai kierto.
- **Kvantisointivirhe:** SQNR, 6 dB:n sääntö ja kertoimien
  kvantisointi.
- **Bittitarkat mallit:** sama algoritmi C:llä ja Pythonilla bitilleen
  samaan tulokseen sekä vertailu double-referenssiin.
- **Suunnittelu:** kiinteä pilkku vai liukuluku, lohkoliukuluku,
  sanaleveyksien valinta virhebudjetilla ja yleiset sudenkuopat.

Tutoriaali rakentuu taitojen *Digitaalitekniikka* ja *Miten tietokone
laskee* päälle. Kahden komplementti, liukulukujen rakenne ja
int8-kvantisointi oletetaan tutuiksi; tässä ne nähdään
laitteistosuunnittelijan silmin. Jatkotaidot *Korkean tason mallinnus
(SystemC/TLM)* ja *DSP-algoritmien laitteistototeutus* käyttävät tämän
tutoriaalin bittitarkkoja malleja RTL:n referenssinä.

## Ensimmäinen kiinteän pilkun luku

Yleisin kiinteän pilkun muoto on Q1.15: 16-bittinen etumerkillinen
kokonaisluku, jonka arvo on koodi jaettuna luvulla $2^{15}$. Se esittää
välin $[-1, 1)$ tasaisin askelin $2^{-15} \approx 3{,}05 \cdot 10^{-5}$.
Muunnos liukuluvusta on kertolasku, pyöristys ja tarvittaessa
leikkaus alueelle:

```{.c tiedosto="esimerkit/01-ensimmainen.c" osa="q15"}
```

```{.c tiedosto="esimerkit/01-ensimmainen.c" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/01-ensimmainen.odotettu"}
```

Taulukosta näkyvät kiinteän pilkun perusominaisuudet. Kahden potenssin
murtoluvut, kuten 0,5 ja −0,25, ovat tarkkoja. Luku 0,3 pyöristyy
lähimpään koodiin, ja virhe on alle puoli LSB:tä (*least significant
bit*, pienimmän bitin paino). Arvo −1 mahtuu, mutta +1 ei: suurin
esitettävä arvo on $1 - 2^{-15}$, joten 1,0 *saturoituu* koodiin 32767.
Hyvin pieni luku pyöristyy nollaksi, koska tarkkuus on absoluuttinen:
jokaisen arvon virhe on samaa kokoluokkaa riippumatta siitä, kuinka suuri
arvo on.

## Työkalut ja esimerkit

Esimerkit ovat C:tä ja Pythonia. C-esimerkit käännetään GCC 14:llä ja
Clang 20:llä C23-standardin mukaan varoitukset virheinä,
AddressSanitizerin ja UndefinedBehaviorSanitizerin kanssa, joten
määrittelemätön ylivuoto pysäyttää ohjelman. C on lähellä
laitteistoa: kiinteän leveyden tyypit (`int16_t`, `int32_t`, `int64_t`)
vastaavat rekisterien ja väylien leveyksiä. Python-esimerkit tarkistetaan
ruffilla ja mypyllä (`--strict`). Pythonin kokonaisluvut ovat
rajoittamattomia, joten bittitarkka malli on helppo kirjoittaa ilman
ylivuotoja, ja NumPy laskee kohinan ja taajuusvasteet.

Kaikki tulosteet ovat deterministisiä: testisignaalit tuotetaan
siniaalloista tai omalla kongruenssigeneraattorilla, ei
satunnaislukukirjastolla.
