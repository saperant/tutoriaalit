# Ylivuoto ja tarkistettu aritmetiikka

Kiinteän leveyden aritmetiikka on aritmetiikkaa modulo $2^n$. Kun tulos
ei mahdu tyyppiin, ylimmät bitit putoavat pois: luvun 2 lukuympyrällä
kuljetaan sauman yli. Laitteisto tekee näin
kaikille kokonaisluvuille, mutta C-kieli kohtelee etumerkillisiä ja
etumerkittömiä tyyppejä eri tavalla.

## Etumerkillinen ylivuoto on määrittelemätöntä

Etumerkillisen kokonaisluvun ylivuoto on C:ssä *määrittelemätöntä
käyttäytymistä* (undefined behavior). Standardi ei lupaa kiertymistä
negatiiviseksi eikä mitään muutakaan, ja kääntäjä saa olettaa, ettei
ylivuotoa tapahdu. Optimoija esimerkiksi päättelee, että `x + 1 > x`
on aina tosi, ja poistaa tarkistuksen, joka yritti havaita ylivuodon
jälkikäteen.

Myyntien summa senteissä ylittää 32-bittisen `int`-tyypin rajan
(2 147 483 647 senttiä eli noin 21,5 miljoonaa euroa):

```{.c tiedosto="esimerkit/03-ylivuoto.kaatuu.c" osa="summa"}
```

```text
runtime error: signed integer overflow: 1800000000 + 900000000
cannot be represented in type 'int'
```

UndefinedBehaviorSanitizer pysäyttää ohjelman ylivuodon kohdalle. Ilman
sitä ohjelma tulostaisi todennäköisesti negatiivisen summan. Ilman
sanitoijaa virhe ei kuitenkaan näy, ennen kuin raportissa on
miinusmerkkinen myynti. Siksi testit ajetaan sanitoijien kanssa.

## Etumerkittömät tyypit kiertävät

Etumerkittömien tyyppien aritmetiikka on määritelty modulo $2^n$.
Kiertyminen on usein juuri sitä, mitä halutaan: järjestysnumerot,
aikaleimat ja tarkistussummat kiertävät tarkoituksella.

```{.c tiedosto="esimerkit/03-kiertava.c" osa="kierto"}
```

Kiertyvien laskurien vertailu tehdään erotuksella. Jos aikaleima
on kiertänyt nollaan, `nyt - edellinen` on silti oikea kulunut aika,
kunhan väli on alle $2^{32}$ millisekuntia. Järjestysnumeroiden
vertailu tulkitsee erotuksen etumerkillisenä (*serial number
arithmetic*, RFC 1982), kuten TCP tekee:

```{.c tiedosto="esimerkit/03-kiertava.c" osa="jarjestys"}
```

```{.tuloste tiedosto="esimerkit/03-kiertava.odotettu"}
```

Kiertyminen on virhe silloin, kun luku kuvaa määrää. Puolitushaun
keskikohta `(ala + yla) / 2` on klassinen esimerkki: summa ylittää
tyypin rajan, vaikka keskikohta mahtuu. Javan kirjastossa tämä virhe
oli vuosikausia.

```{.c tiedosto="esimerkit/03-keskikohta.c" osa="keskikohta"}
```

```{.tuloste tiedosto="esimerkit/03-keskikohta.odotettu"}
```

## Tarkistettu aritmetiikka

Ylivuoto havaitaan luotettavasti vain ennen laskua tai laskun aikana,
ei jälkikäteen. C23:n otsake `<stdckdint.h>` tarjoaa makrot
`ckd_add`, `ckd_sub` ja `ckd_mul`. Ne laskevat tuloksen, tallentavat
sen kohdemuuttujaan modulo $2^n$ ja palauttavat `true`, jos tarkka tulos
ei mahtunut. GCC:ssä ja Clangissa samat ovat saatavilla myös
vanhemmissa standardeissa nimillä `__builtin_add_overflow` ja niin
edelleen. Ne kääntyvät yhdeksi käskyksi ja lipputarkistukseksi.

```{.c tiedosto="esimerkit/03-tarkistettu.c" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/03-tarkistettu.odotettu"}
```

Tarkistettu aritmetiikka kuuluu kohtiin, joissa syöte tulee
ulkopuolelta: tiedoston koko kertaa alkion koko ennen `malloc`-kutsua,
käyttäjän antama määrä kertaa hinta, verkosta luettu pituus plus
otsakkeen pituus. Muistinvarauksen koon ylivuoto on yleinen
haavoittuvuuksien lähde: liian pieni puskuri varataan, ja kirjoitus
ylittää sen.

Kolmas vaihtoehto kiertymisen ja virheen rinnalle on *kyllästyvä*
aritmetiikka: liian suuri tulos korvataan tyypin suurimmalla ja liian
pieni pienimmällä arvolla. Äänessä ja kuvissa se on oikea valinta,
koska leikkautunut huippu on pienempi virhe kuin kiertynyt.
`ckd_add`-makrolla kyllästyminen on yksi ehtolause, ja NumPyssä sama
tehdään laskemalla leveämmässä tyypissä ja rajaamalla tulos
(`np.clip`, luvut 8 ja 10). Signaalinkäsittelyn kyllästyvä aritmetiikka
käsitellään taidossa *Lukujen esitys ja kiinteän pilkun aritmetiikka*.

## Python ja NumPy

Pythonin `int` ei vuoda yli. Kun kiinteän leveyden käyttäytyminen
halutaan, esimerkiksi tarkistussummassa tai toisen järjestelmän
emuloinnissa, tulos rajataan itse:

```{.python tiedosto="esimerkit/03-kierto.py" osa="emulointi"}
```

NumPyn taulukot ovat kiinteän levyisiä, ja ne kiertävät *ilman
varoitusta*. Tämä on yleinen virhe data-analyysissa: `int32`-sarakkeen
summa tai `uint8`-kuvan kirkastus kiertää hiljaa. Kertymälle annetaan
leveämpi tyyppi `dtype`-parametrilla:

```{.python tiedosto="esimerkit/03-kierto.py" osa="numpy"}
```

```{.tuloste tiedosto="esimerkit/03-kierto.odotettu"}
```

## Käytännössä

- **Rahat kokonaislukuina, 64 bittiä.** Sentteinä `int64_t` riittää
  92 233 biljoonaan euroon. 32-bittinen `int` ei riitä edes
  keskikokoisen yrityksen vuosimyyntiin.
- **Tarkista ulkoa tulevat laskut.** `ckd_mul` ennen muistinvarausta ja
  ennen kuin summa tallennetaan. Virhe palautetaan kutsujalle eikä
  tulosta jatketa väärällä arvolla.
- **Älä tarkista ylivuotoa jälkikäteen.** `if (a + b < a)` toimii vain
  etumerkittömille tyypeille. Etumerkillisillä kääntäjä saa poistaa
  ehdon. Käytä `ckd_add`-makroa tai vertaa rajaan ennen laskua
  (`a > INT_MAX - b`).
- **Kiertyminen tarkoituksella vain etumerkittömillä tyypeillä.**
  Järjestysnumerot, aikaleimat ja tiivistefunktiot kirjoitetaan
  etumerkittömillä tyypeillä, ja vertailu tehdään erotuksella.
- **Sanitoijat testeihin.** `-fsanitize=undefined` löytää ylivuodot,
  joita testi ei muuten huomaa. Hinta on testiajossa noin kaksinkertainen
  suoritusaika, tuotantokoodiin ei tule mitään.
- **NumPyssä kertymälle leveämpi tyyppi.** `sum(dtype=np.int64)` tai
  `astype` ennen laskua. NumPy varoittaa ylivuodosta vain
  skalaarilaskuissa, ei taulukoissa.

## Itsearviointi

- Osaat selittää, miksi etumerkillinen ylivuoto on C:ssä
  määrittelemätöntä ja miten se voi poistaa tarkistuksen koodista.
- Osaat kirjoittaa tarkistetun summan ja tulon `ckd_add`- ja
  `ckd_mul`-makroilla.
- Osaat vertailla kiertyviä järjestysnumeroita ja aikaleimoja oikein.
- Osaat löytää ja korjata hiljaisen ylivuodon NumPy-laskennasta.
- Osaat valita kiertyvän, tarkistetun ja kyllästyvän aritmetiikan
  välillä käyttötarkoituksen mukaan.
